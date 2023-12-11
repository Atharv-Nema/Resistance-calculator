#include <bits/stdc++.h>
#include "eigen-3.4.0/Eigen/Dense"
using namespace std;

class Circuit{
    private:
        vector<vector<pair<double, int>> > circuit_graph;
        vector<double> node_values;
        double voltage;
        double net_resistance;
        double current;//It is the senders responsibility that the current is used in a responsible manner.
        void initialize();
    
    public:
        Circuit(vector<vector<pair<double, int>> > graph);
        //The node labeled 0 is connected to the positive terminal.(voltage)
        //The node labeled graph.size() - 1 is connected to the negative terminal(0)
        //So we have n unknown nodes(graph.size() - 2) and 2 known nodes
        //we have n + 1 equations(we wont use the equation from the 0 node as it is redundant)
        Circuit(vector<vector<pair<double, int>> > graph, double volt);
        double getResistance();
        double getTotalCurrent();
        double getCurrent(int node_1, int node_2);
};
Circuit :: Circuit(vector<vector< pair<double, int>> > graph){
    circuit_graph = graph;
    voltage = 5.0;//The default value
    initialize();
}
Circuit :: Circuit(vector<vector<pair<double, int>> > graph, double volt){
    circuit_graph = graph;
    voltage = volt;
}
double Circuit :: getResistance(){
    return net_resistance;
}
double Circuit :: getTotalCurrent(){
    return current;
}
double Circuit :: getCurrent(int node_1, int node_2){
    vector<pair<double,int>> connected_node_1 = circuit_graph[node_1];
    for(int i = 0; i < connected_node_1.size(); i++){
        if(connected_node_1[i].second == node_2){
            if(connected_node_1[i].first == 0){
                //TODO: Handle this
                return 55555555;
            }
            else{
                return (node_values[node_1] - node_values[node_2]) / connected_node_1[i].first;
            }
        }
    }
    throw invalid_argument("node_1 and node_2 are not connected");
}
void Circuit :: initialize(){
    //I will make a circuit_graph.size() - 1 = n; n x n size matrix.(Say M)
    //The first column corresponds to i
    //The next n - 1 positions will correspond to the node variables
    //The last row will correspond to the current i.

    //I will also make a n x 1 column matrix (C) that represents the constants.

    //Hence (M-1)C[i] where 0 <= i < n - 1 represents the voltage at the ith node
    //(M-1)[n - 1] represents the total current in the circuit.
    if(node_values.size() > 0){
        throw "Exception, you have already initialized the object";
    }
    int n = circuit_graph.size() - 1;
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> M(n, n);
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> C(n, 1);
    M(0,0) += -1.0;//As the equation involving the first node has -i term
    
    //I will now populate the matrix
    for(int node = 0; node < circuit_graph.size() - 1; node++){
        //Setting up the base values
        for(int j = 0; j < circuit_graph[node].size(); j++){
            double R = circuit_graph[node][j].first;
            int neighbour = circuit_graph[node][j].second;
            //Special case for constant handling
            if(node == 0){
                C(node,0) += -(voltage/R);
                if(neighbour != circuit_graph.size() - 1){//If it is size - 1 then neighbour value is 0.
                    M(node,neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
            }
            else{
                //No constants
                
                M(node,node) += (1.0/R);
                
                if(neighbour == 0){
                    C(node,0) += (voltage/R);
                }
                else if(neighbour != circuit_graph.size() - 1){//If it is size - 1 then neighbour value is 0.
                    M(node,neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
                
            }
        }
    }
    //Populating the values
    auto soln_mat = M.inverse() * C;
    current = soln_mat(0,0);
    net_resistance = voltage/current;
    node_values.push_back(voltage);
    for(int i = 1; i < n - 1; i++){
        node_values.push_back(soln_mat(i,0));
    }
    node_values.push_back(0);
}
