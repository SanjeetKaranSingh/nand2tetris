from dataclasses import dataclass

# definations for artimatic
C_ARITHMETIC = 1
C_PUSH = 2
C_POP = 3
C_LABEL = 4
C_GOTO = 5
C_IF = 6
C_FUNCTION = 7
C_RETURN = 8
C_CALL = 9

@dataclass
class Instruction:
    type: int
    arg1: str
    arg2: str

class Parser:
    def __init__(self, file) -> None:
        self.file = file

    def command_type(self, instruction):
        current_in = instruction.split()
        if current_in[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return C_ARITHMETIC
        if current_in[0] == "push":
            return C_PUSH
        if current_in[0] == "pop":
            return C_POP
        if current_in[0] == "label":
            return C_LABEL
        if current_in[0] == "if-goto":
            return C_IF
        if current_in[0] == "goto":
            return C_GOTO
        if current_in[0] == "call":
            return C_CALL
        if current_in[0] == "function":
            return C_FUNCTION
        if current_in[0] == "return":
            return C_RETURN


    def iter_each_instruction(self):
        with open(self.file, "r") as fp:
            for line in fp:
                icurrent = line.strip()
                print(icurrent)
                if icurrent == "" or icurrent.startswith("//"):
                    continue

                itype = self.command_type(icurrent)
                i_arg1 = self.arg1(itype, icurrent)
                i_arg2 = self.arg2(itype, icurrent)
                print(f'arg1={i_arg1}')
                print(f'arg2={i_arg2}')
                yield Instruction(itype, i_arg1, i_arg2)

    def arg1(self, itype, instruction):
        current_split = instruction.split()

        if itype == C_RETURN:
            return None

        if itype == C_ARITHMETIC:
            return current_split[0]
        
        return current_split[1]

    def arg2(self, itype, instruction):
        current_split = instruction.split()
        if itype in (C_POP, C_PUSH, C_FUNCTION, C_CALL):
            return current_split[2]
        else:
            return None
