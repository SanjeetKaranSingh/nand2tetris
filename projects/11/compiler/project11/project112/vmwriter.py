class VmWriter():
    def __init__(self, output_file):
        self.output = open(output_file, "w")
    
    def write(self, data):
        self.output.write(f"{data}\n")
    
    def writePush(self, segment, index):
        self.write(f"push {segment} {index}")

    def writePop(self, segment, index):
        self.write(f"pop {segment} {index}")

    def writeArithmetic(self, command):
        if command == "*":
            self.writeCall("Math.multiply", 2)
            return
        if command == "/":
            self.writeCall("Math.divide", 2)
            return

        if command == "+":
            command = "add"
        if command == "-":
            command = "sub"
        if command == "=":
            command = "eq"
        if command == ">":
            command = "gt"
        if command == "<":
            command = "lt"
        if command == "~":
            command = "not"
        if command == "&":
            command = "and"
        if command == "|":
            command = "or"
        
        self.write(f"{command}")
    
    def writeLabel(self, labelname):
        self.write(f"label {labelname}")

    def writeGoto(self, label):
        self.write(f"goto {label}")

    def writeIf(self, label):
        self.write(f"if-goto {label}")

    def writeCall(self, funcname, nargs):
        self.write(f"call {funcname} {nargs}")

    def writeFunction(self, funcname, nVars):
        self.write(f"function {funcname} {nVars}")

    def writeReturn(self):
        self.write(f"return")
    
    def close(self):
        self.output.close()
