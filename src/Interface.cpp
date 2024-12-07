// This acts as an interface between Main.py and Math.cpp
#include <vector>
#include <iostream>
#include "Math.cpp"
using namespace std;

int main(){
    vector<vector<pair<double, int>>> circuit_graph;
    double voltage;
    cin >> voltage;
    int numNodes;
    cin >> numNodes;
    for(int i = 0; i < numNodes; i++){
        vector<pair<double, int>> v;
        circuit_graph.push_back(v);
    }
    int n;
    cin >> n;
    for(int i = 0; i < n; i++){
        int n1, n2;
        double r;
        cin >> n1 >> n2 >> r;
        circuit_graph[n1].push_back({r, n2});
        circuit_graph[n2].push_back({r, n1});
    }
    Circuit c(circuit_graph, voltage);

    // First line is the total resistance
    cout << c.getResistance() << '\n';

    // Second line is the voltage at each node
    for(int i = 0; i < numNodes; i++){
        cout << c.getVoltage(i) << ' ';
    }

    // Next few lines contain the current information
    for(int node = 0; node < circuit_graph.size(); node++){
        for(pair<double, int> p: circuit_graph[node]){
            int neighbour = p.second;
            if(node < neighbour){
                cout << '\n' << node << " " << neighbour << " " << c.getCurrent(node, neighbour);
            }
        }
    }
    
    return 0;
}