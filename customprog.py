from __future__ import print_function


class UnexpectedBranchingLabelException(Exception):
    pass


class InvalidRegisterNameException(Exception):
    pass


class OverflowConstantException(Exception):
    pass


class CustomProg:
    def __init__(self):
        self._listIns = []
        self._nbtmp = 0
        self._nblabel = 0

    # all temps are prefixed by temp_
    def newtmp(self):
        self._nbtmp = self._nbtmp+1
        return 'temp_'+str(self._nbtmp)

    def newlabelWhile(self):
        self._nblabel = self._nblabel+1
        return ("l_while_begin_"+str(self._nblabel),
                "l_while_end_"+str(self._nblabel))

    def newlabelCond(self):
        self._nblabel = self._nblabel+1
        return ("l_cond_neg_"+str(self._nblabel),
                "l_cond_end_"+str(self._nblabel))

    def addLabel(self, s):
        self._listIns.append(Label(s))

    def addInstructionBR(self, s, label):
        s2 = frozenset(s)
        if s2 not in [frozenset(), frozenset("nzp"), frozenset("nz"), frozenset("zp"),
                      frozenset("n"), frozenset("p"), frozenset("np"), frozenset("z")]:
            raise UnexpectedBranchingLabelException()
        self._listIns.append(Br(s, label))

    def addInstructionGOTO(self, label):
        self._listIns.append(Br("", label))

    def addInstructionNOT(self, dr, sr1):
        self._assertIsRegister(dr)
        self._assertIsRegister(sr1)

        self._listIns.append(Not(dr, sr1))

    def addInstructionADD(self, dr, sr1, sr2orimm7):
        self._assertIsRegister(dr)
        self._assertIsRegister(sr1)
        self._assertIsRegisterOrInt(sr2orimm7)

        self._listIns.append(Add(dr, sr1, sr2orimm7))

    def addInstructionAND(self, dr, sr1, sr2orimm7):
        self._assertIsRegister(dr)
        self._assertIsRegister(sr1)
        self._assertIsRegisterOrInt(sr2orimm7)

        self._listIns.append(And(dr, sr1, sr2orimm7))

    def printCode(self, filename):
        pass

    def addComment(self, s):
        pass

    def _isRegister(self, reg):
        return (isinstance(reg, str) and
                reg.startswith("temp_") and reg[5:].isdigit())

    def _isRightSizedInt(self, i):
        return i >= 0 and i.bit_length() <= 5

    def _assertIsRegister(self, reg):
        if not self._isRegister(reg):
            raise InvalidRegisterNameException()

    def _assertIsRegisterOrInt(self, reg):
        int_value = None

        if isinstance(reg, int):
            int_value = reg
        elif reg.startswith("#") and reg[1:].isdigit():
            int_value = int(reg[1:])
        elif reg.isdigit():
            int_value = int(reg)

        if int_value is None:
            self._assertIsRegister(reg)
        else:
            if not self._isRightSizedInt(int_value):
                raise OverflowConstantException()


class Show:
    def __repr__(self):
        def formatdict(d):
            return ', '.join(("%s=%r" % (key, val))
                             for key, val in sorted(d.items()))

        return "{}({})".format(self.__class__.__name__,
                               formatdict(self.__dict__))

    def __str__(self):
        return repr(self)


class Comment(Show):
    def __init__(self, s):
        self.s = s

    def visit(self, state):
        pass


class Label(Show):
    def __init__(self, label):
        self.label = label

    def visit(self, state):
        pass


class And(Show):
    def __init__(self, dr, sr1, sr2orimm7):
        self.dr, self.sr1, self.sr2orimm7 = dr, sr1, sr2orimm7

    def visit(self, state):
        try:
            v0 = state.getRegister(self.sr1)
        except NotInitialisedRegisterException:
            v0 = None

        try:
            v1 = state.getRegisterOrInt(self.sr2orimm7)
        except NotInitialisedRegisterException:
            v1 = None

        if v0 is None or v1 is None:
            if v0 == 0 or v1 == 0:
                state.setRegister(self.dr, 0)
            else:
                raise NotInitialisedRegisterException()

        else:
            state.setRegister(self.dr, v0 & v1)


