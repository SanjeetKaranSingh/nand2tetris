#include <iostream>
#include <fstream>
#include <regex.h>

#include "parser.h"

using namespace std;

bool Parser::isEmptyOrWhitespacesOrComment(string line) {
    if (line.empty()){
        return true;
    }
    
    bool first_match = false;
    for (char chr: line) {
        if (first_match && chr == '/'){
            return true;
        }

        first_match = false;
        if (chr == '/') {
            first_match = true; 
            continue;
        }

        if (!isspace(chr)) {
            break;
        }
    }


    bool onlyspaces = true;
    for (char ch: line) {
        if (!isspace(ch)) {
            onlyspaces = false;
            break;
        }
    }

    return onlyspaces;
}

Parser::Parser(char* filepath)
{
    asm_file.open(filepath);
}

Parser::~Parser() {
    asm_file.close();
}

bool Parser::hasMoreLines() {
    return asm_file.peek() != EOF;
}

void Parser::reset() {
    
    asm_file.clear();
    asm_file.seekg(0, asm_file.beg);
}

std::string trim(const std::string& str,
                 const std::string& whitespace = " \t")
{
    const auto strBegin = str.find_first_not_of(whitespace);
    if (strBegin == std::string::npos)
        return ""; // no content

    const auto strEnd = str.find_last_not_of(whitespace);
    const auto strRange = strEnd - strBegin + 1;

    return str.substr(strBegin, strRange);
}

string Parser::advance() {
    string line;
    while (getline(asm_file, line)) {
        if (isEmptyOrWhitespacesOrComment(line)){
            cout << "Ignorning: " + line + "\n";
            continue;
        }
        break;
    }
    currentInstruction = line;
    currentInstruction = trim(currentInstruction);
    currentInstruction.erase(currentInstruction.length() - 1, 1);
    return line;
}

instructionType Parser::getInstructionType() {
    switch (currentInstruction[0])
    {
        case '@':
            return instructionTypeA;
        case '(':
            return instructionTypeL;            
    }
    return instructionTypeC;
}

string Parser::symbol() {
    instructionType type = getInstructionType();
    string symbol;
    if (type == instructionTypeA) {
        symbol = currentInstruction;
        symbol.erase(0, 1);
    }
    else if (type == instructionTypeL)
    {
        symbol = currentInstruction.substr(1, currentInstruction.length() - 2);
    }
    return symbol;
}

string Parser::dest(){
    int i, j=0;
    string dest;
    int len = currentInstruction.length();
    char* cont = new char[len];

    for(i=0; i < currentInstruction.length(); i++) {
        if (currentInstruction[i] == ' ') {
            continue;
        }
        if (currentInstruction[i] == '=') {
            cont[j] = '\0';
            dest.assign(cont);
            break;
        }
        cont[j] = currentInstruction[i];
        j++;
    }
    free(cont);
    return dest;
}

string Parser::comp(){
    int i, j=0;
    string comp;
    int len = currentInstruction.length();
    char* cont = new char[len];
    cont[0] = 0;
    char* act = cont;
    int dest_len;
    bool assigned = false;

    for(i=0; i < currentInstruction.length(); i++) {
        if (currentInstruction[i] == ' ') {
            continue;
        }
        if (currentInstruction[i] == '=') {
            act += j + 1;
        }
        if (currentInstruction[i] == ';') {
            cont[j] = 0;
            comp.assign(act);
            assigned = true;
            break;
        }
        cont[j] = currentInstruction[i];
        j++;
    }
    if (! assigned){
        comp.assign(act);
    }
    free(cont);
    return comp;
}

string Parser::jump(){
    int i;
    string jump;
    int len = currentInstruction.length();
    char* cont = new char[len];
    int dest_len;
    int j = 0;
    bool start_assigning = false;
    cont[0] = '\0';
    for(i=0; i < currentInstruction.length(); i++) {
        if (currentInstruction[i] == ' ') {
            continue;
        }
        if (start_assigning) {
            cont[j] = currentInstruction[i];
            j++;
        }
        if (currentInstruction[i] == ';') {
            start_assigning = true;
        }
    }
    jump.assign(cont);
    free(cont);
    cout << "jmp is " + jump + "\n";
    return jump;
}