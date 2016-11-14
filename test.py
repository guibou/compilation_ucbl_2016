import unittest
import random
import os
import itertools

from test_utils import run, InfiniteLoopException

maxValue = 15


def rangeGroup(args):
    def singletonToInt(t):
        if len(t) == 1:
            return t[0]
        else:
            return t

    return map(singletonToInt,
               itertools.product(*[range(*item) for item in args]))

if 'FAST' in os.environ:
    limit = int(os.environ['FAST'])

    _rangeGroup = rangeGroup

    def rangeGroup(*args):
        l = list(_rangeGroup(*args))

        return random.sample(l, limit)


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
        for i in rangeGroup([(0, maxValue)]):
            self._testIn('''a = %d;''' % i, i)

    # +
    def test_add(self):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            self._testIn('''a = %d + %d;''' % (i, j), i + j)

    # -
    def test_sub(self):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            self._testIn('''a = %d - %d;''' % (i, j), i - j)

    # (unary -)
    def test_unaryminus(self):
        for i in rangeGroup([(0, maxValue)]):
                self._testIn('''a = - %d;''' % i, -i)

    def test_not_binary(self):
        for i in rangeGroup([(0, maxValue)]):
            self._testIn('''a = !%d;''' % i, ~i)

    def test_complex_expr(self):
        self._testIn('''x = 5 + 3 - 10;''', -2)
        self._testIn('''x = -3 + 10;''', 7)

    def test_sub_expr(self):
        self._testIn('''x = 5 - (3 - 10);''', 12)
        self._testIn('''x = (-3 - 2) + 10;''', 5)

    def test_affectation(self):
        for i in rangeGroup([(0, maxValue)]):
            self._testIn('''a = %d; b = a + 13;''' % i, 13 + i)

    # simple if
    def _test_simple_if(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            expectedValue = 5 + (10 if op(i, j) else 20)
            self._testIn('''
            b = 20;
            if(%d %s %d)
            {
                    b = 10;
            }
            b = b + 5;
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

    # if with else
    def _test_simple_if_else(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            expectedValue = 5 + (10 if op(i, j) else 20)
            self._testIn('''
            if(%d %s %d)
            {
                    b = 10;
            }
            else
            {
                    b = 20;
            }
            b = b + 5;
            ''' % (i, strop, j), expectedValue)

    def test_if_else_lt(self):
        self._test_simple_if_else(lambda x, y: x < y, "<")

    def test_if_else_gt(self):
        self._test_simple_if_else(lambda x, y: x > y, ">")

    def test_if_else_leq(self):
        self._test_simple_if_else(lambda x, y: x <= y, "<=")

    def test_if_else_geq(self):
        self._test_simple_if_else(lambda x, y: x >= y, ">=")

    def test_if_else_eq(self):
        self._test_simple_if_else(lambda x, y: x == y, "==")

    def test_if_else_neq(self):
        self._test_simple_if_else(lambda x, y: x != y, "!=")

    # if chain without else
    def _test_simple_if_chain(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 20
            elif op(j, k):
                b = 25
            b = b + 5

            expectedValue = b
            self._testIn('''
            b = 5;
            if({i} {op} {j})
            {{
                    b = 10;
            }}
            else if({i} {op} {k})
            {{
                    b = 20;
            }}
            else if({j} {op} {k})
            {{
                    b = 25;
            }}
            b = b + 5;
            '''.format(i=i, op=strop, j=j, k=k), expectedValue)

    def test_if_chain_lt(self):
        self._test_simple_if_chain(lambda x, y: x < y, "<")

    def test_if_chain_gt(self):
        self._test_simple_if_chain(lambda x, y: x > y, ">")

    def test_if_chain_leq(self):
        self._test_simple_if_chain(lambda x, y: x <= y, "<=")

    def test_if_chain_geq(self):
        self._test_simple_if_chain(lambda x, y: x >= y, ">=")

    def test_if_chain_eq(self):
        self._test_simple_if_chain(lambda x, y: x == y, "==")

    def test_if_chain_neq(self):
        self._test_simple_if_chain(lambda x, y: x != y, "!=")

    # if chain with else
    def _test_simple_if_chain_else(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 20
            elif op(j, k):
                b = 25
            else:
                b = 15
            b = b + 5

            expectedValue = b
            self._testIn('''
            b = 5;
            if({i} {op} {j})
            {{
                    b = 10;
            }}
            else if({i} {op} {k})
            {{
                    b = 20;
            }}
            else if({j} {op} {k})
            {{
                    b = 25;
            }}
            else
            {{
                    b = 15;
            }}
            b = b + 5;
            '''.format(i=i, op=strop, j=j, k=k), expectedValue)

    def test_if_chain_else_lt(self):
        self._test_simple_if_chain_else(lambda x, y: x < y, "<")

    def test_if_chain_else_gt(self):
        self._test_simple_if_chain_else(lambda x, y: x > y, ">")

    def test_if_chain_else_leq(self):
        self._test_simple_if_chain_else(lambda x, y: x <= y, "<=")

    def test_if_chain_else_geq(self):
        self._test_simple_if_chain_else(lambda x, y: x >= y, ">=")

    def test_if_chain_else_eq(self):
        self._test_simple_if_chain_else(lambda x, y: x == y, "==")

    def test_if_chain_else_neq(self):
        self._test_simple_if_chain_else(lambda x, y: x != y, "!=")

    def _test_simple_while(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
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
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            self._testIn('''x = %d && %d;''' % (i, j), i & j)

    def test_or_binary(self):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            self._testIn('''x = %d || %d;''' % (i, j), i | j)

    def test_bonus_mul(self):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            self._testIn('''x = %d * %d;''' % (i, j), i * j)

    def test_bonus_div(self):
        for i, j in rangeGroup([(0, maxValue), (1, maxValue)]):
            self._testIn('''x = %d / %d;''' % (i, j), i // j)

    def test_bonus_mod(self):
        for i, j in rangeGroup([(0, maxValue), (1, maxValue)]):
            self._testIn('''x = %d %% %d;''' % (i, j), i % j)

    def test_bonus_pow(self):
        for i, j in rangeGroup([(1, 5), (0, 5)]):
            self._testIn('''x = %d ^ %d;''' % (i, j), i ** j)

    def test_bonus_overflow(self):
        self._testIn('''x = 1515;''', 1515)
        self._testIn('''x = 3000;''', 3000)

    # test the boolean version of not / and / or
    def test_not_boolean(self):
        for a in ["true", "false"]:
            self._testIn('''
            a = %s;
            b = 3;
            if(!a)
            {
                b = 5;
            }

            c = b + 3;
            ''' % a, 6 if a == "true" else 8)

    def test_and_boolean(self):
        for a in ["true", "false"]:
            for b in ["true", "false"]:
                self._testIn('''
                a = %s;
                c = %s;
                b = 3;
                if(a && c)
                {
                    b = 5;
                }
                c = b + 3;
                ''' % (a, b), 8 if (a == "true" and b == "true") else 6)

    def test_or_boolean(self):
        for a in ["true", "false"]:
            for b in ["true", "false"]:
                self._testIn('''
                a = %s;
                c = %s;
                b = 3;
                if(a || c)
                {
                    b = 5;
                }
                c = b + 3;
                ''' % (a, b), 8 if (a == "true" or b == "true") else 6)
'''
TODOs:

- If
- register imutability
'''