class Add(Show):
    def __init__(self, dr, sr1, sr2orimm7):
        self.dr, self.sr1, self.sr2orimm7 = dr, sr1, sr2orimm7

    def visit(self, state):
        state.setRegister(self.dr, state.getRegister(self.sr1) +
                          state.getRegisterOrInt(self.sr2orimm7))


class Not(Show):
    def __init__(self, dr, sr1):
        self.dr, self.sr1 = dr, sr1

    def visit(self, state):
        state.setRegister(self.dr, ~state.getRegister(self.sr1))


class Br(Show):
    def __init__(self, s, label):
        self.s = frozenset(s)
        self.label = label

    def visit(self, state):
        ops = {frozenset("n"): lambda x: x < 0,
               frozenset("nz"): lambda x: x <= 0,
               frozenset("z"): lambda x: x == 0,
               frozenset("zp"): lambda x: x >= 0,
               frozenset("p"): lambda x: x > 0,
               frozenset("np"): lambda x: x != 0}

        # do not read the last register if
        # the branch is unconditional
        if (self.s in {frozenset(), frozenset("nzp")} or
           ops[self.s](state.getLastRegister())):
            return state.getPcAtLabel(self.label)

        return None


class InfiniteLoopException(Exception):
    pass


class MissingLabelException(Exception):
    pass


class NotInitialisedRegisterException(Exception):
    pass


class State:
    def __init__(self, instrs, maxInstructions=1000):
        self.instrs = instrs
        self.maxInstructions = maxInstructions

        # find labels offsets
        self.labels = {}

        for idx, instr in enumerate(instrs):
            if isinstance(instr, Label):
                self.labels[instr.label] = idx

        # registers
        self.registers = {}

        self.lastRegister = None

    def getLastRegister(self):
        if self.lastRegister is not None:
            return self.lastRegister
        else:
            raise NotInitialisedRegisterException()

    def setRegister(self, r, value):
        self.registers[r] = value

        self.lastRegister = value

    def getRegister(self, r):
        if r not in self.registers:
            raise NotInitialisedRegisterException()

        return self.registers[r]

    def getRegisterOrInt(self, roi):
        if isinstance(roi, int):
            return roi
        # special case for int starting with '#'
        elif roi.startswith('#'):
            return int(roi[1:].strip())
        else:
            # special case for int passed as string
            try:
                i = int(roi)
                return i
            except ValueError:
                return self.getRegister(roi)

    def run(self):
        count = 0
        pc = 0
        while pc < len(self.instrs):
            instr = self.instrs[pc]
            overridePc = instr.visit(self)

            if overridePc is not None:
                pc = overridePc
            else:
                pc += 1

            count += 1

            if count > self.maxInstructions:
                raise InfiniteLoopException()

    def getPcAtLabel(self, label):
        try:
            return self.labels[label]
        except KeyError:
            raise MissingLabelException(label)

