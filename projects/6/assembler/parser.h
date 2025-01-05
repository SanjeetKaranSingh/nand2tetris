#ifndef PARSER_H
#define PARSER_H

#include <iostream>
#include <fstream>

using namespace std;

enum instructionType 
{   
    instructionTypeA,
    instructionTypeC,
    instructionTypeL,
    instructionTypeInvalid
};

class Parser
{
private:
    ifstream asm_file;
    bool isEmptyOrWhitespacesOrComment(string line);
public:
string currentInstruction;
    Parser(char* filepath);
    bool hasMoreLines();
    string advance();
    void reset();
    instructionType getInstructionType();
    string symbol();
    string dest();
    string comp();
    string jump();
    ~Parser();
};

#endif