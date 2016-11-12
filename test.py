import sys
import os.path
import cStringIO

from antlr4 import CommonTokenStream, InputStream
from customprog import CustomProg, State, InfiniteLoopException

sys.path.insert(0, "../MIF08_TP4/StudFilesTP4")
from MuLexer import MuLexer
from MuParser import MuParser
from MyMuCodeGenVisitor import MyMuCodeGenVisitor


def run(inputname, debug=False):
    input_s = InputStream(inputname)
    lexer = MuLexer(input_s)
    stream = CommonTokenStream(lexer)
    parser = MuParser(stream)
    tree = parser.prog()

    (hd, rest) = os.path.splitext(inputname)
    output_name = hd + ".asm"

    # Codegen Visitor, first argument is debug mode
    visitor3 = MyMuCodeGenVisitor(debug, output_name, parser)

    # mock the visitor
    prog = CustomProg()
    visitor3._prog = prog
    # parser is there to provide basic PP for expressions.

    if not debug:
        backstdout = sys.stdout
        sys.stdout = cStringIO.StringIO()

    visitor3.visit(tree)

    if not debug:
        sys.stdout = backstdout

    instrs = prog._listIns

    state = State(instrs)

    return state


def runfile(filename):
    state = run(open(filename).read(), True)

    for instr in state.instrs:
        print(instr)

    state.run()

    print(state.registers)

if __name__ == '__main__':
    pass
    # runfile("../MIF08_TP4/StudFilesTP4/ex/expr.mu")
    # run(open("../MIF08_TP4/StudFilesTP4/ex/expr.mu").read())

import unittest

maxValue = 15

class TestCase(unittest.TestCase):
    def _testIn(self, code, *needed):
        state = run(code)

        # print('-' * 100)
        # for instr in state.instrs:
        #   print(instr)

        state.run()

        for i in needed:
            self.assertIn(i, state.registers.values())

    # Atoms
    def test_constant(self):
        for i in range(maxValue):
            self._testIn('''a = %d;''' % i, i)

    # +
    def test_add(self):
        for i in range(maxValue):
            for j in range(maxValue):
                self._testIn('''a = %d + %d;''' % (i, j), i + j)

    # -
    def test_sub(self):
        for i in range(maxValue):
            for j in range(maxValue):
                self._testIn('''a = %d - %d;''' % (i, j), i - j)

    # (unary -)
    def test_unaryminus(self):
        for i in range(maxValue):
                self._testIn('''a = - %d;''' % i, -i)

    def test_not(self):
        for i in range(maxValue):
            self._testIn('''a = !%d;''' % i, ~i)

    def test_complex_expr(self):
        self._testIn('''x = 1515;''', 1515)
        self._testIn('''x = 5 + 3 - 10;''', -2)
        self._testIn('''x = -3 + 10;''', 7)

    def test_sub_expr(self):
        self._testIn('''x = 5 - (3 - 10);''', 12)
        self._testIn('''x = (-3 - 2) + 10;''', 5)

    def test_affectation(self):
        for i in range(100):
            self._testIn('''a = %d; b = a + 100;''' % i, 100 + i)
            self._testIn('''a = %d; b = a + 100; c = !b;
            d = c - 2;''' % i, ~(i + 100) - 2)

    def _test_simple_if(self, op, strop):
        for i in range(0, 15):
            for j in range(0, 15):
                expectedValue = 10 + (100 if op(i, j) else 50)
                self._testIn('''
                b = 50;
                if(%d %s %d)
                {
                        b = 100;
                }
                b = b + 10;
                ''' % (i, strop, j), expectedValue)

    def test_if_lt(self):
        self._test_simple_if(lambda x, y: x < y, "<")

    def test_if_gt(self):
        self._test_simple_if(lambda x, y: x > y, ">")

    def test_if_leq(self):
        self._test_simple_if(lambda x, y: x <= y, "<=")

    def test_if_geq(self):
        self._test_simple_if(lambda x, y: x >= y, ">=")

    def test_if_eq(self):
        self._test_simple_if(lambda x, y: x == y, "==")

    def test_if_neq(self):
        self._test_simple_if(lambda x, y: x != y, "!=")

    def _test_simple_while(self, op, strop):
        for i in range(0, 15):
            for j in range(0, 15):
                infiniteLoop = op(i, j)

                code = '''
                while(%d %s %d)
                {
                }
                res = 10 + 5;
                ''' % (i, strop, j)

                if infiniteLoop:
                    with self.assertRaises(InfiniteLoopException):
                        run(code).run()
                else:
                    self._testIn(code, 15)

    def test_while_lt(self):
        self._test_simple_while(lambda x, y: x < y, "<")

    def test_while_gt(self):
        self._test_simple_while(lambda x, y: x > y, ">")

    def test_while_leq(self):
        self._test_simple_while(lambda x, y: x <= y, "<=")

    def test_while_geq(self):
        self._test_simple_while(lambda x, y: x >= y, ">=")

    def test_while_eq(self):
        self._test_simple_while(lambda x, y: x == y, "==")

    def test_while_neq(self):
        self._test_simple_while(lambda x, y: x != y, "!=")

    def test_and_binary(self):
        for i in range(16):
            for j in range(16):
                self._testIn('''x = %d && %d;''' % (i, j), i & j)

    def test_or_binary(self):
        for i in range(16):
            for j in range(16):
                self._testIn('''x = %d || %d;''' % (i, j), i | j)

    def test_bonus_mul(self):
        for i in range(16):
            for j in range(16):
                self._testIn('''x = %d * %d;''' % (i, j), i * j)

    def test_bonus_div(self):
        for i in range(16):
            for j in range(1, 16):
                self._testIn('''x = %d / %d;''' % (i, j), i // j)

    def test_bonus_mod(self):
        for i in range(16):
            for j in range(1, 16):
                self._testIn('''x = %d %% %d;''' % (i, j), i % j)

    def test_bonus_pow(self):
        for i in range(5):
            for j in range(5):
                self._testIn('''x = %d ^ %d;''' % (i, j), i ** j)

'''
TODOs:

- meilleurs debug quand cela plante
- planter Des que l'API est mal appelee
'''
