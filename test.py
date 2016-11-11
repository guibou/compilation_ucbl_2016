import sys
import os.path

from antlr4 import CommonTokenStream, FileStream
from customprog import CustomProg, State

sys.path.insert(0, "../MIF08_TP4/StudFilesTP4")
from MuLexer import MuLexer
from MuParser import MuParser
from MyMuCodeGenVisitor import MyMuCodeGenVisitor


def run(inputname):
    input_s = FileStream(inputname)
    lexer = MuLexer(input_s)
    stream = CommonTokenStream(lexer)
    parser = MuParser(stream)
    tree = parser.prog()

    (hd, rest) = os.path.splitext(inputname)
    output_name = hd + ".asm"

    print("Code will be generated in file "+output_name)

    # Codegen Visitor, first argument is debug mode
    visitor3 = MyMuCodeGenVisitor(True, output_name, parser)

    # mock the visitor
    prog = CustomProg()
    visitor3._prog = prog
    # parser is there to provide basic PP for expressions.

    visitor3.visit(tree)

    instrs = prog._listIns

    for instr in instrs:
        print(instr)
    print('-' * 10)

    state = State(instrs)
    state.run()

    print(state.registers)

if __name__ == '__main__':
    run("../MIF08_TP4/StudFilesTP4/ex/expr.mu")
