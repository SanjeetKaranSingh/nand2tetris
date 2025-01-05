#include <iostream>
#include <map>
#include <algorithm>
#include "code.h"

using namespace std;

Code::Code()
{
}

Code::~Code()
{
}

string Code::dest(string in){
    map<string, string> dest_dict = {
        { "null", "000"},
        {"M", "001"},
        {"D", "010"},
        {"DM", "011"},
        {"A", "100"},
        {"AM", "101"},
        {"AD", "110"},
        {"ADM", "111"}
    };
    sort(in.begin(), in.end());
    if (dest_dict.find(in.data()) != dest_dict.end())
        return dest_dict.at(in.data());
    cout << "dest null for " + in + "rr\n";
    return dest_dict.at("null");
}

string Code::comp(string in){
    map<string, string> comp_dict = {
        { "0", "0101010"},
        {"1", "0111111"},
        {"-1", "0111010"},
        {"D", "0001100"},
        {"A", "0110000"},
        {"M", "1110000"},
        {"!D", "0001101"},
        {"!A", "0110001"},
        {"!M", "1110001"},
        {"-D", "0001111"},
        {"-A", "0110011"},
        {"-M", "1110011"},
        {"D+1", "0011111"},
        {"A+1", "0110111"},
        {"M+1", "1110111"},
        {"D-1", "0001110"},
        {"A-1", "0110010"},
        {"M-1", "1110010"},
        {"D+A", "0000010"},
        {"D+M", "1000010"},
        {"D-A", "0010011"},
        {"D-M", "1010011"},
        {"A-D", "0000111"},
        {"M-D", "1000111"},
        {"D&A", "0000000"},
        {"D&M", "1000000"},
        {"D|A", "0010101"},
        {"D|M", "1010101"},
    };
    if (comp_dict.count(in.data()) > 0)
        return comp_dict.at(in.data());
    cout << "comp null for " + in + "\n";
    return comp_dict.at("0");
}

string Code::jump(string in){
    map<string, string> jump_dict = {
        { "null", "000"},
        {"JGT", "001"},
        {"JEQ", "010"},
        {"JGE", "011"},
        {"JLT", "100"},
        {"JNE", "101"},
        {"JLE", "110"},
        {"JMP", "111"}
    };
    if (jump_dict.count(in.data()) > 0)
        return jump_dict.at(in.data());
    cout << "jump null for " + in + "\n";
    return jump_dict.at("null");
}