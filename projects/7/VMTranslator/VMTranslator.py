#!/usr/bin/env python3
import glob
import sys
import parser
import os
from parser import Parser
from code_writer import CodeWriter

def main():
    args = sys.argv
    if len(args) < 2:
        print("Error missing input")
        return 1
    
    input_file = args[1]

    if os.path.isdir(input_file):
        output_file = os.path.basename(os.path.realpath(input_file)) + ".asm"
        output_file = f'{input_file}/{output_file}'
        files = glob.glob(f'{input_file}/*vm')
        m_codeWriter = CodeWriter(output_file)
        m_codeWriter.WriteBootStrap()
    else:
        output_file = input_file.split('.')[0] + ".asm"
        m_codeWriter = CodeWriter(output_file)
        files = [input_file]
    
    for file in files:
        m_parser = Parser(file)

        for instruction in m_parser.iter_each_instruction():
            if (instruction.type == parser.C_PUSH or 
                instruction.type == parser.C_POP):
                m_codeWriter.WritePushPop(instruction.type, instruction.arg1, instruction.arg2, file)
            elif (instruction.type == parser.C_ARITHMETIC):
                m_codeWriter.write_arithematic(instruction.arg1)
            elif (instruction.type == parser.C_GOTO):
                m_codeWriter.WriteGoto(instruction.arg1)
            elif (instruction.type == parser.C_IF):
                m_codeWriter.WriteGotoIf(instruction.arg1)
            elif (instruction.type == parser.C_LABEL):
                m_codeWriter.WriteLabel(instruction.arg1)
            elif (instruction.type == parser.C_CALL):
                m_codeWriter.WriteCall(instruction.arg1, instruction.arg2)
            elif (instruction.type == parser.C_FUNCTION):
                m_codeWriter.WriteFunction(instruction.arg1, instruction.arg2)
            elif (instruction.type == parser.C_RETURN):
                m_codeWriter.WriteReturn()


main()