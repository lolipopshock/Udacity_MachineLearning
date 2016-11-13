Udacity Machine Learning NanoDegree Program Report

### Project 4: Train a Smart Cab to Drive 

#### 0 Contents

[TOC]

#### 1 Brief Introduction 

Self-driving car has been a increasingly important issue nowadays. Different ways of training cars to drive, such as neuron networks in supervised learning, have been applied in industry. 

In this project, the method of q-learning in reinforcement learning was selected. After several tests, it showed remarkable capibility of learning the specific traffic rule and helped the car successfully driving to its destination.

#### 2 Implement a Basic Driving Agent

The core idea of this task is to let the primary cab to drive in the specific grid world. By passing an action selected from all possible actions to the variable `action`  , the car will automatically run in the grid world.

##### 2.1 Code Implementaton

```python
action = random.choice([None, 'forward', 'left', 'right']) # line44
```

##### 2.2 Question Answering

1. ***Does the smartcab eventually make it to the destination?*** 
   I've tried several times and, amazingly, the cab successfully got to the destination for almost all of these trials without time limitation. It may reflect the famous theorem-infinite monkey theorem.
2. ***Are there any other interesting observations to note?***
   1. From my observation, the smartcab with random actions may go through every point in the grid world. If the destination is close to the starting point of the cab, then the cab will quickly get to the destination.
   2. Since there is no learning algorithms in the cab, the movements of the cab can be seen as gambling - even though it is close to the destination, it will still turn around and get away from the destination.

#### 3 Inform the Driving Agent

Chosing the state variable may be the most important thing in q-learning implementation. It will not only decide the scale of the q-learning matrix, which is relevant to the scale of the problem, but also what it will learn in every epsidoe. 

##### 3.1 Code Implementation 

```Python
self.state = (self.next_waypoint,
              inputs['light'], 
              inputs['oncoming'], 
              inputs['left'], 
              inputs['right'])
# line42
```

##### 3.2 Question Answering

1. ***What states have you identified that are appropriate for modeling the smartcab and environment?***
   After several tests, I finally chose the following values for my state variable:

   1. cab's current next_waypoint (value can be chosen from: `left`, `right`,`None`)
   2. current traffic light color (`red`, `green`)
   3. cab's current oncoming direction car condition (`left`, `right`,`None`)
   4. cab's current left direction car condition (`left`, `right`,`None`)
   5. cab's current right direction car condition (`left`, `right`,`None`)

2. ***Why do you believe each of these states to be appropriate for this problem?***

   1. For the first value, it reflects the next direction of the cab and helps the cab get to the destination as fast as possible.
   2. For the rest value, it helps the cab to learn traffic rules - how the cab should act at a conjunction is simultaneously decided by the color of traffic light and whether there are cabs and their next driving directions on other connected roads.
   3. **<u>[NEW]</u>** Reasons for NOT choosing deadline:
      It seems reasonable for choosing deadline features, but is it worthwhile to do so? 
      - deadline indicates the time effectiveness of the algorithm, but a next_waypoint will function a little in representing the time effectiveness because a penalty will be given if the next_waypoint is not right.
      - the states for deadline is too many: there are 30 different states ranging for 0 to 29. It will remarkably increase the scale of the Q_learning matrix. I think it's not worthwhile.
   4. **<u>[NEW]</u>** Whether to exclude cab's current right direction car condition:
      A dilemma for me. For the symmetry of the grid world at a conjunction, it seems the right and left direction condition may have similar effects, that is, the right direction can be excluded. But for considerately dealing with the problem, I just chose to include the feature.

3. ***How many states in total exist for the smartcab in this environment?*** 
   $$
   3 * 2 * 3 * 3 * 3 = 162
   $$


4. ***Does this number seem reasonable given that the goal of Q-Learning is to learn and make informed decisions about each state? Why?***
   I think it's OK, though the scale of states seems to be large.

   - *The scale of the major learning object is not that large.*
     Under most of the circumstances, the last three values of state is `None`, that is, the size of major learning is 6,  which helps the cab learn how to get to the destination as soon as possible with obeying the traffic rule. And generally, it will always takes more than 6 steps for the cab to get to its destination for each epsidoe. Consequently, it will fastly learn how to drive. 
   - *For other situations, it will learn very fast.*
     Secondly, when the last three circumstances are not `None`, most common situations are there are just one cabs on the near roads ( from the perspective of probability). And when a wrong action is selected, a negative point will be granted. So it will pick another action next time when facing the same situation, that is, it will learn very quickly for these circumstances.
   - *Conclusion: it's generally reasonable for chosing the state.*


#### 4 Implement a Q-Learning Driving Agent

The Following formula is applied for updating Q Matrix:
$$
Q(s,a) = (1-\alpha)\times Q(s,a)+\alpha\times(r+\gamma\times\max(Q(s_{next},a_{next}))) .
$$

##### 4.1 Code Implementation

*Only the code for initializing and updating the Q matrix and the implementation of eplison greedy exploration is shown. Others are in the agent.py.* ;)

```python
# initializing 
for dr in self.action_scheme:
    for lt in ['red','green']:
        for dron in self.action_scheme:
            for drlf in self.action_scheme:
                for drrt in self.action_scheme:
                    self.q_table[(dr,lt,dron,drlf,drrt)] = [0, 0, 0, 0]
# line22
```

```python
# updating
self.q_table[self.state][action] = \ 
	(1 - alpha) * self.q_table[self.state][action] + \
	alpha * (reward + gamma * max(self.q_table[state_new]))
# line54
```

