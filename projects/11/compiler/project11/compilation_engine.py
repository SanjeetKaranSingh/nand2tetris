import sys
import re
import os
from xml.sax.saxutils import escape
import symbol_table
from symbol_table import symbolTable
from vmwriter import VmWriter
import tokenizer
import random, string

class CompilerEngineException(Exception):
    def __init__(self, msg):
        super().__init__(f"CompilerEngine Error {msg}")

def get_random():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

class compilationEngine():
    def __init__(self, output, tokensIterater):
        self.vmwriter = VmWriter(output)
        self.output = open(os.devnull, "w")
        self.tokensIterater = tokensIterater
        self.nexttoken = None
        self.ident = 0
        self.class_sym_table = None
        self.subroutine_sym_table = None

    def symbol_tbl_lookup(self, name) -> symbol_table.symbolData:
        try:
            return self.subroutine_sym_table.get(name)
        except Exception:
            try:
                return self.class_sym_table.get(name)
            except:
                return None

    def write(self):
        token = next(self.tokensIterater)
        self.compileClass(token)


    def writeTokenWithType(self, token):
        self.output.write(f'{" " * self.ident}<{token.type}> {escape(token.value)} </{token.type}>\n')
        if token.type == "identifier":
            try:
                val = self.symbol_tbl_lookup(token.value)
                defined = True
                self.output.write(f'{" " * self.ident}<{token.type}> index: {val.index}, kind: {val.kind}, type: {val.type} </{token.type}>\n')
            except:
                self.output.write(f'{" " * self.ident}<{token.type}> not defined </{token.type}>\n')

 
    def compileClass(self, token):
        if token.value != "class":
            return False

        self.class_sym_table = symbolTable()
        self.subroutine_sym_table = symbolTable()

        if class_name_token := next(self.tokensIterater):
            self.class_name = class_name_token.value
        else:
            raise CompilerEngineException("Missing class name")

        if class_name_token := next(self.tokensIterater):
            pass
        else:
            raise CompilerEngineException("Missing Curly bracket")

        while token := next(self.tokensIterater):
            if self.compileClassVarDec(token) or self.compileSubroutine(token):
                continue
            if token.value == "}":
                self.writeTokenWithType(token)
                break

            raise CompilerEngineException(f"unsupported token {token} inside class")


    def compileClassVarDec(self, token):
        if token.value == "static":
            kind = symbol_table.STATIC_SYMBOL
        elif token.value == "field":
            kind = symbol_table.FIELD_SYMBOL
        else:
            return False

        self.compileDecHelper(kind, self.class_sym_table)
        return True

    def compileDecHelper(self, kind, symbol_table, end=";"):
        if token := next(self.tokensIterater):
            mtype = token.value
        else:
            raise CompilerEngineException("Missing type specifier")

        while True:
            if token := next(self.tokensIterater):
                symbol_table.define(token.value, mtype, kind)
            else:
                raise CompilerEngineException("Missing variable name")

            if token := next(self.tokensIterater): # , or ;
                if token.value == end:
                    break
                elif token.value == ",":
                    continue
                raise CompilerEngineException("Invalid token during variable decleration")


    def compileSubroutine(self, token):
        if token.value != "constructor" and token.value != "function" and token.value != "method":
            return False
        
        self.subroutine_sym_table.reset()

        if token.value == "method":
            self.subroutine_sym_table.define("this", self.class_name, symbol_table.ARG_SYMBOL)

        function_type = token.value

        if token := next(self.tokensIterater):
            pass
        else:
            raise CompilerEngineException("Missing function return type")

        if token := next(self.tokensIterater):
            function_name = self.class_name + "." + token.value
        else:
            raise CompilerEngineException("Missing function name")

        token = next(self.tokensIterater)
        if token and token.value == "(":
            pass
        else:
            raise CompilerEngineException("Missing ( after function name")

        token = next(self.tokensIterater)
        
        if token is None:
            raise CompilerEngineException(") not exist")
        

        token = self.compileParameterList(token,self.subroutine_sym_table)
        if token.value != ")":
            raise CompilerEngineException(") not exist")

        self.writeTokenWithType(token)

        token = next(self.tokensIterater)

        if token is None or not self.compileSubroutineBody(token, function_name, function_type):
            raise CompilerEngineException("Missing subroutine body")

        self.ident -= 2
        self.output.write(f'{" " * self.ident}</subroutineDec>\n')
        return True


    def compileParameterList(self, token, sybl_table: symbol_table.symbolTable):
        mtype = None
        miden = None
        while True:
            if token.value == ")":
                return token

            if token.value == ",":
                miden = None
                mtype = None
            elif not mtype:
                mtype = token.value
            elif not miden:
                miden = token.value
                sybl_table.define(miden, mtype, symbol_table.ARG_SYMBOL)

            if token := next(self.tokensIterater):
                continue

            raise CompilerEngineException("Invalid function parameter")


    def compileSubroutineBody(self, token, func_name, func_type):
        if token.value != "{":
            return False

        while token := next(self.tokensIterater):
            if not self.compileVarDec(token):
                break

        local_vars = self.subroutine_sym_table.varCount("local")
        self.vmwriter.writeFunction(func_name, local_vars)

        if func_type == "constructor":
            this_vars = self.class_sym_table.varCount("this")
            self.vmwriter.writePush("constant", this_vars)
            self.vmwriter.writeCall("Memory.alloc", 1)
            self.vmwriter.writePop("pointer", 0)
        if func_type == "method":
            self.vmwriter.writePush("argument", 0)
            self.vmwriter.writePop("pointer", 0)

        token = self.compileStatements(token)

        if token.value != "}":
            raise CompilerEngineException("Missing closing subroutine")

        self.writeTokenWithType(token)
        self.ident -= 2
        self.output.write(f'{" " * self.ident}</subroutineBody>\n')
        return True


    def compileVarDec(self, token):
        if token.value != "var":
            return False

        self.compileDecHelper("local", self.subroutine_sym_table)
        return True

    def next_token(self):
        if self.nexttoken:
            token = self.nexttoken
            self.nexttoken = None
            return token
        
        return next(self.tokensIterater)

    def compileStatements(self, token):
        self.output.write(f'{" " * self.ident}<statements>\n')
        self.ident += 2
        while True:
            print(f"handling {token.value}")
            if token.value == "}":
                break
            elif self.compileLet(token):
                pass
            elif self.compileIf(token):
                pass
            elif self.compileWhile(token):
                pass
            elif self.compileDo(token):
                pass
            elif self.compileReturn(token):
                pass
            else:
                raise CompilerEngineException("Invalid statement type")
            token = self.next_token()

        self.ident -=2
        self.output.write(f"{' ' * self.ident}</statements>\n")
        return token


    def compileLet(self, token):
        if token.value != "let":
            return False

        array_exp = False
        var_name = ""
        while True:
            token=self.next_token()
            if token.value == "=" or token.value == "[":
                break
            var_name += token.value

        symbol = self.symbol_tbl_lookup(var_name)
        if not symbol:
            raise Exception(f"invalid symbol {var_name}")

        if token.value == "[":
            token = self.next_token()
            print(token.value)
            token = self.compileExpression(token)
            print(token.value)
            if token.value != "]":
                raise Exception(f"let statement array missing ]")
            
            self.vmwriter.writePush(symbol.kind, symbol.index)
            self.vmwriter.writeArithmetic("add")
            self.vmwriter.writePop("temp", 7)

            array_exp = True
            token = self.next_token()

            if token.value != "=":
                raise Exception("missing = in let array")

        token = self.next_token()

        self.compileExpression(token)


        if array_exp:
            self.vmwriter.writePush("temp", 7)
            self.vmwriter.writePop("pointer", 1)
            self.vmwriter.writePop("that", 0)
        else:
            self.vmwriter.writePop(symbol.kind, symbol.index)
        return True


    def compileIf(self, token):
        if token.value != "if":
            return False

        label1 = "label1_" + get_random()
        label2 = "label2_" + get_random()
        
        token = next(self.tokensIterater)

        if token and token.value == "(":
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("compiler if failed, missing (")
        
        if token := next(self.tokensIterater):
            token = self.compileExpression(token)
        else:
            raise CompilerEngineException("compiler if failed, missing expression")

        self.vmwriter.writeArithmetic("not")

        if token.value != ")":
            raise CompilerEngineException("compiler if failed, missing )")
        
        self.vmwriter.writeIf(label1)
        # if-goto L1

        token = next(self.tokensIterater)
        if token.value != "{":
            raise CompilerEngineException("compiler if failed, missing {")
        
        self.writeTokenWithType(token)

        token = next(self.tokensIterater)
        token = self.compileStatements(token)
        if token.value != "}":
            raise CompilerEngineException("compiler if failed, missing }")
        
        self.writeTokenWithType(token)

        token = next(self.tokensIterater)

        self.nexttoken = token

        self.vmwriter.writeGoto(label2)
        self.vmwriter.writeLabel(label1)
        # label L1

        if token and token.value == "else":
            self.nexttoken = None

            self.writeTokenWithType(token)

            token = next(self.tokensIterater)
            if token.value != "{":
                raise CompilerEngineException("compiler else failed, missing {")

            self.writeTokenWithType(token)

            token = next(self.tokensIterater)
            token = self.compileStatements(token)
            if token.value != "}":
                raise CompilerEngineException("compiler if failed, missing }")
            
            self.writeTokenWithType(token)

        self.vmwriter.writeLabel(label2)
        return True


    def compileWhile(self, token):
        if token.value != "while":
            return False

        label1 = "label1_" + get_random()
        label2 = "label2_" + get_random()

        self.vmwriter.writeLabel(label1)

        token = next(self.tokensIterater)
        if token and token.value == "(":
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("compiler while failed, missing (")
        
        if token := next(self.tokensIterater):
            token = self.compileExpression(token)
        else:
            raise CompilerEngineException("compiler while failed, missing expression")

        self.vmwriter.writeArithmetic("not")

        if token.value != ")":
            raise CompilerEngineException("compiler while failed, missing )")

        self.vmwriter.writeIf(label2)

        token = next(self.tokensIterater)
        if token.value != "{":
            raise CompilerEngineException("compiler while failed, missing {")

        token = next(self.tokensIterater)
        token = self.compileStatements(token)
        if token.value != "}":
            raise CompilerEngineException("compiler while failed, missing }")
        
        self.vmwriter.writeGoto(label1)
        self.vmwriter.writeLabel(label2)
        return True


    def compileDo(self, token):
        if token.value != "do":
            return False

        token = next(self.tokensIterater)
        token = self.compileTerm(token, addheader=False)
        if token.value != ";":
            raise Exception("Missing ; do statement")
        self.vmwriter.writePop("temp", 0)
        return True


    def compileReturn(self, token):
        if token.value != "return":
            return False
        
        if token := next(self.tokensIterater):
            if token.value == ';':
                self.vmwriter.writePush("constant", 0)
            else:
                token = self.compileExpression(token)
                if token.value != ';':
                    raise CompilerEngineException("compiler do failed missing ;")
                self.writeTokenWithType(token)
        else: 
            raise CompilerEngineException("compiler do failed missing function name")

        self.vmwriter.writeReturn()
        return True

    def compileExpression(self, token):
        expected_op = False
        self.output.write(f"{' ' * self.ident}<expression>\n")
        self.ident += 2
        cached_op = None
        while True:
            print(token.value)
            if expected_op:
                if token.value not in [ "+", "-", "*", "/", "&", "|", "<", ">", "=" ]:
                    break
                cached_op = token.value
                token = next(self.tokensIterater)
            else:
                token = self.compileTerm(token)
                if cached_op:
                    self.vmwriter.writeArithmetic(cached_op)

            expected_op = not expected_op

            if not token:
                raise CompilerEngineException("Missing term in expression")

        return token

    def compileTerm(self, token, addheader=True):
        if addheader:
            self.output.write(f"{' ' * self.ident}<term>\n")
            self.ident += 2
        expat_char = False            
        print(token.value)
        if (token.value in ('~', '-')):
            op = token.value
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
            token = self.compileTerm(token, addheader)
            if op == '~':
                self.vmwriter.writeArithmetic("not")
            else:
                self.vmwriter.writeArithmetic("neg")
            return token

        if token.value == "(":
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
            token = self.compileExpression(token)
            if token.value != ")":
                raise CompilerEngineException(f"term: missing ) at end of expression. val is {token.value}")
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
        else:
            identifier_name = ""
            symbol = None
            symbol1 = None
            while True:
                if token.type == tokenizer.STRING_CONST:
                    string_len = len(token.value)
                    self.vmwriter.writePush("constant", string_len)
                    self.vmwriter.writeCall("String.new", 1)
                    for char in token.value:
                        self.vmwriter.writePush("constant", ord(char))
                        self.vmwriter.writeCall("String.appendChar", 2)
                if token.value == "true":
                    self.vmwriter.writePush("constant", 0)
                    self.vmwriter.writeArithmetic("not")
                elif token.value == "false" or token.value == "null":
                    self.vmwriter.writePush("constant", 0)
                elif token.value == "this":
                    self.vmwriter.writePush("pointer", 0)
                elif token.type == tokenizer.INT_CONST:
                    self.vmwriter.writePush("constant", token.value)
                elif token.type == tokenizer.IDENTIFIER:
                    if sym_data := self.symbol_tbl_lookup(token.value):
                        symbol = sym_data
                        symbol1 = sym_data
                    else:
                        identifier_name += token.value

                token = next(self.tokensIterater)
        
                if token.value == ".":
                    if symbol:
                        identifier_name = symbol.type + "."
                        symbol = None
                    else:
                        identifier_name += "."
                    expat_char = True
                    continue
                elif symbol:
                    self.vmwriter.writePush(symbol.kind, symbol.index)
                    symbol = None

                if token.value == "[":
                    self.writeTokenWithType(token)
                    token = next(self.tokensIterater)
                    token = self.compileExpression(token)
                    self.vmwriter.writeArithmetic("add")
                    self.vmwriter.writePop("pointer", 1)
                    self.vmwriter.writePush("that", 0)
                    expat_char = False
                    if token.value != "]":
                        raise CompilerEngineException("term: missing ] at end of expression")
                elif token.value == "(":
                    self.writeTokenWithType(token)
                    token = next(self.tokensIterater)
                    method_in_method = False
                    if "." not in identifier_name:
                        # method of same class
                        identifier_name = self.class_name +"." + identifier_name
                        self.vmwriter.writePush("pointer", 0)
                        method_in_method = True
                    if symbol1:
                        self.vmwriter.writePush(symbol1.kind, symbol1.index)
                    token, nargs = self.compileExpressionList(token)
                    if symbol1 or method_in_method:
                        nargs += 1
                    expat_char = False
                    self.vmwriter.writeCall(identifier_name, nargs)
                    self.identifier_name = ""
                    if token.value != ")":
                        raise CompilerEngineException(f"term: missing ) at end of expression. val is {token.value}")
                elif not expat_char:
                    break
            
        return token


    def compileExpressionList(self, token):
        self.output.write(f"{' ' * self.ident}<expressionList>\n")
        self.ident += 2
        nargs = 0

        while True:
            if token.value == ")":
                break
            nargs += 1
            token = self.compileExpression(token)

            if token.value == ",":
                self.writeTokenWithType(token)
                token = next(self.tokensIterater)
            else:
                break
        
        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</expressionList>\n")
        return token, nargs
    

