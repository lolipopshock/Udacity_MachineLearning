Udacity Machine Learning Nanodegree | Capstone Project
September 18, 2016,  **Xavier Massa**

# Smart Maze-Solver Robot

------

## **I. Definition**

### 1.1 **Project Overview**

Here in this project, the student is asked to design a smart maze-solver robot, which can automatically find the path (maybe shortest) from the start point to the endpoint in a maze and not crash into the wall. The robot doesn't have a complete information of the maze: it just knows its adjacent situation (whether there is wall next to itself).

The most important thing is to develop a comprehensive path finding an algorithm, which helps the robot find the way it should go.

Actually, it's generally about building an AI and can be categorized as a **Reinforced Learning** problem.

### 1.2 **Problem Statement**

1. Student needs to previously program the robot so that it can automatically run and find the best path if tested. The robot does NOT have a bird eye view of the maze. It just knows the distance to the wall at its heading direction on every position.
2. Test the robot for the first time: it can go around in the maze and gain some information about the setting of the maze. The time it used is denoted by $t_1$.
3. Test the robot for the second time: the robot must select the best path according to the information it has and rush to the destination. The time it used is denoted by $t_2$.
4. Scoring the robot according to the rule described in section 1.3.

### 1.3 **Scoring Metrics**

#### *1.3.1 Absolute time index $S$*

The score is calucated according to the formula:
$$
S = t_2 + \alpha t_1, \ \ \ \ \alpha = \mbox{a givne constant}
$$
Obviously, we tend to find a robot with lower $S$ score for fast performance.

Throughout the project, the $\alpha$ is set to be 0.03. This gives smaller weight for the first running time, which makes the $S$ index emphasize the second running time.

#### *1.3.2 Successful Rate $r$*

Sometimes, with randomness introduced in, for the same test maze, the robot may not always be able to reach the destination within the given time period. So for a maze, the `tester.py` will be executed for a couple of times $T_0$, with the successful times denoted as $T_1$. The successful rate is defined as:
$$
r = T_1/\ T_0
$$

#### *1.3.3 Maze Evaluation*

Metrics for evaluating the maze is described in the chap 2.3.

### 1.4 **Other Issues**

#### *1.4.1 Start Code*