```python
# eplison greedy exploration
def choose_action(self):
    currentaction = self.q_table[self.state]
    actionscore = max(currentaction)
    actionnum = currentaction.count(actionscore)
    if actionnum > 1
        if random.random() <= self.eplison:
            bestaction = [val+random.random() 
                          if val== actionscore else val for val in currentaction ]
            action = bestaction.index(max(bestaction))
    else:
        action = currentaction.index(actionscore)
    return action
# line56
```

##### 4.2 <u>[NEW]</u> Ideas for implementing random exploration

My idea: if there is multiple choice with same max q value, then randomly choose from the actions with max values. if not, then just choose the only action.

There is a small trick in implementing the code, I think you can easily figure it out.

I think pure eplison greedy exploration with random choice is too aggressive, so I just prefer the more tender one.

##### 4.3 Question Answering

1. ***What changes do you notice in the agent's behavior when compared to the basic driving agent when random actions were always taken?***
   The action gradually seems reasonable, i.e, the movement of the cab is not kind aimless wondering but a series of purposive strategy to get the destination as soon as possible with obeying the traffic rule. 
2. ***Why is this behavior occurring?***
   In my opinion, it generally comes down to the reinforcement learning. If an action of the cab is right(heading to the destination and not violating the traffic rule), a positive reward is endowed. And it will choose the action with the highest q value. So a seemingly 'right' action is tend to be chosen in the next movement. 

#### 5 Improve the Q-Learning Driving Agent

Tunning a learning algorithm can be seen as a kind of art. 

##### 5.1 Successful Rate as A Metric for Learning

**<u>[NEW]</u>** For each combination of parameters, I choose the successful rate as the metric for judging wheter it's a good learning agent. The definiton of successful rate is defined as below:


$$
rate = \frac{times}{100}
$$
The times is the total successful times recorded in all 100 training episodes.

And for each combination of parameters, I just run training session for only one time( for time saving), although it will be not that accurate for reflecting the real situation.

##### 5.2 Blind Search For appropriate α,γ,ε

I've implemented some loops to passing different α, γ, ε values to the learning agent and fetch its corresponding successful rate. The output data is stored in  the txt file `data1.txt` and csv file `dataall.csv` .

```python
res = dict()
for a in range(3,7):
    for g in range (3,7):
        for e in range (1,6):
            alpha = float(a)/10
            gamma = float(g)/10
            eplison = float(e)/10
            res[(alpha,gamma,eplison)] = run(alpha,gamma,eplison)
# line92
```

And the result is shown below:

![successful rate - eplison](/Learning/Udacity_MLND_2016C/Projects/P4/successful rate - eplison.jpg)

▲ We can see higher ε tends to have a better successful rate.

![successful rate - alpha](/Learning/Udacity_MLND_2016C/Projects/P4/successful rate - alpha.jpg)

▲ When ε is 0.4 or 0.5, the performance of α is relatively steady.

![successful rate - gamma](/Learning/Udacity_MLND_2016C/Projects/P4/successful rate - gamma.jpg)

▲ When ε is 0.4 or 0.5, the performance of γ is also relatively steady.

**Colclusion**: It's better to take 0.4 or 0.5 for ε. But there are not specific trend for α and γ.

##### 5.3 Peformance with selected parameter value.

| **α** | **γ** | **ε** | successful rate |
| :---: | :---: | :---: | :-------------: |
| *0.3* | *0.6* | *0.5* |       *1*       |
| *0.4* | *0.4* | *0.5* |       *1*       |
| *0.6* | *0.3* | *0.5* |       *1*       |
| *0.5* | *0.6* | *0.4* |       *1*       |
| *0.4* | *0.3* | *0.5* |       *1*       |
| *0.4* | *0.4* | *0.4* |       *1*       |

And the outcoming result is correspond to my previous assumption: successful rate is sensitive to ε and relatively not sensitive  to α and γ ( in my selection of range of α and γ). 

##### 5.3 Accumulated Reward Graph with selected tests

I've chosen the first and the last test shown in the table above and plot their accumulated reward graph.

![reward 1](/Learning/Udacity_MLND_2016C/Projects/P4/reward 1.jpg) ![reward 3](/Learning/Udacity_MLND_2016C/Projects/P4/reward 3.jpg)

##### 5.4 Question Answering

1. ***Report the different values for the parameters tuned in your basic implementation of Q-Learning. For which set of parameters does the agent perform best? How well does the final driving agent perform?***
   Shown Above. Any parameter combination appeared in the table above can be my choice with the successful rate equal to 1.
2. ***Does your agent get close to finding an optimal policy, i.e. reach the destination in the minimum possible time, and not incur any penalties?***
   I think yes. **<u>[NEW]</u>** But there are still some problems. 
   - *It is possible that the agent goes in circles to accumulate more reward before reaching destination.* 
     By observing the peaks in the reward graph above, the uncommonly high rewards mostly come down to the circling problem.
   - Suggestions for redesining state to reduce the occurrence of such behavior
     The core problem for current learning scheme is that: it doesn't give faster agent higher rewards. That is, it creates some lazy agents that are only required to reach the destination before the deadline, but not fast agents that are asked to reach the destination as fast as possible.
     But it's dangerous. If faster agents get higher rewards, then finally the route the agents will take may just converge to the cloest path. The car will neglect the traffic rules and rush to the destination if the rewards are not well set.
3. ***How would you describe an optimal policy for this problem?***
   * drive in the shortest direction
   * obey the traffic rule.

#### 6 Conclusion

Such a tough and wonderful work…….