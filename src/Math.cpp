#include <bits/stdc++.h>
#include "../eigen-3.4.0/Eigen/Dense"
using namespace std;

class Circuit{
    private:
        /*The node labeled 0 is connected to the positive terminal.(voltage)
        The node labeled graph.size() - 1 is connected to the negative terminal(0)
        So we have n unknown nodes(graph.size() - 2) and 2 known nodes
        we have n + 1 equations(we wont use the equation from the 0 node as it is redundant)*/
        vector<vector<pair<double, int>> > circuit_graph;
        vector<vector<pair<double, int>> > current_of_edges;
        vector<double> node_values;
        double voltage;
        double net_resistance;
        double current;//It is the senders responsibility that the current is used in a responsible manner.
        vector<vector<double>> current_matrix;
        vector<vector<bool>> connected_matrix;//Checks if two nodes are connected
        void initialize();
        void coefficient_adder(int node,vector<int> &equivalent,Eigen :: Matrix<double, 
        Eigen :: Dynamic, Eigen :: Dynamic> &M,Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &C);
    
    public:
        Circuit(vector<vector<pair<double, int>> > graph);
        Circuit(vector<vector<pair<double, int>> > graph, double volt);
        double getResistance();
        double getTotalCurrent();
        double getCurrent(int node_1, int node_2);
        double getVoltage(int node_1);
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
double Circuit :: getVoltage(int node_1){
    if(node_1 < 0 || node_1 >= circuit_graph.size()){
        throw new range_error("Out of bounds array");
    }
    else{
        return node_values[node_1];
    }
}
double Circuit :: getResistance(){
    return net_resistance;
}
double Circuit :: getTotalCurrent(){
    return current;
}
double Circuit :: getCurrent(int node_1, int node_2){//By default node_1 < node_2, else reorder
    if(node_1 < 0 || node_1 >= circuit_graph.size() || node_2 < 0 || node_2 >= circuit_graph.size()){
        throw range_error("Array out of bounds");
    }
    if(!(connected_matrix[node_1][node_2])){
        throw invalid_argument("Nodes are not connected");
    }
    else{
        if(isnan(current_matrix[node_1][node_2])){
            /*In cases where a finite current would flow if there was a wire with 0
            resistance connected. However, there are more than 1 wires of 0 resistance connected between the nodes.*/
            throw domain_error("Undefined current");
        }
        else{
            return current_matrix[node_1][node_2];
        }
    }
}
//Go through this code in context with initialize
void Circuit :: coefficient_adder(int node,vector<int> &equivalent,Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &M,
Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &C)
{
    //This function just adds the non zero resistance coefficients for the equation equivalent[node] coming from node
    for(int i = 0; i < circuit_graph[node].size(); i++){
        double R = circuit_graph[node][i].first;
        int neighbour = circuit_graph[node][i].second;
        if(equivalent[node] == 0){
            if(R != 0){
                C(equivalent[node],0) += -(voltage/R);//(voltage - neighbour)/R is the current
            }
            if(neighbour != circuit_graph.size() - 1){//If it is size -1 then neighbour value is 0.
                if(R != 0){
                    M(equivalent[node],neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
            }
        }
        else{
            if(R != 0){
                M(equivalent[node],equivalent[node]) += (1.0/R);
            }
            if(neighbour == 0){
                if(R != 0){
                    C(equivalent[node],0) += (voltage/R);
                }
            }
            else if(neighbour != circuit_graph.size() - 1){//If it is size - 1 then neighbour value is 0.
                if(R != 0){
                    M(equivalent[node],neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
            }
        }
    }
}
void Circuit :: initialize(){
    /*I will make a circuit_graph.size() - 1 = n; n x n size matrix.(Say M)
    Columns correspond to the variables and the rows correspond to equations
    The first column corresponds to i
    The next n - 1 positions will correspond to the node variables

    I will also make a n x 1 column matrix (C) that represents the constants.

    Hence (M-1)C[i] where 0 <= i < n - 1 represents the voltage at the ith node
    (M-1)[n - 1] represents the total current in the circuit.*/
    if(node_values.size() > 0){
        throw logic_error("Exception, you have already initialized the object");
    }
    /*HANDLING ZERO RESISTANCES
    My model allows for wires(zero resistances) to be connected
    I will make a new vector that stores the node value which have the same voltage value as the node(i.e.
    they are connected with a zero resistance)
    I will go through the circuit graph. Say we are at node a and we have found that a is connected to b with a zero resistance
    If a > b then equivalent[a] = equivalent[b]. Else equivalent[a] = a. Note that if a is not connected to any such b then 
    equivalent[a] = a
    This means that equivalent[i] = min(node such that node is reachable to i using only zero resistance paths)*/
    vector<int> equivalent;
    vector<bool> check_required;//Stores if there is a need to search the rest of the array for equivalents.
    for(int i = 0; i < circuit_graph.size(); i++){
        int min_with_zero_res = circuit_graph.size() + 1;//Node with min value connected to the given node with 0 resistance
        for(int j = 0; j < circuit_graph[i].size(); j++){
            auto ele = circuit_graph[i][j];
            if(ele.first == 0){
                if(ele.second < min_with_zero_res){
                    min_with_zero_res = ele.second;
                }
            }
        }
        if(min_with_zero_res < i){
            equivalent.push_back(equivalent[min_with_zero_res]);
            check_required.push_back(false);//As the value of equivalent[node] != node, we don't need to check anything
        }
        else{
            if(min_with_zero_res == circuit_graph.size() + 1){//This means that no connections with 0 resistance
                check_required.push_back(false);//Note that this is what will happen most of the times
            }
            else{
                check_required.push_back(true);//Need a check to add the extra coefficients.
            }
            equivalent.push_back(i);//Irrespective, equivalent[i] = i
        }
    }
    //If last node is equivalent to node 0, then the circuit is short circuited leading to infinite current
    if(equivalent[equivalent.size() - 1] == 0){
        throw invalid_argument("Infinite current exception");
    }
    /*equivalent has been set up
    Now I will go through circuit graph. 
    When I encounter a node, if node == equivalent[node], add the currents for the other nodes which are not connected
    with 0 resistance. Then go through the rest of equivalent to search for equivalence(if check is true).(If check is
    false you are done). If node != equivalent[node], node - equivalent[node] is the equation for the node(as both have the
    same voltage).
    Helper function coefficient_adder  does the adding of coefficients as there was a huge repetition of code(read it now)*/
    
    int n = circuit_graph.size() - 1;
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> M(n, n);
    M.setZero();//Coefficient matrix
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> C(n, 1);
    C.setZero();//Constant matrix
    M(0,0) += -1.0;//As the equation involving the first node has -i term()
    
    //I will now populate the matrix
    for(int node = 0; node < circuit_graph.size() - 1; node++){
        //Setting up the base values
        if(node == equivalent[node]){
            coefficient_adder(node, equivalent, M, C);
            if(check_required[node]){
                for(int equi = node + 1; equi < circuit_graph.size(); equi++){
                    if(equivalent[equi] == node){
                        coefficient_adder(equi, equivalent, M, C);
                    }
                }
            }
        }
        else{
            if(equivalent[node] == 0){
                M(node,node) = 1;
                C(node,0) = voltage;
            }
            else if(equivalent[node] == circuit_graph.size() - 1){
                M(node,node) = 1;
            }
            else{
                M(node,node) = 1;
                M(node,equivalent[node]) = -1;//Equality condition
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
    
    /*Current graph initialization
    Algorithm: I need to take care about the cases of 0 resistances. Hence here is an algo I propose.
    Start from node 0, do situation for all nodes. Give counter of connections with unknown current to each node. 
    Do one pass. After pass u do to each node where 1 unknown exists and give it current. This will reduce other higher
    nodes current too.
    Hence you repeat until you are done.*/

    //Initialize the 2d vector(nan means either that the nodes are not connected or the current in undefined)

    for(int i = 0; i < circuit_graph.size(); i++){
        vector<double> temp1(circuit_graph.size(), NAN);
        current_matrix.push_back(temp1);
        vector<bool> temp2(circuit_graph.size(),false);
        connected_matrix.push_back(temp2);
    }
    //Now I want to make a vector that keeps track of the number of zero resistances in connection to a particular node
    //All the non zero resistances are populated with the current
    vector<int> unknown_ct;
    for(int i = 0; i < circuit_graph.size(); i++){
        int ct = 0;
        for(int j = 0; j < circuit_graph[i].size(); j++){
            auto ele = circuit_graph[i][j];
            connected_matrix[i][ele.second] = true;
            if(ele.first == 0){
                ct++;
                //current_matrix[i][ele.second] = -2; //I dont think this is needed
            }
            else{
                current_matrix[i][ele.second] = (node_values[i] - node_values[ele.second])/(ele.first);//Current outwards is positive
            }
        }
        unknown_ct.push_back(ct);
    }
    
    bool modified = true;//stored if the current_matrix has been modified
    while(modified){
        modified = false;
        for(int i = 0; i < unknown_ct.size(); i++){
            if(unknown_ct[i] == 1){//We can only solve if 1 unknown is there
                int unknown_neighbour = -1;
                double outward_current = 0.0;
                for(int j = 0; j < circuit_graph[i].size(); j++){
                    auto ele = circuit_graph[i][j];
                    double current = current_matrix[i][ele.second];
                    if(isnan(current)){
                        unknown_neighbour = ele.second;
                    }
                    else{
                        outward_current += current;
                    }
                }
                if(unknown_neighbour < 0){
                    throw logic_error("internal state error problem in current matrix");
                }
                else{
                    current_matrix[i][unknown_neighbour] = -outward_current;//Kirchoffs law
                    modified = true;//As we have clearly modified
                    unknown_ct[i]--;
                    unknown_ct[unknown_neighbour]--;//As now we have one less unknown
                }
            }
        }
    }
    //Voila! we are done with the core bit. Now just a bit of floating point error cleanup is required
    for(int i = 0; i < circuit_graph.size(); i++){
        for(int j = 0; j < circuit_graph[i].size(); j++){
            auto ele = circuit_graph[i][j];
            if(current_matrix[i][ele.second] < 1e-8 && current_matrix[i][ele.second] > -1e-8){
                current_matrix[i][ele.second] = 0.0;
            }
        }
    }
    //And we are done!!!!
}