I made the project mainly based on the [AI startcode](https://www.google.com/url?q=https://drive.google.com/open?id%3D0B9Yf01UaIbUgQ2tjRHhKZGlHSzQ&sa=D&ust=1472819571751000&usg=AFQjCNE-FlWeT--5JJF1p3H6hZaf3Ofo0w) given on the project description page. The `tester.py` is generally not modified, except for the reset state in line 38 and some other print stuff.

#### *1.4.2 Preliminary Assumption*

In the problem description page, the robot can move more than 1 unit in every update period. But is it good for a robot to run too far at a time? The core problem is that it has limited information about the surroundings, that is, it can decide how long it can walk at the beginning. 
In the following, the default moving distance is assumed to be 1 at beginning. After some test of the robot, the distance limitation will be eliminated.

#### *1.4.3 Description of different parts of the report*

Since it's a little bit different kind of problem, the arrangement of the report is slightly different from the samples. For better and faster understanding and grading my report, I made a simple description of different parts of my report:

1. **Definition**
   Including: *Project Overview* (1.1), *Problem Statement* (1.2) and *Metrics* (1.3)
2. **Data Exploration and Visualization**
   Including: *Data Exploration* (2.1), *Exploratory Visualization* (2.2) and *Preprocessing* (2.4)
3. **Analysis & Methodology**
   Including: *Algorithms and Techniques* (chap3) and *Implementation of the Methodology* (chap3)
4. **First Implementation, Test And Conclusion**
   Since I tried 2 different algorithms, the first implementation and test chapter helps me choose which one is better and continue to refine (that is, I dismissed the algorithm with bad performance).
   Including: *Benchmark* (3.1, 3.2) and *Model Comparison and Conclusion* (3.3)
5. **Improvement**
   Including: *Refinement*, *Reflection* and *Improvement* (they are throughout this chap.)
6. **Conclusion**
   Including: *Comparison* (5.1, 5.2), *Justification* (5.2), *Reflection* (5.3) and *Conclusion* (5.4)

------

## **II. Data Exploration and Visualization**

### 2.1 **Data Exploration**

Here in this project, the given 'data' is the maze grid matrix, which seems much neater: there is no outliers and noises and the data is well formatted. ( If there are problems in the maze, the program in `tester.py` will automatically find and report them. )

The given maze data is stored in text files. The first line of a txt file only contains an integer, which represents the dimension of the maze, e.g., 12,14 or 16, denoted by $D$. The next lines are used for the description of the maze. The $i\mbox{-th}$ number in the $j\mbox{-th}$ row (ignoring the first line, counted from 1) represents the maze grid at coordinate $[\ j-1,i-1 \ ]$. 

The numbers describing the maze grids are 4-digits 2-based integers. The 1st (from left to right) digit represents the situation on up side of the grid. If there is an opening on the up side, the digit is 1. Otherwise, it is 0. The 2nd  digit represents that on the right side of the grid, the 3rd represents that on down side, the 4th represents that on the left side. For example, for a given number 5, first we write it into binary form: 0101. Then it means there are two openings in the grid, which is at the top side and the down side.

The target region of the maze if a small square with edge length equal to 2. The coordinates can be described as a set: $\{(x,y)|x = D \mbox{ or } D-1, y=D\mbox{ or }D-1\}$ .

### 2.2 **Exploratory Visualization**

According to the interpretation rules shown above, the maze can be read from the raw data (e.g. *test_maze_01.txt*) and can be shown by using the built-in function `showmaze.py` and the statement:

```shell
python showmaze.py test_maze01.txt
```

These are the mazes' picture with fast path marked.![picture.002](picture/picture.002.jpeg)

### 2.3 **The Difficulty of a Maze**

Actually, there are various ways to measure the difficulty of a maze. But I will tend to use the following as my metric to evaluate the hardness of a maze. 

- **the ratio of minimal path length to the target region to the area of the maze ** | Metric A
  It's a metric to measure the complexity of the maze. For a maze with specific area, if the minimal path length is a large number, we may assume the maze is a complex maze. For a given path length, if the maze is larger, we may think the maze is less complex.


- **the number and the location of the openings of the target region** | Metric B 
  Actually, the target region is covered by walls with only one opening for robots to get in. If there are more openings in the target region, it tends to be easy for the robot to solve the maze. 
  And If the opening is on the left side of the target region, there are much fewer difficulties for the robot to reach the target. In fact, if not, then the robot must make a detour reach the target, which adds extra difficulties for the problem.
- **the size of the maze** | Metric C
  The size reflects the search area of the robot. It grows on a square basis. 

Although the three metrics are mutually correlated, the latter 2 are easy to measure and can give us a fast impression of the maze. The evaluation of the hardness of the mazes is shown in the following table. 

|  Metric  | Maze_01 | Maze_02 | Maze_03 |
| :------: | :-----: | :-----: | :-----: |
| Metric A | 31/144  | 42/196  | 40/256  |
| Metric B |  hard   | normal  | normal  |
| Metric C |  easy   | normal  |  hard   |
| General  | normal  | normal  |  hard   |

___

#### 2.4 **Data Preprocessing** 

The data preprocessing of this project is mainly about to check whether the maze is consistent. If there are problems in the maze, the program in `tester.py` will automatically find and report them. 

## **III. Analysis & Methodology**

### 3.1 **General Ideas for solving the maze**

There are mainly two ways to making the maze intelligent:

- ***set specific walking rules for the robot***
  tell it when and where it should turn and how long it should walk under a specific position
- ***set a heuristic algorithm (e.g A* Search or Q Learning) for the robot*** 
  the robot will automatically learning when to turn and how long it should go after a learning period

I've implemented the codes for both problems.

### 3.2 **Rule-Based Algorithm**

#### *3.2.1 General Method*

The rule-based algorithm (see in the files in `rule-based_version1`) gives the robot a set of rules for walking and gain information of the maze. Its pseudocode is shown below:

```python
Reset the Robot
running = True
while(running):	
	buildmaze(sensors) 
	# sense the maze from the given sensor distance
	rotation, movement = chooseroute()
    # choose the route for the given situation
    move(rotation,movement)
    # move the robot according to the direction
    # update the robot location
    if location in destination:
    	running == False
```

The most tricky part is to build the `move` function. I divide the function into 3 parts.

1. If there is only one opening (except for the initial position) in the grid, this is a dead end. The robot must go backward and mark the grid an 'S', meaning never go to this dead end again.
2. If there are two openings in the grid:
   1. if the previously visited grid is marked with an 'S' sign, i.e., the robot is under on a backward walking, then it's required to continue to go backward and mark current grid 'S';
   2. if the previously visited grid isn't marked with an 'S' sign, then move forward.
3. If there are three or four openings in the grid:
   1. choose the suggested direction according to the Manhattan distance difference
      ( 'u' if dy\<0, 'd' if dy \>0, 'r' if dx\<0, 'l' if dx \>0 )
   2. select the available directions from the suggested direction
      (check if there is a wall in that direction. if so, then drop that direction)
   3. **choose a specific direction (will be further described in next chapters)**
      (there are 2 different ways to do this in the first 2 versions of the robot)

#### *3.2.2 Function of the first running*

The function of the first running is used to accumulate information of the maze. In this algorithm, dead end and circling roads will be detected in the first running. Then in the second running, the meaningless road will be avoided.

### 3.3 **Q-Learning based Algorithm** 

#### *3.3.1 General Method*

The reinforcement learning algorithm may seem a good choice for the maze solving problem. it will automatically learn about the maze and make the right choice. The core idea of this algorithm is that it will choose the action with the highest score for the current state (see in the files in `q-learning_version1`).

The state is defined as the current location of the robot. And the action choice includes ['u','r','d','l']. Then the q_table is initialized:

```python
self.q_table = {} # state-action table
for ii in range(self.maze_dim):
    for jj in range(self.maze_dim):
        self.q_table[tuple([ii,jj])] = [0., 0., 0., 0.]
```

And the q_table update rule is:
$$
Q(s,a) = (1-\alpha)\times Q(s,a)+\alpha\times(r+\gamma\times\max(Q(s_{next},a_{next})))\\
\begin{align}
& s\mbox{    current state} 
& a\mbox{ current action} \\
& s_{next} \mbox{ next state} 
& a_{next} \mbox{ next action}\\
& \alpha \mbox{ update parameter} 
& \gamma \mbox{ learning rate}\\
& r  \mbox{ reward}
\end{align}
$$
Consequently, the pseudocode is:

```python
Reset the Robot
running = True
while(running):	
	buildmaze(sensors) 
	# sense the maze from the given sensor distance
    modify_qtable()
    # modify q_table in order to avoid walls
	rotation, movement = chooseroute()
    # use q_learng method to choose the route for 
    # the given sate
    move(rotation,movement)
    # move the robot according to the direction
    # update the robot location
    update_qtable()
    # update the q_table
    if location in destination:
    	running == False
```

The way to modify the q_table is:

```python
# wall avoidance
location # the current state of the robot
for direction in ['u','r','d','l']:
	if wall_in_specific_direction == True:
    	q_table[location][direction] -= 3	
```

And the ideal reward computation method is defined as:

```python
# ideal reward definition
current_location 
next_location
reward = 0
distance1 = compute_distance(current_location,target)
distance2 = compute_distance(next_location,target)
# compute the Manhattan distance of current 
# and next location to the target region
if distance1 > distance2:
    reward = 2
else:
    reward = 0
if next_location in target_region:
    reward += 10
```

However, considering the target region is a set of coordinates (refer to chap 2.1) the actual implementation to calculate reward is:

```python
# reward definition
current_location 
next_location
reward = 0
for location in target:
	distance1 = compute_distance(current_location,location)
	distance2 = compute_distance(next_location,location)
	if distance1 > distance2:
    	reward += 1
if next_location in target_region:
    reward += 10
```

The parameters are previously set: $\alpha = 0.5, \gamma = 0.5$. 

#### *3.3.2 Function of the first running*

Actually, after the first running, the robot may have learned the following things:

1. if there is wall on the specific direction
2. which is the better direction to the target

But it didn't know many other things, including how to get to the target after just one running. So there may be some problems.

___

## **IV. First Implementation, Test And Conclusion **

### 4.1 **Description of this chapter**

In this chapter, only the successful rate and the mean of $S$ will be considered to evaluate which model is better.

### 4.2 **Implementation and test for the first version of Rule-Based** 

Without considering the visited times, I add a randomness factor in the `choosedirection` function in order to avoid the circling problem. The method is:

```python
random.choice(available_direction)
# randomly choose a direction from the available direction
```

The algorithm is slow and inefficient. And the data I collected is shown below:

| test_num | maze_01 | maze_02 | maze_03 |
| :------: | :-----: | :-----: | :-----: |
|    1     | 352.57  | 140.00  |    x    |
|    2     | 180.97  |    x    |    x    |
|    3     | 381.43  |    x    |    x    |
|    4     |  79.57  | 245.07  |    x    |
|    5     | 730.50  |    x    |    x    |
|    6     |    x    |    x    |    x    |
|    7     | 122.10  | 311.13  |    x    |
|    8     |    x    | 459.40  |    x    |
|    9     | 236.10  |    x    |    x    |
|    10    | 180.37  | 202.07  |    x    |
|    11    |    x    | 572.33  |    x    |
|    12    |  95.30  |    x    | 455.07  |
|    13    |  95.17  |    x    | 821.67  |
|    14    | 477.83  |    x    |    x    |
|    15    | 272.70  |    x    |    x    |
|    16    | 240.50  | 654.93  |    x    |
|    17    | 578.83  | 413.67  |    x    |
|    18    | 101.10  | 301.13  |    x    |
|    19    |    x    |    x    | 691.20  |
|    20    |    x    | 476.47  |    x    |
|   $r$    |   75%   |   50%   |   15%   |
|  mean_s  | 275.00  | 377.62  | 655.98  |

* the x in the table means the robot failed to reach the destination within the given time
     ​** the number in the table is the score $S$ for each test 

It seems not that bad. But it's also not that good…. Let's see the next.

### 4.3 **Implementation and test for the first version of Q-Learning**

After adjusting the parameters for a long time, the result of the algorithm is still really bad:

| test_num | maze_01 | maze_02 | maze_03 |
| :------: | :-----: | :-----: | :-----: |
|    1     | 833.20  |    x    |    x    |
|    2     |    x    |    x    |    x    |
|    3     |    x    |    x    |    x    |
|    4     |    x    |    x    |    x    |
|    5     |    x    |    x    |    x    |
|    6     |    x    |    x    |    x    |
|    7     |    x    |    x    |    x    |
|    8     |    x    |    x    |    x    |
|    9     |    x    |    x    |    x    |
|    10    |    x    |    x    |    x    |
|    11    |    x    |    x    |    x    |
|    12    |    x    |    x    |    x    |
|    13    |    x    |    x    |    x    |
|    14    |    x    |    x    |    x    |
|    15    | 531.10  |    x    |    x    |
|    16    |    x    |    x    |    x    |
|    17    |    x    |    x    |    x    |
|    18    |    x    |    x    |    x    |
|    19    |    x    |    x    |    x    |
|    20    |    x    |    x    |    x    |

It almost failed in all the tests. 

And for further reference, it may be the test maze is too big for q-learning to converge in just 2 episodes. So I will try for another version by increasing the running times to test if it works on myself. It's really an important issue that when and how should we apply the q-learning algorithm?

### 4.4 **Conclusion** 

Under the game rule of the problem, the rule-based algorithm may be a better choice for the following reasons:

- it's target oriented
  *It chooses the seemingly most correct direction through all the time.*
- randomness
  *With Randomness introduced in, the robot will be able to avoid some tuning problems*

___

## **V. Improvement**

### 5.1 Rule-Based 2nd Version: Find the best direction

The randomness may not be the best choice for avoiding the circling problems. I improved the code (in 
`rule-based-version2.py`) to make it be able to select the direction which is not frequently visited. The method is:

```python
t = []
# a list storing the visited_times
for direction in available_directions:
    next_location = find_pos(direciton)
    # find the new location if the robot is 
    # moving in the selected direction
   	t.append(visited_times[next_location])
sorted_t = sorted(t)
ind = t.index(sorted_t[0])
# find the index of the direction of the least
# visited times
selected_direction = available_directions[ind]
```

And the result improves a lot!

| time | maze_01 | maze_02 | maze_03 |
| :--: | :-----: | :-----: | :-----: |
|  t1  |   130   |   157   |   121   |
|  t2  |   123   |   140   |   66    |
|  S   | 126.30  | 144.20  |  69.00  |

Since it turned from a random algorithm into a deterministic algorithm, only one test is OK.

And we can see, there is a time decrease in the t2, which proves the first running is of help in the problem.

The Route for each maze in the second run is shown below:  ![未命名.001](/Users/aqurella/Desktop/未命名/未命名.001.jpeg)

​	The direction of the small angle in each location shows the direction of movement. 

From the picture, we can see that even in the second run, there is some repeated or unnecessary movement shown in the picture.

### 5.2 Rule Based 3rd Version: Move more than 1 unit distance

In this version, I eliminated the 1-movment restriction in the code. The robot will be able to move more than 1 unit distance within a unit time interval. But due to the lack of information, I firstly let the robot randomly choose the movement distance in the available movement distances. The available movement distances and the chosen movement distance are defined as:

```python
i # the direction the robot is going to turn to
max_move_distance = sensors[i]
if max_move_distance > 3:
	available_movement_distances = range(3+1)
else:
	available_movement_distances = range(max_move_distance+1)
movement_distance = random.choice(available_movement_distances)
  # randomly choose the movement distance
```

Since it introduced randomness in, a repeated test is required.

| test_num | maze_01 | maze_02 | maze_03 |
| :------: | :-----: | :-----: | :-----: |
|    1     | 153.13  |    x    | 142.00  |
|    2     |  64.43  |  86.33  | 395.90  |
|    3     |  53.23  | 132.63  | 658.53  |
|    4     | 796.80  | 121.73  |  93.97  |
|    5     |    x    |  85.90  | 208.07  |
|    6     |    x    |    x    |  80.53  |
|    7     | 207.27  | 150.67  | 291.50  |
|    8     | 717.10  | 272.80  | 163.10  |
|    9     | 254.43  | 155.07  |  73.80  |
|    10    |  57.53  | 645.63  |  92.87  |
|    r     |   80%   |   80%   |  100%   |
|  mean_S  | 287.99  | 206.35  | 220.03  |

Actually, the performance is not better than the previous version. It may be obvious that the robot ran amuck at the maze and failed to find the best route.

Taking the the difference between t1 and t2 into consideration, the robot was tested on the maze_01:

| test_num |   1    |   2    |   3   |   4   |   5    |
| :------: | :----: | :----: | :---: | :---: | :----: |
|    t1    |   39   |  296   |  50   |  520  |  156   |
|    t2    |  484   |  566   |  71   |  456  |  301   |
|    S     | 484.27 | 574.83 | 71.63 | 472.3 | 305.17 |

Sometimes, the t2 is much larger than t1, which means the first running session is of no use in this algorithm. So the model can be seen as a bad one.

### 5.3 Rule Based 4th Version: Greedy Rational Robot

If we change the way that the robot select the moving distance as followed, the robot becomes a greedy and rational robot.

```python
available_movement_distances # defined as above
suggested_direction 
# by computing the Manhattan distance from the current location and the aimed 
# region, a set of suggested direction will be given
if robot_heading in suggested_direction:
    movement = max(available_movement_distances)
else:
    movement = 1
```

It's greedy because it moves farthest in the suggested direction. Since the algorithm becomes a deterministic algorithm, only 1 test is enough:

| test_t | maze_01 | maze_02 | maze_03 |
| :----: | :-----: | :-----: | :-----: |
|   t1   |   103   |    x    |   121   |
|   t2   |   95    |    x    |   55    |
|   s    |  97.40  |    x    |  58.00  |

The performance for maze\_01 and maze\_03 improved a lot. But it didn't successfully solve the second maze.

___

## **VI. Conclusion**

### 6.1 Comparison between different version of rule-based robot

| Version | Version Features                         | Evaluation | maze_01 | maze_02 | maze_03 |
| :-----: | :--------------------------------------- | :--------- | :-----: | :-----: | :-----: |
|    1    | randomly chooses move direction          | bad        | 275.00  | 377.62  | 655.98  |
|    2    | strategically choose the less visited direction | **good**   | 126.30  | 144.20  |  69.00  |
|    3    | randomly choose the movement distance    | normal     | 287.99  | 206.35  | 220.03  |
|    4    | strategically choose the movement distance | normal     |  97.40  |    x    |  58.00  |

The evaluation of the models in the chart is relative. It considers both $S$ and $r$. 

- Firstly, we want the robot to successfully find the way to the region ignoring the time it used. If is unable to reach the region, it will not be a good robot.
- Secondly, we want the robot to get the region in a short time. If the time is smaller, it tends to be a better robot.
- Thirdly, the difference between t1 and t2 is another factor. It shows the learning capability of the robot. It has been discussed above so I did't put it here in the table.

You can see from the table that from randomness to strategy doesn't ensure better performance of the robot. Sometimes, with randomness introduced in, the performance of the robot will be better because it can use the randomness to avoid the problems that the strategy is not able to deal with.

### 6.2 Justification of the model 

Since all kinds of complicated mazes have been tested, I just try the easiest maze without any walls:

 ![QQ20160917-0](/Users/aqurella/Desktop/QQ20160917-0.png)

And this is the performance of all the algorithms: 

| version | mean_time |
| :-----: | :-------: |
|  ver1   | 171.8732  |
|  ver2   |   14.5    |
|  ver3   |   9.96    |
|  ver4   |  43.433   |
|  verx   |  81.2754  |

​	* 'verx' means the robot with q-learning algorithm

It really reflects the truth:

- the ver1 and verx algorithm spends much time to accumulate information about the maze with low effluence. And with randomness introduced, their behavior is much more arbitrary, which leads to its poor performance.
- the ver3 algorithm is less restricted so, in this simple version of the problem , it can move as fast as possible. But due to its less restriction, it doesn't perform well in the more complicated mazes.

### 6.3 Reflection

When dealing with the maze problem, there are two main topics I am facing:

- Heuristic or Rule-based
- Random or deterministic 

My heuristic algorithm is based on the q-learning algorithm. It performed badly in this problem. I think the reason mainly comes down to the following four:

1. Choice of states
   It's a really important issue in the q-learning algorithm. I just choose the current location coordinate to mark the state. Will there be a better choice for the state? I will do some further research on my own.
2. Choice of actions
   Since I limited the movement to 1 unit length, I eliminated the possibility of faster moving. Will the performance be better if it can move more than 1 unit length?
3. Number of episodes 
   The q-learning table is updated one by one episodes. But here in the problem, there are only 2 episodes, which is much less than the commonly required times.
4. Parameter tuning
   I tried to make some tuning to the parameters but the results are not so good. I will try again after change the setting of the states and actions.

With regard to the randomness, I think it's necessary to add randomness to the problem. The reason mainly comes down to the following two:

1. It's compatible with the real situation
   In the real situation, for various kind of reasons, the action the robot really executed may not always be the same at it is required to. So with randomness introduced in, the situation is much closer to the real situation.
2. It can help solve the problems that the strategies can't deal with
   For example, the robot can easily circle in the mazes. And with randomness introduced in, it can jump out from the circle and find the new path.

### 6.4 Conclusion

Here at the end of the problem, these versions of the robot and be able to successfully solve the maze. And I will tend to use the second and fourth version of the rule-based robot to solve the real problem.

For further study, I will continue to improve the robot algorithm for better results.

Thank you very much.