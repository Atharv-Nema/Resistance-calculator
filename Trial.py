import numpy as np
import math
def pairs(N):
    vec = np.arange(N)
    np.random.shuffle(vec)
    return (vec[:N//2], vec[N//2:])
def kinetic_exchange(v,w):
    R = np.random.uniform(size = len(v))
    return ((v + w) * R, (v + w) * (1 - R))
def sim(people,T):#O(T*n)
    for i in range(T):
        print(i)
        pair = pairs(len(people))#O(n) I assume
        x = kinetic_exchange(people[pair[0]],people[pair[1]])#O(n)
        people[pair[0]] = x[0]
        people[pair[1]] = x[1]
        '''ind = np.append(pair[0],pair[1])#O(n)
        people = np.append(x[0],x[1])[ind]#O(n).'''
    return people
def stable_sim(people):
    while(True):
        pair = pairs(len(people))
        x = kinetic_exchange(people[pair[0]],people[pair[1]])
        ind = np.append(pair[0],pair[1])
        temp = np.append(x[0],x[1])[ind]
        if(math.fabs((np.var(people) - np.var(temp))/np.var(temp)) < 0.1):#The stability condition
            return temp
        people = np.append(x[0],x[1])[ind]
people = np.ones(50000)
print("here?")
people = stable_sim(people)
new_people = sim(people,300000)
#answer = mobility(people,new_people)