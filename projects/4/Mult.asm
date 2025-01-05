@R0
D=M
@number1
M=D
@R1
D=M
@number2
M=D
@R2
M=0

(LOOP)
    @number2
    D=M
    @END
    D=D-1;JLT
    @number2
    M=D

    @number1
    D=M
    @R2
    M=D+M
    @LOOP
    0;JMP
(END)
    0;JMP
