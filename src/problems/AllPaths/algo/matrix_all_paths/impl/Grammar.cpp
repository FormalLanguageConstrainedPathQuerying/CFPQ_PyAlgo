
#include "Grammar.h"
#include <sstream>
#include <fstream>
#include <iostream>

using namespace std;

using std::istringstream;
using std::ifstream;
using std::ofstream;
using std::string;
using std::vector;


Grammar::Grammar(const string &grammar_filename) {

    auto chomsky_stream = ifstream(grammar_filename, ifstream::in);

    string line, tmp;
    getline(chomsky_stream, line);
    getline(chomsky_stream, line);
    while (getline(chomsky_stream, line)) {
        vector<string> terms;
        istringstream iss(line);
        while (iss >> tmp) {
            if(tmp != "->")
            {
                terms.push_back(tmp);
            }
        }
        if (!nonterminal_to_index.count(terms[0])) {
            nonterminal_to_index[terms[0]] = nonterminals_count++;
        }
        if (terms.size() == 2) {
            if (!terminal_to_nonterminals.count(terms[1])) {
                terminal_to_nonterminals[terms[1]] = {};
            }
            terminal_to_nonterminals[terms[1]].push_back(nonterminal_to_index[terms[0]]);
        } else if (terms.size() == 3) {
            if (!nonterminal_to_index.count(terms[1])) {
                nonterminal_to_index[terms[1]] = nonterminals_count++;
            }
            if (!nonterminal_to_index.count(terms[2])) {
                nonterminal_to_index[terms[2]] = nonterminals_count++;
            }
            rules.push_back(
                    {nonterminal_to_index[terms[0]], {nonterminal_to_index[terms[1]], nonterminal_to_index[terms[2]]}});
        }
    }
    chomsky_stream.close();
}

Grammar::~Grammar() {
    for (unsigned int i = 0; i < nonterminals_count; ++i)
        delete matrices[i];
}

char* Grammar::get_elements(std::string S)
{
    return matrices[nonterminal_to_index[S]]->get_elements();
}

void Grammar::print_results(const string &output_filename, int time) {
    ofstream out_stream;
    out_stream.open(output_filename, ios::app);
    out_stream << time / 1000.0 << std::endl;
    for (auto &nonterm : nonterminal_to_index) {
        unsigned long count = 0;
        out_stream << nonterm.first << " ";
        out_stream << matrices[nonterm.second]->get_nvals() << endl;
    }
    out_stream.close();
}

