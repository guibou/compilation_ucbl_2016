from __future__ import print_function

import unittest
import random
import os
import itertools

from test_utils import run, InfiniteLoopError

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
    def _testRun(self, code, *needed):
        state = run(code)

        state.run()

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

    def _test_run_affectation_op(self, op):
        self._testRun('''a = 1 %s 2;''' % op)

    def test_run_affectation_add(self):
        self._test_run_affectation_op("+")

    def test_run_affectation_sub(self):
        self._test_run_affectation_op("-")

    def test_run_affectation_div(self):
        self._test_run_affectation_op("/")

    def test_run_affectation_mul(self):
        self._test_run_affectation_op("*")

    def test_run_affectation_mod(self):
        self._test_run_affectation_op("%")

    def test_run_affectation_and_binary(self):
        self._test_run_affectation_op("&&")

    def test_run_affectation_or_binary(self):
        self._test_run_affectation_op("||")

    def _test_run_affectation_binop_bool(self, op):
        self._testRun('''a = true %s false;''' % op)

    def test_run_affectation_and_bool(self):
        self._test_run_affectation_binop_bool("&&")

    def test_run_affectation_or_bool(self):
        self._test_run_affectation_binop_bool("||")

    def test_run_affectation_lt(self):
        self._test_run_affectation_op("<")

    def test_run_affectation_gt(self):
        self._test_run_affectation_op(">")

    def test_run_affectation_lte(self):
        self._test_run_affectation_op("<=")

    def test_run_affectation_gte(self):
        self._test_run_affectation_op(">=")

    def test_run_affectation_eq(self):
        self._test_run_affectation_op("==")

    def test_run_affectation_neq(self):
        self._test_run_affectation_op("!=")

    def test_run_affectation_not_binary(self):
        self._testRun('''a = !5;''')

    def test_run_affectation_not_boolean(self):
        self._testRun('''a = !true;''')

    # simple if
    def _test_simple_if(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            expectedValue = 5 + (10 if op(i, j) else 12)
            self._testIn('''
            b = 12;
            if(%d %s %d)
            {
                    b = 10;
            }
            b = b + 5;
            ''' % (i, strop, j), expectedValue)

    def _test_simple_if_var(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            # test with a variable
            expectedValue = 5 + (10 if op(i, j) else 12)
            self._testIn('''
            b = 12;
            op = %d %s %d;
            c = false;
            if(op)
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

    def test_if_lt_var(self):
        self._test_simple_if(lambda x, y: x < y, "<")

    def test_if_gt_var(self):
        self._test_simple_if(lambda x, y: x > y, ">")

    def test_if_leq_var(self):
        self._test_simple_if(lambda x, y: x <= y, "<=")

    def test_if_geq_var(self):
        self._test_simple_if(lambda x, y: x >= y, ">=")

    def test_if_eq_var(self):
        self._test_simple_if(lambda x, y: x == y, "==")

    def test_if_neq_var(self):
        self._test_simple_if(lambda x, y: x != y, "!=")

    def test_if_bool(self):
        self._testIn('''
        if(false)
        {
            x = 10;
        }
        else
        {
            x = 5;
        }

        x = x + 7;
        ''', 12)

        self._testIn('''
        if(true)
        {
            x = 10;
        }
        else
        {
            x = 5;
        }

        x = x + 7;
        ''', 17)

    def test_while_bool(self):
        code = '''
        while(true)
        {
        }'''

        with self.assertRaises(InfiniteLoopError):
            run(code).run()

        self._testRun('''
        while(false)
        {
        }
        ''')

    # if with else
    def _test_simple_if_else(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            expectedValue = 5 + (10 if op(i, j) else 12)
            self._testIn('''
            if(%d %s %d)
            {
                    b = 10;
            }
            else
            {
                    b = 12;
            }
            b = b + 5;
            ''' % (i, strop, j), expectedValue)

    def _test_simple_if_else_var(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            expectedValue = 5 + (10 if op(i, j) else 12)
            self._testIn('''
            v = %d %s %d;
            if(v)
            {
                    b = 10;
            }
            else
            {
                    b = 12;
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

    def test_if_else_lt_var(self):
        self._test_simple_if_else(lambda x, y: x < y, "<")

    def test_if_else_gt_var(self):
        self._test_simple_if_else(lambda x, y: x > y, ">")

    def test_if_else_leq_var(self):
        self._test_simple_if_else(lambda x, y: x <= y, "<=")

    def test_if_else_geq_var(self):
        self._test_simple_if_else(lambda x, y: x >= y, ">=")

    def test_if_else_eq_var(self):
        self._test_simple_if_else(lambda x, y: x == y, "==")

    def test_if_else_neq_var(self):
        self._test_simple_if_else(lambda x, y: x != y, "!=")

    # if chain without else
    def _test_simple_if_chain(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 12
            elif op(j, k):
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
                    b = 12;
            }}
            else if({j} {op} {k})
            {{
                    b = 15;
            }}
            b = b + 5;
            '''.format(i=i, op=strop, j=j, k=k), expectedValue)

    def _test_simple_if_chain(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 12
            elif op(j, k):
                b = 15
            b = b + 5

            expectedValue = b
            self._testIn('''
            b = 5;

            var1 = {i} {op} {j};
            var2 = {i} {op} {k};
            var3 = {j} {op} {k};
            if(var1)
            {{
                    b = 10;
            }}
            else if(var2)
            {{
                    b = 12;
            }}
            else if(var3)
            {{
                    b = 15;
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

    def test_if_chain_lt_var(self):
        self._test_simple_if_chain(lambda x, y: x < y, "<")

    def test_if_chain_gt_var(self):
        self._test_simple_if_chain(lambda x, y: x > y, ">")

    def test_if_chain_leq_var(self):
        self._test_simple_if_chain(lambda x, y: x <= y, "<=")

    def test_if_chain_geq_var(self):
        self._test_simple_if_chain(lambda x, y: x >= y, ">=")

    def test_if_chain_eq_var(self):
        self._test_simple_if_chain(lambda x, y: x == y, "==")

    def test_if_chain_neq_var(self):
        self._test_simple_if_chain(lambda x, y: x != y, "!=")

    # if chain with else
    def _test_simple_if_chain_else(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 12
            elif op(j, k):
                b = 8
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
                    b = 12;
            }}
            else if({j} {op} {k})
            {{
                    b = 8;
            }}
            else
            {{
                    b = 15;
            }}
            b = b + 5;
            '''.format(i=i, op=strop, j=j, k=k), expectedValue)

    def _test_simple_if_chain_else_var(self, op, strop):
        for i, j, k in rangeGroup([(0, 8), (4, 10), (6, 12)]):
            b = 5
            if op(i, j):
                b = 10
            elif op(i, k):
                b = 12
            elif op(j, k):
                b = 8
            else:
                b = 15
            b = b + 5

            expectedValue = b
            self._testIn('''
            b = 5;
            var1 = {i} {op} {j};
            var2 = {i} {op} {k};
            var3 = {j} {op} {k};
            if(var1)
            {{
                    b = 10;
            }}
            else if(var2)
            {{
                    b = 12;
            }}
            else if(var3)
            {{
                    b = 8;
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

    def test_if_chain_else_lt_var(self):
        self._test_simple_if_chain_else(lambda x, y: x < y, "<")

    def test_if_chain_else_gt_var(self):
        self._test_simple_if_chain_else(lambda x, y: x > y, ">")

    def test_if_chain_else_leq_var(self):
        self._test_simple_if_chain_else(lambda x, y: x <= y, "<=")

    def test_if_chain_else_geq_var(self):
        self._test_simple_if_chain_else(lambda x, y: x >= y, ">=")

    def test_if_chain_else_eq_var(self):
        self._test_simple_if_chain_else(lambda x, y: x == y, "==")

    def test_if_chain_else_neq_var(self):
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
                with self.assertRaises(InfiniteLoopError):
                    run(code).run()
            else:
                self._testIn(code, 15)

    def _test_simple_while_var(self, op, strop):
        for i, j in rangeGroup([(0, maxValue), (0, maxValue)]):
            infiniteLoop = op(i, j)

            code = '''
            var = %d %s %d;
            while(var)
            {
            }
            res = 10 + 5;
            ''' % (i, strop, j)

            if infiniteLoop:
                with self.assertRaises(InfiniteLoopError):
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

    def test_while_lt_var(self):
        self._test_simple_while(lambda x, y: x < y, "<")

    def test_while_gt_var(self):
        self._test_simple_while(lambda x, y: x > y, ">")

    def test_while_leq_var(self):
        self._test_simple_while(lambda x, y: x <= y, "<=")

    def test_while_geq_var(self):
        self._test_simple_while(lambda x, y: x >= y, ">=")

    def test_while_eq_var(self):
        self._test_simple_while(lambda x, y: x == y, "==")

    def test_while_neq_var(self):
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

    def test_non_mutable_not_binary(self):
        self._testIn('''
        a = 5;
        c = !a;
        d = a + 14;
        ''', 19)

    def test_non_mutable_not_boolean(self):
        self._testIn('''
        a = true;
        c = !a;
        if(a)
        {
           d = 12;
        }
        ''', 12)

    def _test_non_mutable_op(self, op):
        self._testIn('''
        a = 5;
        b = 3;
        c = a %s b;
        d = a + 14;
        ''' % op, 19)

        self._testIn('''
        a = 5;
        b = 3;
        c = a %s b;
        d = b + 14;
        ''' % op, 17)

    def test_non_mutable_add(self):
        self._test_non_mutable_op("+")

    def test_non_mutable_sub(self):
        self._test_non_mutable_op("-")

    def test_non_mutable_div(self):
        self._test_non_mutable_op("/")

    def test_non_mutable_mul(self):
        self._test_non_mutable_op("*")

    def test_non_mutable_mod(self):
        self._test_non_mutable_op("%")

    def test_non_mutable_and_binary(self):
        self._test_non_mutable_op("&&")

    def test_non_mutable_or_binary(self):
        self._test_non_mutable_op("||")

    def test_non_mutable_lt(self):
        self._test_non_mutable_op("<")

    def test_non_mutable_gt(self):
        self._test_non_mutable_op(">")

    def test_non_mutable_lte(self):
        self._test_non_mutable_op("<=")

    def test_non_mutable_gte(self):
        self._test_non_mutable_op(">=")

    def test_non_mutable_eq(self):
        self._test_non_mutable_op("==")

    def test_non_mutable_neq(self):
        self._test_non_mutable_op("!=")

    def test_complex_program_multiplication(self):
        code = '''
        a  = 5;
        b = 8;

        acc = 0;

        while(b > 0)
        {
            acc = acc + a;
            b = b - 1;
        }
        '''

        self._testIn(code, 40)

    def test_complex_program_factorial(self):
        code = '''
        n = 7;
        accum = 1;
        while(n >= 2)
        {
            # multiplication
            a  = n;
            b = accum;

            acc = 0;

            test = 0 < b;
            while(test)
            {
                acc = acc + a;
                b = b + (-1);
            }

            accum = acc;
            n = n - 1;
        }
        '''

        self._testIn(code, 5040)

if __name__ == '__main__':
    import csv

    result = unittest.main(exit=False).result

    errTests = {}
    for item in (result.failures + result.errors):
        errTests[item[0].id().split('.')[-1]] = 'Exception: Not Yet Implemented' in item[1]

    tests = []
    for test in dir(TestCase):
        if test.startswith("test_"):
            tests.append(test)

    tests.sort()

    with open('result.csv', 'w') as f:
        writer = csv.writer(f)

        for test in tests:
            label = ''
            if test in errTests:
                if errTests[test]:
                    label = "Not Implemented"
                else:
                    label = "Bug"
            else:
                label = "Ok"

            writer.writerow([test, label])
