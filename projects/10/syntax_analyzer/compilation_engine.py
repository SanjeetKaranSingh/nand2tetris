import sys
from xml.sax.saxutils import escape

class CompilerEngineException(Exception):
    def __init__(self, msg):
        super().__init__(f"CompilerEngine Error {msg}")

class compilationEngine():
    def __init__(self, output, tokensIterater):
        self.output = open(output, "w")
        self.tokensIterater = tokensIterater
        self.nexttoken = None
        self.ident = 0

    def write(self):
        token = next(self.tokensIterater)
        self.compileClass(token)

    def writeTokenWithType(self, token):
        self.output.write(f'{" " * self.ident}<{token.type}> {escape(token.value)} </{token.type}>\n')

    def compileClass(self, token):
        if token.value != "class":
            return False
        
        self.output.write("<class>\n")
        self.ident += 2
        self.writeTokenWithType(token)

        if class_name_token := next(self.tokensIterater):
            self.writeTokenWithType(class_name_token)
        else:
            raise CompilerEngineException("Missing class name")
        
        if class_name_token := next(self.tokensIterater):
            self.writeTokenWithType(class_name_token)
        else:
            raise CompilerEngineException("Missing Curly bracket")

        while token := next(self.tokensIterater):
            if self.compileClassVarDec(token) or self.compileSubroutine(token):
                continue
            if token.value == "}":
                self.writeTokenWithType(token)
                break

            raise CompilerEngineException(f"unsupported token {token} inside class")
        self.ident -= 2
        self.output.write("</class>\n")


    def compileClassVarDec(self, token):
        if token.value != "static" and token.value != "field":
            return False

        self.output.write(f'{" " * self.ident}<classVarDec>\n')
        self.ident += 2
        self.writeTokenWithType(token)
        self.compileDecHelper()
        self.ident -=2
        self.output.write(f'{" " * self.ident}</classVarDec>\n')
        return True

    def compileDecHelper(self, end=";"):
        if token := next(self.tokensIterater):
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("Missing type specifier")

        while True:
            if token := next(self.tokensIterater):
                self.writeTokenWithType(token)
            else:
                raise CompilerEngineException("Missing variable name")

            if token := next(self.tokensIterater): # , or ;
                if token.value == end:
                    self.writeTokenWithType(token)
                    break
                elif token.value == ",":
                    self.writeTokenWithType(token)
                    continue
                raise CompilerEngineException("Invalid token during variable decleration")


    def compileSubroutine(self, token):
        if token.value != "constructor" and token.value != "function" and token.value != "method":
            return False
        
        self.output.write(f'{" " * self.ident}<subroutineDec>\n')
        self.ident += 2

        self.writeTokenWithType(token)

        if token := next(self.tokensIterater):
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("Missing function treturn type")

        if token := next(self.tokensIterater):
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("Missing function name")

        token = next(self.tokensIterater)
        if token and token.value == "(":
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("Missing ( after function name")

        token = next(self.tokensIterater)
        
        if token is None:
            raise CompilerEngineException(") not exist")
        

        token = self.compileParameterList(token)
        if token.value != ")":
            raise CompilerEngineException(") not exist")

        self.writeTokenWithType(token)

        token = next(self.tokensIterater)

        if token is None or not self.compileSubroutineBody(token):
            raise CompilerEngineException("Missing subroutine body")

        self.ident -= 2
        self.output.write(f'{" " * self.ident}</subroutineDec>\n')
        return True


    def compileParameterList(self, token):
        self.output.write(f'{" " * self.ident}<parameterList>\n')
        self.ident += 2
        while True:
            if token.value == ")":
                self.ident -= 2
                self.output.write(f'{" " * self.ident}</parameterList>\n')
                return token

            self.writeTokenWithType(token)

            if token := next(self.tokensIterater):
                continue

            raise CompilerEngineException("Invalid function parameter")


    def compileSubroutineBody(self, token):
        if token.value != "{":
            return False

        self.output.write(f'{" " * self.ident}<subroutineBody>\n')
        self.ident += 2
        self.writeTokenWithType(token)

        while token := next(self.tokensIterater):
            if not self.compileVarDec(token):
                break
        
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
        
        self.output.write(f'{" " * self.ident}<varDec>\n')
        self.ident += 2
        self.writeTokenWithType(token)
        self.compileDecHelper()
        self.ident -= 2
        self.output.write(f'{" " * self.ident}</varDec>\n')
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
        
        self.output.write(f"{' ' * self.ident}<letStatement>\n")
        self.ident += 2
        exp_expression = False
        self.writeTokenWithType(token)

        while True:
            if token.value == ";":
                break
            elif token.value == "[" or token.value == "=":
                exp_expression = True

            if token := next(self.tokensIterater):
                if exp_expression:
                    token = self.compileExpression(token)
                    self.writeTokenWithType(token)
                    exp_expression = False
                else:
                    self.writeTokenWithType(token)
            else:
                raise CompilerEngineException("compiler let failed missing variable name")
        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</letStatement>\n")
        return True


    def compileIf(self, token):
        if token.value != "if":
            return False

        self.output.write(f"{' ' * self.ident}<ifStatement>\n")
        self.ident += 2

        self.writeTokenWithType(token)
        
        token = next(self.tokensIterater)
        if token and token.value == "(":
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("compiler if failed, missing (")
        
        if token := next(self.tokensIterater):
            token = self.compileExpression(token)
        else:
            raise CompilerEngineException("compiler if failed, missing expression")

        if token.value != ")":
            raise CompilerEngineException("compiler if failed, missing )")
        
        self.writeTokenWithType(token)

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

        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</ifStatement>\n")
        return True


    def compileWhile(self, token):
        if token.value != "while":
            return False

        self.output.write(f"{' ' * self.ident}<whileStatement>\n")
        self.ident += 2
        self.writeTokenWithType(token)
        
        token = next(self.tokensIterater)
        if token and token.value == "(":
            self.writeTokenWithType(token)
        else:
            raise CompilerEngineException("compiler while failed, missing (")
        
        if token := next(self.tokensIterater):
            token = self.compileExpression(token)
        else:
            raise CompilerEngineException("compiler while failed, missing expression")

        if token.value != ")":
            raise CompilerEngineException("compiler while failed, missing )")
        
        self.writeTokenWithType(token)

        token = next(self.tokensIterater)
        if token.value != "{":
            raise CompilerEngineException("compiler while failed, missing {")
        
        self.writeTokenWithType(token)

        token = next(self.tokensIterater)
        token = self.compileStatements(token)
        if token.value != "}":
            raise CompilerEngineException("compiler while failed, missing }")
        
        self.writeTokenWithType(token)
        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</whileStatement>\n")
        return True


    def compileDo(self, token):
        if token.value != "do":
            return False
        
        self.output.write(f"{' ' * self.ident}<doStatement>\n")
        self.ident += 2
        self.writeTokenWithType(token)

        token = next(self.tokensIterater)
        token = self.compileTerm(token, addheader=False)
        if token.value != ";":
            raise Exception("Missing ; do statement")
        self.writeTokenWithType(token)
        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</doStatement>\n")
        return True


    def compileReturn(self, token):
        if token.value != "return":
            return False
        
        self.output.write(f"{' ' * self.ident}<returnStatement>\n")
        self.ident += 2
        self.writeTokenWithType(token)

        if token := next(self.tokensIterater):
            if token.value == ';':
                self.writeTokenWithType(token)
            else:
                token = self.compileExpression(token)
                if token.value != ';':
                    raise CompilerEngineException("compiler do failed missing ;")
                self.writeTokenWithType(token)
        else: 
            raise CompilerEngineException("compiler do failed missing function name")

        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</returnStatement>\n")
        return True

    def compileExpression(self, token):
        expected_op = False
        self.output.write(f"{' ' * self.ident}<expression>\n")
        self.ident += 2
        while True:
            if expected_op:
                if token.value not in [ "+", "-", "*", "/", "&", "|", "<", ">", "=" ]:
                    break
                self.writeTokenWithType(token)
                token = next(self.tokensIterater)
            else:
                token = self.compileTerm(token)

            expected_op = not expected_op

            if not token:
                raise CompilerEngineException("Missing term in expression")

        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</expression>\n")
        return token

    def compileTerm(self, token, addheader=True):
        if addheader:
            self.output.write(f"{' ' * self.ident}<term>\n")
            self.ident += 2
        expat_char = False            

        if (token.value in ('~', '-')):
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
            token = self.compileTerm(token, addheader)
        elif token.value == "(":
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
            token = self.compileExpression(token)
            if token.value != ")":
                raise CompilerEngineException(f"term: missing ) at end of expression. val is {token.value}")
            self.writeTokenWithType(token)
            token = next(self.tokensIterater)
        else:
            while True:
                self.writeTokenWithType(token)

                token = next(self.tokensIterater)
                if token.value == ".":
                    expat_char = True
                    continue
                elif token.value == "[":
                    self.writeTokenWithType(token)
                    token = next(self.tokensIterater)
                    token = self.compileExpression(token)
                    expat_char = False
                    if token.value != "]":
                        raise CompilerEngineException("term: missing ] at end of expression")
                elif token.value == "(":
                    self.writeTokenWithType(token)
                    token = next(self.tokensIterater)
                    token = self.compileExpressionList(token)
                    expat_char = False
                    if token.value != ")":
                        raise CompilerEngineException(f"term: missing ) at end of expression. val is {token.value}")
                elif not expat_char:
                    break
            
        if addheader:
            self.ident -= 2
            self.output.write(f"{' ' * self.ident}</term>\n")
        return token

    def compileExpressionList(self, token):
        self.output.write(f"{' ' * self.ident}<expressionList>\n")
        self.ident += 2

        while True:
            if token.value == ")":
                break
            token = self.compileExpression(token)

            if token.value == ",":
                self.writeTokenWithType(token)
                token = next(self.tokensIterater)
            else:
                break
        
        self.ident -= 2
        self.output.write(f"{' ' * self.ident}</expressionList>\n")
        return token
    