if __name__ == '__main__':
    import unittest

    r0 = "temp_0"
    r1 = "temp_1"
    r2 = "temp_2"
    r3 = "temp_3"
    r4 = "temp_4"
    r5 = "temp_5"
    r6 = "temp_6"
    r7 = "temp_7"
    rCrap = "temp_Crap"

    class Test(unittest.TestCase):
        def _test(self, instrs, registers):
            state = State(instrs)
            state.run()

            return self.assertEquals(state.registers, registers)

        def test_and_0(self):
            self._test([And(r0, r0, 0)], {r0: 0})

        def test_add_cste(self):
            self._test([And(r0, r0, 0),
                        Add(r0, r0, 5)],
                       {r0: 5})

        def test_and_cste(self):
            self._test([And(r0, r0, "#0"),
                        And(r0, r0, 0),
                        Add(r0, r0, 7),
                        And(r1, r0, 4),
                        And(r0, r0, "#3")],
                       {r0: 3, r1: 4})

        def test_add_cste_alt(self):
            self._test([And(r0, r0, 0),
                        Add(r0, r0, "#5")],
                       {r0: 5})

        def test_add_cste_alt_bis(self):
            self._test([And(r0, r0, 0),
                        Add(r0, r0, "5")],
                       {r0: 5})

        def test_add_registers(self):
            self._test([And(r0, r0, 0),
                        And(r1, r1, 0),
                        Add(r0, r1, 5),
                        Add(r1, r0, 2),
                        Add(r2, r0, r1)],
                       {r0: 5, r1: 7, r2: 12})

        def test_and_registers(self):
            self._test([And(r0, r0, 0),
                        And(r1, r1, 0),
                        Add(r0, r0, 3),
                        Add(r1, r1, 5),
                        And(r2, r0, r1)],
                       {r0: 3, r1: 5, r2: 1})

        def test_not(self):
            self._test([And(r0, r0, 0),
                        Add(r0, r0, 5),
                        Not(r0, r0),
                        Add(r1, r0, 1)],
                       {r0: -6, r1: -5})

        def _testLastRegister(self, res, instrs):
            state = State(instrs)
            state.run()
            self.assertEqual(state.getLastRegister(), res)

        # Tests of the last register
        def test_lr_and_0(self):
            self._testLastRegister(0, [And(r0, r0, 0)])

        def test_lr_add_constant(self):
            self._testLastRegister(12, [And(r0, r0, 0),
                                        Add(r0, r0, 12)])

        def test_lr_add_registers(self):
            self._testLastRegister(22, [And(r0, r0, 0),
                                        Add(r0, r0, 12),
                                        And(r1, r1, 0),
                                        Add(r1, r1, 10),
                                        Add(r2, r1, r0)])

        def test_lr_and_registers(self):
            self._testLastRegister(8, [And(r0, r0, 0),
                                       Add(r0, r0, 12),
                                       And(r1, r1, 0),
                                       Add(r1, r1, 10),
                                       And(r2, r1, r0)])

        def test_lr_and_constant(self):
            self._testLastRegister(8, [And(r0, r0, 0),
                                       Add(r0, r0, "12"),
                                       And(r0, r0, 10)])

        def test_lr_not(self):
            self._testLastRegister(-13, [And(r0, r0, 0),
                                         Add(r0, r0, 12),
                                         Not(r0, r0)])

        def test_branching(self):
            # tests for branching
            # last register is supposed to work, so well, branch

            for v in range(-10, 11):
                instrs = []

                for test in ["", "n", "nz", "z", "zp", "p", "np", "nzp"]:
                    instrs.extend(
                        [
                            And(r0, r0, 0),
                            Add(r0, r0, v),
                            Br(test, "l" + test),
                            And("r" + test, "r" + test, 0),
                            Label("l" + test)
                        ])

                state = State(instrs)
                state.run()

                for reg, f in [("", lambda x:True),
                               ("n", lambda x: x < 0),
                               ("nz", lambda x: x <= 0),
                               ("z", lambda x: x == 0),
                               ("zp", lambda x: x >= 0),
                               ("p", lambda x: x > 0),
                               ("np", lambda x: x != 0),
                               ("nzp", lambda x: True)]:
                    if f(v):
                        self.assertNotIn(("r" + reg),  state.registers)
                    else:
                        self.assertEqual(state.registers["r" + reg], 0)

        def test_infinite_loop(self):
            state = State([
                Label("start"), Br("", "start")])

            with self.assertRaises(InfiniteLoopException):
                state.run()

        def test_missing_label(self):
            state = State([Br("", "missing")])

            with self.assertRaises(MissingLabelException):
                state.run()

        def test_notinitialised_register_not(self):
            state = State([Not(r0, r0)])

            with self.assertRaises(NotInitialisedRegisterException):
                state.run()

        def test_notinitialised_register_and_first(self):
            state = State([And(r0, r0, 2)])

            with self.assertRaises(NotInitialisedRegisterException):
                state.run()

        def test_notinitialised_register_and_second(self):
            state = State([And(r0, r0, 0), Add(r0, r0, 10), And(r0, r0, r1)])

            with self.assertRaises(NotInitialisedRegisterException):
                state.run()

        def test_notinitialised_register_or_first(self):
            state = State([Add(r0, r0, 2)])

            with self.assertRaises(NotInitialisedRegisterException):
                state.run()

        def test_notinitialised_register_or_second(self):
            state = State([And(r0, r0, 0), Add(r0, r0, r1)])

            with self.assertRaises(NotInitialisedRegisterException):
                state.run()

    unittest.main()
