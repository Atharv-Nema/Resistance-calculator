#include <bits/stdc++.h>
#include "Math.cpp"
using namespace std;

int main(){
    //Test 1
    
    vector<vector<pair<double, int>> > series_parallel = {{make_pair(6,1),make_pair(6,1),make_pair(6,1)},{make_pair(6,0),make_pair(6,0),make_pair(6,0),make_pair(6,2),make_pair(6,2),make_pair(6,2)},{make_pair(6,1),make_pair(6,1),make_pair(6,1)}};
    
    Circuit t1 = Circuit(series_parallel);
    cout << t1.getResistance() << endl;// Expected 4
    

    cout << "Hello" << endl;
    vector<vector<pair<double, int>> > balanced_wheatstone = {{make_pair(6,1),make_pair(3,2)},{make_pair(6,0),make_pair(6,3),make_pair(4,2)},{make_pair(3,0),make_pair(3,3),make_pair(4,1)},{make_pair(6,1),make_pair(3,2)}};
    Circuit t2 = Circuit(balanced_wheatstone);
    cout << t2.getResistance() << endl;// Expected 4
}