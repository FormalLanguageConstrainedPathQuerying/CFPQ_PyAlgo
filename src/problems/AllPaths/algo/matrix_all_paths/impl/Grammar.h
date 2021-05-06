#ifndef CFPQ_CFPQ_H
#define CFPQ_CFPQ_H

#include <string>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <iostream>
#include <vector>
#include "apmatrix.h"
#include "Graph.h"

using nonterminals_pair = std::pair<unsigned int, unsigned int>;

class Grammar {

public:
    explicit Grammar(const std::string &grammar_filename);

    ~Grammar();

    char* get_elements(std::string S);

    unsigned int intersection_with_graph(Graph &graph) {
        vertices_count = graph.vertices_count;
        matrices.reserve(nonterminals_count);
        rules_with_nonterminal.reserve(nonterminals_count);

        for (unsigned int i = 0; i < nonterminals_count; ++i) {
            rules_with_nonterminal.emplace_back();
            matrices.push_back(new ApMatrix(vertices_count));
        }

        for (unsigned int i = 0; i < rules.size(); ++i) {
            rules_with_nonterminal[rules[i].second.first].push_back(i);
            rules_with_nonterminal[rules[i].second.second].push_back(i);
            to_recalculate.insert(i);
        }

        for (auto &edge : graph.edges) {
            for (unsigned int nonterm : terminal_to_nonterminals[edge.first]) {
                matrices[nonterm]->set_bit(edge.second.first, edge.second.second);
            }
        }

        using namespace std::chrono;
        high_resolution_clock::time_point begin_time = high_resolution_clock::now();

        while (!to_recalculate.empty()) {
            unsigned int rule_index = *to_recalculate.begin();
            to_recalculate.erase(to_recalculate.begin());
            unsigned int C = rules[rule_index].first;
            unsigned int A = rules[rule_index].second.first;
            unsigned int B = rules[rule_index].second.second;

            if (matrices[C]->add_mul(matrices[A], matrices[B])) {
                for (unsigned int changed_rule_index: rules_with_nonterminal[C]) {
                    to_recalculate.insert(changed_rule_index);
                }
            }
        }
        high_resolution_clock::time_point end_time = high_resolution_clock::now();
        milliseconds elapsed_secs = duration_cast<milliseconds>(end_time - begin_time);
        return static_cast<unsigned int>(elapsed_secs.count());
    }

 std::vector<int> get_paths(unsigned int i, unsigned int j, const std::string &nonterm_name, unsigned int current_len) {
        if (current_len > 0)
        {
            unsigned int S = nonterminal_to_index[nonterm_name];
            ApMatrix* m = matrices[S];
            unsigned int size = m->get_size();
            PathIndex* pindex = m->get_bit(i, j);
            if (PathIndex_IsIdentity(pindex))
            {
                delete pindex;
                return std::vector<int>();
            }
            unsigned int k = 0;
            std::vector<int> res;
            for (unsigned int mid = 0; mid < pindex->size; mid++)
            {
                k = pindex->middle[mid];
                if (k == size)
                {
                    res.push_back(1);
                }
                else
                {
                    for (auto rule : rules)
                    {
                        if(rule.first == S)
                        {
                            unsigned int A = rule.second.first;
                            unsigned int B = rule.second.second;
                            std::string A_name, B_name;
                            for (auto &nonterm : nonterminal_to_index)
                            {
                                if (nonterm.second == A)
                                {
                                    A_name = nonterm.first;
                                }
                                else if (nonterm.second == B)
                                {
                                    B_name = nonterm.first;
                                }
                            }
                            
                            std::vector<int> left_paths = get_paths(i, k, A_name, current_len - 1);
                            if(left_paths.size() > 0)
                            {
                                unsigned int min_len = current_len;
                                for (auto p : left_paths)
                                {
                                    if (p < min_len)
                                    {
                                        min_len = p;
                                    }
                                }
                                
                                std::vector<int> right_paths = get_paths(k, j, B_name, current_len - min_len);
                                for(auto p1 : left_paths)
                                {
                                    for(auto p2 : right_paths)
                                    {
                                        if (p1 + p2 < current_len)
                                        {
                                            res.push_back(p1 + p2);
                                        }
                                    }
                                }
                            }

                        }
                    }
                }

            }

            delete pindex;

            return res;
        }
        return std::vector<int>();
    }

    void print_results(const std::string &output_filename, int time);

    unsigned int nonterminals_count = 0;
    unsigned int vertices_count = 0;

    std::unordered_set<unsigned int> to_recalculate;
    std::vector<std::vector<unsigned int>> rules_with_nonterminal;
    std::map<std::string, unsigned int> nonterminal_to_index;
    std::unordered_map<std::string, std::vector<int>> terminal_to_nonterminals;
    std::vector<std::pair<unsigned int, nonterminals_pair>> rules;
    std::vector<ApMatrix *> matrices;
};

#endif //CFPQ_CFPQ_H

