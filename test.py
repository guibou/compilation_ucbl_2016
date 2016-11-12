import unittest

from test_utils import run, InfiniteLoopException

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

    def test_not_binary(self):
        for i in range(maxValue):
            self._testIn('''a = !%d;''' % i, ~i)

    def test_complex_expr(self):
        self._testIn('''x = 5 + 3 - 10;''', -2)
        self._testIn('''x = -3 + 10;''', 7)

    def test_sub_expr(self):
        self._testIn('''x = 5 - (3 - 10);''', 12)
        self._testIn('''x = (-3 - 2) + 10;''', 5)

    def test_affectation(self):
        for i in range(15):
            self._testIn('''a = %d; b = a + 13;''' % i, 13 + i)
            self._testIn('''a = %d; b = a + 13; c = !b;
            d = c - 2;''' % i, ~(i + 13) - 2)

    # simple if
    def _test_simple_if(self, op, strop):
        for i in range(0, 15):
            for j in range(0, 15):
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
        for i in range(0, 15):
            for j in range(0, 15):
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

    def test_bonus_overflow(self):
        self._testIn('''x = 1515;''', 1515)
        self._testIn('''x = 3000;''', 3000)
'''
TODOs:

- If
- register imutability
'''
