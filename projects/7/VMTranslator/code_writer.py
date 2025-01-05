import parser
import string
import random
import os

output_file = None

def id_generator(size=6, chars=string.ascii_uppercase + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def select_lbl(lbl: str):
    return f'@{lbl}\n'

def dec_lbl(lbl: str):
    return f'({lbl})\n'

def select_top_stack():
    assem = (
        "@SP\n"
        "A=M-1\n"
    )
    return assem

def pop_stack_to_D():
    assem = (
        "@SP\n"
        "M=M-1\n"
        "A=M\n"
        "D=M\n"
    )
    return assem

def push_D_to_stack():
    assem = (
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )
    return assem

def set_top_stack(operation: str):
    assem = (
        f'{select_top_stack()}'
        f'M={operation}\n'
    )
    return assem


def unary_assem(operation: str):
    return set_top_stack(operation)

def binary_assem(operation: str):
    return pop_stack_to_D() + unary_assem(operation)

def goto(lbl: str, variable: str='0', oper:str='JMP'):
    return (
        f"{select_lbl(lbl)}"
        f"{variable};{oper}\n"
    )


def assign(dest, value):
    return f'{dest}={value}\n'

def select_symbol(symbol: str):
    return f'@{symbol}\n'

def assign_symbol(dest: str, symbol: str):
    return (
        f"{select_symbol(symbol)}"
        f"{dest}=A\n"
    )

def assign_symbol_val(dest: str, symbol: str):
    return (
        f"@{symbol}\n"
        f"{dest}=M\n"
    )

def compare_assembly(oper: str):
    id = id_generator(10)
    lbl = f"{oper}_{id}_lbl"
    end_lbl = f'{lbl}_end'

    assem = (
        pop_stack_to_D() +
        select_top_stack() +
        assign("D", "M-D") +

        goto(lbl, "D", oper) +

        set_top_stack("0") +
        goto(end_lbl) +

        dec_lbl(lbl) +
        set_top_stack("-1") +
        dec_lbl(end_lbl)
    )
    return assem


def push_constant(i: str):
    return assign_symbol("D", i) + push_D_to_stack()


def push_from_D_base(i: str):
    return (
        select_symbol(i) +
        assign("A", "D+A") + 
        assign("D", "M") +
        push_D_to_stack()
    )

def pop_to_D_base(i: str):
    return (
        select_symbol(i) +
        assign("D", "D+A") +
        select_symbol("R13") +
        assign("M", "D") +
        pop_stack_to_D() +
        select_symbol("R13") +
        assign("A", "M") +
        assign("M", "D"))


def push_from_base_pointer(seg_base: str, i: str):
    return ( assign_symbol_val("D", seg_base) + 
              push_from_D_base(i)
            )

def pop_to_base_pointer(seg_base: str, i: str):
    return (
        assign_symbol_val("D", seg_base) + 
        pop_to_D_base(i)
    )

def push_from_base(seg_base: str, i: str):
    return ( assign_symbol("D", seg_base) + 
              push_from_D_base(i)
            )

def pop_to_base(seg_base: str, i: str):
    return (
        assign_symbol("D", seg_base) + 
        pop_to_D_base(i)
    )

def push_static(classname: str, i: str):
    return (
        assign_symbol_val("D", f"{classname}.{i}") +
        push_D_to_stack()
    )

def assign_to_symbol(symbol, value):
    return (select_symbol(symbol) + f"M={value}\n")

def pop_static(classname: str, i: str):
    assem = (
        pop_stack_to_D() +
        assign_to_symbol(f"{classname}.{i}", "D")
    )
    return assem

def push_val_to_stack(sym):
    return ( 
            assign_symbol_val("D", sym) +
            push_D_to_stack() 
        )

def push_symbol_addr_to_stack(sym):
    return ( 
            assign_symbol("D", sym) +
            push_D_to_stack() 
        )


def end_loop():
    return dec_lbl("final_end") + goto("final_end")

ArithmeticTable = {
    "add": lambda: binary_assem("D+M"),
    "sub": lambda: binary_assem("M-D"),
    "neg": lambda: unary_assem("-M"),
    "eq": lambda: compare_assembly("JEQ"),
    "gt": lambda: compare_assembly("JGT"),
    "lt": lambda: compare_assembly("JLT"),
    "and": lambda: binary_assem("D&M"),
    "or": lambda: binary_assem("D|M"),
    "not": lambda: unary_assem("!M")
}

PushTable = {
    "local": lambda index: push_from_base_pointer("LCL", index),
    "argument": lambda index: push_from_base_pointer("ARG", index),
    "this": lambda index: push_from_base_pointer("THIS", index),
    "that": lambda index: push_from_base_pointer("THAT", index),
    "constant": lambda value: push_constant(value),
    "static": lambda outfile, index: push_static(outfile, index),
    "pointer": lambda index: push_from_base("3", index),
    "temp": lambda index: push_from_base("5", index)
}

PopTable = {
    "local": lambda index: pop_to_base_pointer("LCL", index),
    "argument": lambda index: pop_to_base_pointer("ARG", index),
    "this": lambda index: pop_to_base_pointer("THIS", index),
    "that": lambda index: pop_to_base_pointer("THAT", index),
    "static": lambda outfile, index: pop_static(outfile, index),
    "pointer": lambda index: pop_to_base("3", index),
    "temp": lambda index: pop_to_base("5", index)
}


function_call_counters = {}

class CodeWriter:
    def __init__(self, out_stream) -> None:
        self.out_file = out_stream
        self.fp = open(self.out_file, "w")
    
    def write_arithematic(self, command: str):
        assembly_func = ArithmeticTable.get(command)
        if assembly_func is None:
            raise Exception("Invalid value")
        assembly = assembly_func()
        self.fp.write(assembly)
    
    def WritePushPop(self, command, segment, index, infile=None):
        assem = ""
        index = str(index)
        if command == parser.C_PUSH:
            if pushfn := PushTable.get(segment):
                if segment == "static":
                    if infile:
                        classname = os.path.basename(infile).split('.')[0]
                        assem = pushfn(classname, index)
                    else:
                        raise Exception("Missing infile with static")
                else:
                    assem = pushfn(index)
            else:
                raise Exception("invalid value")
        elif command == parser.C_POP:
            if popfn := PopTable.get(segment):
                if segment == "static":
                    if infile:
                        classname = os.path.basename(infile).split('.')[0]
                        assem = popfn(classname, index)
                    else:
                        raise Exception("Missing infile with static")
                else:
                    assem = popfn(index)
            else:
                raise Exception("invalid value")
        self.fp.write(assem)
    
    def WriteLabel(self, label):
        assam = dec_lbl(label)
        self.fp.write(assam)

    def WriteEndloop(self):
        assam = end_loop()
        self.fp.write(assam)

    def WriteGotoIf(self, label):
        assam = pop_stack_to_D()
        assam += goto(lbl=label, variable="D", oper="JNE")
        self.fp.write(assam)

    def WriteGoto(self, label):
        assam = goto(label)
        self.fp.write(assam)
    
    def WriteFunction(self, function, nlocals):
        self.fp.write("//write function sanjeet " + function + "\n")
        nlocals = int(nlocals)
        self.fp.write(dec_lbl(function))
        # initialize local variables
        for _ in range(0, nlocals):
            self.WritePushPop(parser.C_PUSH, "constant", "0")


    def WriteCall(self, function, nargs):
        self.fp.write("//write call sanjeet " + function + "\n")
        if function_call_counters.get(function):
            function_call_counters[function] += 1
        else:
            function_call_counters[function] = 1
        
        # Assign ARG register
        assem = select_symbol("SP")
        assem += assign("D", "M")
        assem += select_symbol(nargs)
        assem += assign("D", "D-A")
        assem += assign_to_symbol("R13", "D")

        return_label = f'call_{function}.{function_call_counters[function]}'
        assem += push_symbol_addr_to_stack(return_label)
        assem += push_val_to_stack("LCL")
        assem += push_val_to_stack("ARG")
        assem += push_val_to_stack("THIS")
        assem += push_val_to_stack("THAT")

        assem += select_symbol("R13")
        assem += assign("D", "M")
        assem += assign_to_symbol("ARG", "D")
        
        assem += select_lbl("SP")
        assem += assign("D", "M")
        assem += assign_to_symbol("LCL", "D")

        assem += goto(function)

        assem += dec_lbl(return_label)
        self.fp.write(assem)


    def WriteReturn(self):
        # Store endframe 
        self.fp.write("//write return sanjeet " + "\n")
        assem = assign_symbol_val("D", "LCL")
        assem += assign_to_symbol("R14", "D")

        assem += select_symbol("5")
        assem += assign("D", "A")
        assem += select_symbol("R14")
        assem += assign("A", "M-D")
        assem += assign("D", "M")
        assem += assign_to_symbol("R15", "D")

        self.fp.write(assem)

        self.WritePushPop(parser.C_POP, "argument", "0")

        assem = select_lbl("ARG")
        assem += assign("D", "M+1")
        assem += assign_to_symbol("SP", "D")

        assem += select_symbol("1")
        assem += assign("D", "A")
        assem += select_symbol("R14")
        assem += assign("A", "M-D")
        assem += assign("D", "M")
        assem += assign_to_symbol("THAT", "D")

        assem += select_symbol("2")
        assem += assign("D", "A")
        assem += select_symbol("R14")
        assem += assign("A", "M-D")
        assem += assign("D", "M")
        assem += assign_to_symbol("THIS", "D")

        assem += select_symbol("3")
        assem += assign("D", "A")
        assem += select_symbol("R14")
        assem += assign("A", "M-D")
        assem += assign("D", "M")
        assem += assign_to_symbol("ARG", "D")

        assem += select_symbol("4")
        assem += assign("D", "A")
        assem += select_symbol("R14")
        assem += assign("A", "M-D")
        assem += assign("D", "M")
        assem += assign_to_symbol("LCL", "D")

        assem += assign_symbol_val("D", "R15")
        assem += assign("A", "D")
        assem += "0;JMP\n"

        self.fp.write(assem)

    def WriteBootStrap(self):
        self.fp.write("@256\n"
                      "D=A\n"
                      "@SP\n"
                      "M=D\n")
        self.WriteCall("Sys.init", "0")
        self.WriteEndloop()