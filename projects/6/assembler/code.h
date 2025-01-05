#ifndef CODE_H
#define CODE_H
#include <iostream>

using namespace std;

class Code
{
private:
public:
    Code();
    ~Code();
    string dest(string in);
    string comp(string in);
    string jump(string in);
};

#endif