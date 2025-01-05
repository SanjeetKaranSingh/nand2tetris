#ifndef SymbolTable_H
#define SymbolTable_H

#include <iostream>
#include <map>

using namespace std;

class SymbolTable
{
private:
    map<string, int> table;
public:
    SymbolTable(/* args */);
    ~SymbolTable();
    void addEntry(string symbol, int address);
    bool contains(string symbol);
    int getAddress(string symbol);
};


#endif