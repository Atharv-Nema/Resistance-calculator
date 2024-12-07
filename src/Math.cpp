#include <vector>
#include "../eigen-3.4.0/Eigen/Dense"
#include <iostream>
using namespace std;

class Circuit{
    private:
        /*The node labeled 0 is connected to the positive terminal.(voltage)
        The node labeled graph.size() - 1 is connected to the negative terminal(0)
        So we have n unknown nodes(graph.size() - 2) and 2 known nodes
        we have n + 1 equations(we wont use the equation from the 0 node as it is redundant)*/
        vector<vector<pair<double, int>> > circuitGraph;
        vector<vector<pair<double, int>> > currentOfEdges;
        vector<double> nodeValues; // Voltages at the nodes
        double voltage;
        double netResistance;
        double current;//It is the senders responsibility that the current is used in a responsible manner.
        vector<vector<double>> currentMatrix;
        vector<vector<bool>> connectedMatrix;//Checks if two nodes are connected
        void initialize();
        void performEquivalentDFS(
            vector<int> &equivalent, vector<bool> &checkRequired, 
            vector<int> &dfsStack, vector<bool> &visited
        );
        void fillEquivalent(vector<int> &equivalent, vector<bool> &checkRequired);
        void coefficientAdder(
            int node, 
            vector<int> &equivalent,
            Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &M,
            Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &C
        );
    
