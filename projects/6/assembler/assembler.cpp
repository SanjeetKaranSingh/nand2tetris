#include <iostream>
#include <bitset>
#include "parser.h"
#include "code.h"
#include "symbol_table.h"

using namespace std;

void first_pass(Parser *parser, SymbolTable* symbolTable) {
    string symbol;
    int counter = 0;
    cout << "First pass running\n";
    while (parser->hasMoreLines())
    {
        parser->advance();
        cout << parser->currentInstruction + "\n";
        if (parser->getInstructionType() == instructionTypeL) {
            symbol = parser->symbol();
            cout << "Adding label " + symbol + " \n";
            symbolTable->addEntry(symbol, counter);
        } else {
            cout << "Ignoring as not L instruction\n";
            counter++;
        }
    }
}

bool is_number(const std::string& s)
{
    if (s.empty()) {
        return false;
    }

    for (char chr: s) {
        if (chr == 0) {
            return true;
        } 
        else if (! isdigit(chr) ){
            return false;
        }
    }
    return true;
}

void second_pass(Parser *parser, SymbolTable* symbolTable, ofstream &output) {
    Code code;
    instructionType itype;
    string symbol;
    int symboladdr = 16;
    int symbol_int;
    string binary_symbol;
    string out;

    parser->reset();
    while (parser->hasMoreLines()) {
        cout << "here\n";
        parser->advance();
        cout << parser->currentInstruction + "\n";
        cout << "there\n";
        itype = parser->getInstructionType();
        if (itype == instructionTypeA) {
            symbol = parser->symbol();

            if (is_number(symbol)) {
                symbol_int = atoi(symbol.c_str() );
            }
            else if (symbolTable->contains(symbol)) {
                cout << "symbol " + symbol + " exists, taking that value\n";
                cout << symbol + "\n";
                symbol_int = symbolTable->getAddress(symbol);
                cout << symbol_int;
                cout << "\nend\n";
            } else {
                cout << "symbol " + symbol +" doesn't exist, adding it\n";
                symbolTable->addEntry(symbol, symboladdr);
                symbol_int = symboladdr;
                symboladdr++;
            }

            binary_symbol = bitset<16>(symbol_int).to_string();
            out = binary_symbol;
            output <<  out + '\n';
        }
        else if (itype == instructionTypeC) {
            // Fix this, everything else seems fine.
            string comp = parser->comp();
            string dest = parser->dest();
            string jump = parser->jump();
            out = "111" + code.comp(comp) +  code.dest(dest) + code.jump(jump);
            output <<  out + '\n';
        }
    }
}


int main(int argc, char **argv) {
    if (argc < 2){
        cout << "Wrong input";
        return 1;
    }

    char *asm_file = argv[1];
    Parser parser = Parser(asm_file);
    SymbolTable symbolTable;
    first_pass(&parser, &symbolTable);
    ofstream myfile;
    string out(asm_file);
    out = out.substr(0, out.length() -3);
    myfile.open(out + "hack");
    second_pass(&parser, &symbolTable, myfile);
    myfile.close();
    return 0;
}