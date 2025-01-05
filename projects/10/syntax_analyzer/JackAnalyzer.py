#!/usr/bin/env python3
import tokenizer
from compilation_engine import compilationEngine
import sys
import os
import glob
from xml.sax.saxutils import escape

def main():
    args = sys.argv
    if len(args) < 2:
        print("Error missing input")
        return 1

    input_file = args[1]
    if os.path.isdir(input_file):
        dir = os.path.realpath(input_file)
        files = glob.glob(f'{dir}/*jack')
    else:
        files = [input_file]
    
    for file in files:
        output_file = file.split('.')[0] + ".xml"
        print(file)
        token_gen = tokenizer.iter_each_instruction(file)
        engine = compilationEngine(output_file, token_gen)
        engine.write()


main()