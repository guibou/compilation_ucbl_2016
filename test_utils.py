import sys
import os.path
import cStringIO

from antlr4 import CommonTokenStream, InputStream
from customprog import CustomProg, State, InfiniteLoopError

from MuLexer import MuLexer
from MuParser import MuParser
from MyMuCodeGenVisitor import MyMuCodeGenVisitor

import MyMuCodeGenVisitor as MyMuCodeGenVisitorModule

# monkey patch
MyMuCodeGenVisitorModule.LC3Prog = CustomProg


def run(inputname, debug=False):
    input_s = InputStream(inputname)
    lexer = MuLexer(input_s)
    stream = CommonTokenStream(lexer)
    parser = MuParser(stream)
    tree = parser.prog()

    (hd, rest) = os.path.splitext(inputname)
    output_name = hd + ".asm"

    # Codegen Visitor, first argument is debug mode
    visitor3 = MyMuCodeGenVisitor(True, output_name, parser)

    def nop(self):
        pass

    # another hack to remove some error due to unimplemented stuffs
    MyMuCodeGenVisitor.printRegisterMap = nop

    # mock the visitor
    prog = CustomProg()
    visitor3._prog = prog
    # parser is there to provide basic PP for expressions.

    backstdout = sys.stdout
    sys.stdout = cStringIO.StringIO()

    try:
        visitor3.visit(tree)
    finally:
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
    runfile(sys.argv[1])