    public:
        Circuit(vector<vector<pair<double, int>>> &graph);
        Circuit(vector<vector<pair<double, int>>> graph, double volt);
        double getResistance();
        double getTotalCurrent();
        double getCurrent(int node_1, int node_2);
        double getVoltage(int node_1);
};
Circuit :: Circuit(vector<vector< pair<double, int>>> &graph){
    circuitGraph = graph;
    voltage = 5.0;//The default value
    initialize();
}
Circuit :: Circuit(vector<vector<pair<double, int>> > graph, double volt){
    circuitGraph = graph;
    voltage = volt;
    initialize();
}
double Circuit :: getVoltage(int node_1){
    if(node_1 < 0 || node_1 >= circuitGraph.size()){
        throw new range_error("Out of bounds array");
    }
    else{
        return nodeValues[node_1];
    }
}
double Circuit :: getResistance(){
    return netResistance;
}
double Circuit :: getTotalCurrent(){
    return current;
}
double Circuit :: getCurrent(int node_1, int node_2){//By default node_1 < node_2, else reorder
    if(node_1 < 0 || node_1 >= circuitGraph.size() || node_2 < 0 || node_2 >= circuitGraph.size()){
        throw range_error("Array out of bounds");
    }
    if(!(connectedMatrix[node_1][node_2])){
        throw invalid_argument("Nodes are not connected");
    }
    else{
        if(isnan(currentMatrix[node_1][node_2])){
            /*In cases where a finite current would flow if there was a wire with 0
            resistance connected. However, there are more than 1 wires of 0 resistance connected between the nodes.*/
            throw domain_error("Undefined current");
        }
        else{
            return currentMatrix[node_1][node_2];
        }
    }
}
//Go through this code in context with initialize
void Circuit :: coefficientAdder(
    int node, 
    vector<int> &equivalent,
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &M,
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> &C
){
    //This function just adds the non zero resistance coefficients for the equation equivalent[node] coming from node
    if(equivalent[node] == circuitGraph.size() - 1){
        // This is the last node
        // This is a special case as its equation for circuit_graph.size() - 1 is not included
        M(node, node) = 1; /// This just says that the voltage of node is 0
        return;
    }
    for(int i = 0; i < circuitGraph[node].size(); i++){
        double R = circuitGraph[node][i].first;
        int neighbour = circuitGraph[node][i].second;
        if(equivalent[node] == 0){
            if(R != 0){
                // Updating the C matrix
                C(equivalent[node],0) += -(voltage/R);//(voltage - neighbour)/R is the current
                // Updating the M matrix
                if(neighbour != circuitGraph.size() - 1){//If it is size - 1 then neighbour voltage value is 0.
                    M(equivalent[node],neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
            }
        }
        else{
            if(R != 0){
                M(equivalent[node],equivalent[node]) += (1.0/R);
                if(neighbour == 0){
                    C(equivalent[node],0) += (voltage/R);
                }
                else if(neighbour != circuitGraph.size() - 1){//If it is size - 1 then neighbour value is 0.
                    M(equivalent[node],neighbour) += (-1.0/R);//I am doing += just in case muliple neighbours with the same node val
                }
            }
        }
    }
}
void Circuit :: performEquivalentDFS(
    vector<int> &equivalent, 
    vector<bool> &checkRequired, 
    vector<int> &dfsStack, 
    vector<bool> &visited
){
    while(dfsStack.size() > 0){
        int node = dfsStack[dfsStack.size() - 1];
        dfsStack.pop_back();
        for(auto p: circuitGraph[node]){
            double resistance = p.first;
            double neighbour = p.second;
            if(resistance == 0 && !(visited[neighbour])){
                equivalent[neighbour] = equivalent[node];
                checkRequired[node] = true;
                checkRequired[neighbour] = true;
                visited[neighbour] = true;
                dfsStack.push_back(neighbour);
            }
        }
    }
}

void Circuit :: fillEquivalent(vector<int> &equivalent, vector<bool> &checkRequired){
    // Clear the arrays initially
    equivalent.clear();
    checkRequired.clear();

    // Now, initialize equivalent with the node itself and check required with False
    int N = circuitGraph.size();
    for(int i = 0; i < N; i++){
        equivalent.push_back(i);
        checkRequired.push_back(false);
    }

    // Now, I will perform a simple dfs originating from the two end points
    vector<int> dfsStack;
    vector<bool> visited(N, false);
    dfsStack.push_back(0);
    visited[0] = true;
    performEquivalentDFS(equivalent, checkRequired, dfsStack, visited);
    if(visited[N - 1]){
        throw invalid_argument("Infinite current exception");
    }
    dfsStack.push_back(N - 1);
    visited[N - 1] = true;
    performEquivalentDFS(equivalent, checkRequired, dfsStack, visited);

    //Now perform a simple dfs from all the other nodes
    for(int i = 1; i < N - 1; i++){
        if(!visited[i]){
            dfsStack.push_back(i);
            visited[i] = true;
            performEquivalentDFS(equivalent, checkRequired, dfsStack, visited);
        }
    }
}

void Circuit :: initialize(){
    /*I will make a circuit_graph.size() - 1 = n; n x n size matrix.(Say M)
    Columns correspond to the variables and the rows correspond to equations
    The first column corresponds to i(total current)
    The next n - 1 positions will correspond to the node variables

    I will also make a n x 1 column matrix (C) that represents the constants.
    Hence (inv(M))C[i] where 1 <= i < n represents the voltage at the ith node(zero indexed).
    Voltage of the 0th node is voltage and of the nth node is 0
    (inv(M))[0] represents the total current in the circuit.*/
    if(nodeValues.size() > 0){
        throw logic_error("Exception, you have already initialized the object");
    }
    /*HANDLING ZERO RESISTANCES
    My model allows for wires(zero resistances) to be connected
    I will make a new vector that stores the node value which have the same voltage value as the node(i.e.
    they are connected with a zero resistance)
    I will go through the circuit graph. Say we are at node a and we have found that a is connected to b with a zero resistance
    If a > b then equivalent[a] = equivalent[b](note, here = is assignment). Else equivalent[a] = a. Note that if a is not 
    connected to any such b then equivalent[a] = a
    This means that equivalent[i] = min(node such that node is reachable to i using only zero resistance paths)*/
    

    vector<int> equivalent;
    vector<bool> checkRequired;//Stores if there is a need to search the rest of the array for equivalents.
    
    fillEquivalent(equivalent, checkRequired);
    //If last node is equivalent to node 0, then the circuit is short circuited leading to infinite current
    if(equivalent[equivalent.size() - 1] == equivalent[0]){
        throw invalid_argument("Infinite current exception");
    }

    /*equivalent has been set up
    Now I will go through circuit graph. 
    When I encounter a node, if node == equivalent[node], add the currents for the other nodes which are not connected
    with 0 resistance. Then go through the rest of equivalent to search for equivalence(if check is true).(If check is
    false you are done). If node != equivalent[node], node - equivalent[node] is the equation for the node(as both have the
    same voltage).
    Helper function coefficient_adder  does the adding of coefficients as there was a huge repetition of code(read it now)*/
    
    int n = (circuitGraph.size() - 2) + 1;
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> M(n, n);
    M.setZero();//Coefficient matrix
    Eigen :: Matrix<double, Eigen :: Dynamic, Eigen :: Dynamic> C(n, 1);
    C.setZero();//Constant matrix
    M(0,0) += -1.0;//As the equation involving the first node has -i term()
    
    //I will now populate the matrix
    for(int node = 0; node < circuitGraph.size() - 1; node++){
        //Setting up the base values
        if(node == equivalent[node]){
            coefficientAdder(node, equivalent, M, C);
            if(checkRequired[node]){
                // Note: The way that I have performed the dfs, for node < circuitGraph.size(), 
                // (equivalent[x] == node) => node <= x
                for(int equi = node + 1; equi < circuitGraph.size(); equi++){
                    if(equivalent[equi] == node){
                        coefficientAdder(equi, equivalent, M, C);
                    }
                }
            }
        }
        else{
            if(equivalent[node] == 0){
                // This means that node = voltage(remember that node represents the voltage of the node)
                M(node,node) = 1;
                C(node,0) = voltage;
            }
            else if(equivalent[node] == circuitGraph.size() - 1){
                // node = 0
                M(node,node) = 1;
            }
            else{
                // node = equivalent[node]
                M(node,node) = 1;
                M(node,equivalent[node]) = -1;//Equality condition
            }
        }
    }
    auto soln_mat = M.inverse() * C;
    current = soln_mat(0,0);
    netResistance = voltage/current;
    nodeValues.push_back(voltage);
    for(int i = 1; i < n; i++){
        nodeValues.push_back(soln_mat(i,0));
    }
    nodeValues.push_back(0);
    
    /*Current graph initialization
    Algorithm: I need to take care about the cases of 0 resistances. Hence here is an algo I propose.
    Start from node 0, do situation for all nodes. Give counter of connections with unknown current to each node. 
    Do one pass. After pass you do to each node where 1 unknown exists and give it current. This will reduce other higher
    nodes current too.
    Hence you repeat until you are done.*/

    //Initialize the 2d vector(nan means either that the nodes are not connected or the current in undefined)

    for(int i = 0; i < circuitGraph.size(); i++){
        vector<double> temp1(circuitGraph.size(), NAN);
        currentMatrix.push_back(temp1);
        vector<bool> temp2(circuitGraph.size(),false);
        connectedMatrix.push_back(temp2);
    }
    //Now I want to make a vector that keeps track of the number of zero resistances in connection to a particular node
    //All the non zero resistances are populated with the current
    vector<int> unknown_ct;
    for(int i = 0; i < circuitGraph.size(); i++){
        int ct = 0;
        for(int j = 0; j < circuitGraph[i].size(); j++){
            auto ele = circuitGraph[i][j];
            connectedMatrix[i][ele.second] = true; // So i and ele.second are connected
            if(ele.first == 0){
                ct++;
            }
            else{
                currentMatrix[i][ele.second] = (nodeValues[i] - nodeValues[ele.second])/(ele.first);//Current outwards is positive
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
                double outward_current = 0.0; // Outward known current
                if(i == 0){
                    outward_current -= current;
                }
                else if(i == unknown_ct.size() - 1){
                    outward_current += current;
                }
                for(int j = 0; j < circuitGraph[i].size(); j++){
                    auto ele = circuitGraph[i][j];
                    double current = currentMatrix[i][ele.second];
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
                    currentMatrix[i][unknown_neighbour] = -outward_current;//Kirchoffs law
                    currentMatrix[unknown_neighbour][i] = outward_current; //Current going in == current going out
                    modified = true;//As we have clearly modified
                    unknown_ct[i]--;
                    unknown_ct[unknown_neighbour]--;//As now we have one less unknown
                }
            }
        }
    }
    //Voila! we are done with the core bit. Now just a bit of floating point error cleanup is required
    for(int i = 0; i < circuitGraph.size(); i++){
        for(int j = 0; j < circuitGraph[i].size(); j++){
            auto ele = circuitGraph[i][j];
            if(currentMatrix[i][ele.second] < 1e-8 && currentMatrix[i][ele.second] > -1e-8){
                currentMatrix[i][ele.second] = 0.0;
            }
        }
    }
    //And we are done!!!!
}
