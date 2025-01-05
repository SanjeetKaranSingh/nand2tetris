#include <iostream>
#include <map>

#include "symbol_table.h"

using namespace std;


SymbolTable::SymbolTable()
{
    cout << "Initializing symbol table\n";
    table = {
        {"R0", 0},
        {"R1", 1},
        {"R2", 2},
        {"R3", 3},
        {"R4", 4},
        {"R5", 5},
        {"R6", 6},
        {"R7", 7},
        {"R8", 8},
        {"R9", 9},
        {"R10", 10},
        {"R11", 11},
        {"R12", 12},
        {"R13", 13},
        {"R14", 14},
        {"R15", 15},
        {"SCREEN", 16384},
        {"KBD", 24576},
        {"SP", 0},
        {"LCL", 1},
        {"ARG", 2},
        {"THIS", 3},
        {"THAT", 4},
        {"LOOP", 4},
        {"STOP", 18},
        {"i", 16},
        {"sum", 17}
    };
}

SymbolTable::~SymbolTable()
{
}

void SymbolTable::addEntry(string symbol, int address) {
    table[symbol] = address;
}

bool SymbolTable::contains(string symbol) {
    return table.count(symbol.data()) > 0;
}

int SymbolTable::getAddress(string symbol) {
    return table[symbol.data()];
}