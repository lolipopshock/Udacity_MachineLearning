import numpy as np
from copy import deepcopy as cp
import random

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0, 0]
        self.pre_location = [0,0]
        self.heading = 'up'
        self.maze_dim = maze_dim
        r = (maze_dim)/2
        l = (maze_dim-2)/2
        self.aim = [[r,r],[r,l],[l,r],[l,l]]
        self.near_aim = [[l-1,l],[l-1,r],[l,r+1],[r,r+1],[r+1,r],[r+1,l],[l,l-1],[r,l-1]]

        # some constants for fast convertion
        self.rot_CHO = [-90,0,90]
        self.dir_ROT = {'u':{-90:'l',0:'u',90:'r'},
                        'r':{-90:'u',0:'r',90:'d'},
                        'd':{-90:'r',0:'d',90:'l'},
                        'l':{-90:'d',0:'l',90:'u'}}
        self.dir_SEQ = ['u','r','d','l']
        self.dir_CON = {'u':{'l':(-90,1),'u':(0,1),'r':(90,1),'d':(0,-1)},
                        'r':{'u':(-90,1),'r':(0,1),'d':(90,1),'l':(0,-1)},
                        'd':{'r':(-90,1),'d':(0,1),'l':(90,1),'u':(0,-1)},
                        'l':{'d':(-90,1),'l':(0,1),'u':(90,1),'r':(0,-1)}}
        self.dir_MOV = {'u': [0, 1], 
                        'r': [1, 0],
                        'd': [0, -1],
                        'l': [-1, 0]}
        self.dir_REV = {'u': 'd', 
                        'r': 'l', 
                        'd': 'u', 
                        'l': 'r'}
        
        # q_learning stuff
        self.q_table = {} # state-action q_table
        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                self.q_table[tuple([ii,jj])] = [0., 0., 0., 0.]
        for pos in self.aim:
            self.q_table[tuple(pos)] = [10.,10.,10.,10.] 
        self.exploration_rate = 0.4
        self.alpha = 0.4
        self.gamma = 0.5
        self.reward = -1.
        
        # maze construction
        self.maze_grid = {}
        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                self.maze_grid[tuple([ii,jj])] = [-1,-1,-1,-1,0]
                # the first four element indciates the openning situation
                # 1 if opened, 0 if not, -1 means not detected
                # 1st element: up, 2nd element: right, 3rd element: down, 4th element: left
        self.maze_grid[(0,0)][2] = 0
        self.maze_grid[(0,0)][4] = 1
        
        # recording the robot's path
        self.path = list()
        self.path.append(list([cp(self.heading), cp(self.location)]))

    def reset(self):
        
        self.location = [0,0]
        self.pre_location = [0,0]
        self.heading = 'u'
        self.q_table[(0,0)] = [1.,0.,0.,0.]
        self.path = list()
        self.path.append(list([cp(self.heading), cp(self.location)]))
        self.maze_grid[(0,0)][4] = 1


    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        rotation = 0
        movement = 0

        self.build_maze(sensors)

        self.modify_qtable()

        rotation, movement,action_index = self.choose_movement()
        print self.location,self.q_table[tuple(self.location)],rotation,movement

        self.pre_location = cp(self.location)
        self.move(rotation,movement)

        self.update_qtable(action_index)

        self.path.append(list([cp(self.heading), cp(self.location)]))

        print self.pre_location,self.q_table[tuple(self.pre_location)],rotation,movement

        if self.pre_location in self.aim:
            return 'Reset','Reset'
        return rotation, movement


    def build_maze(self,sensors):

        for ii in [0,1,2]:
            dis = sensors[ii]
            ori = self.dir_ROT[self.heading][self.rot_CHO[ii]]
            xdr = self.location[0]
            ydr = self.location[1]
            d = 0
            if ori == 'u':
                while d < dis:
                    self.maze_grid[tuple([xdr,ydr+d])][0] = 1
                    d += 1
                    self.maze_grid[tuple([xdr,ydr+d])][2] = 1
                self.maze_grid[tuple([xdr,ydr+d])][0] = 0
                if ydr+d < self.maze_dim-1:
                    d += 1
                    self.maze_grid[tuple([xdr,ydr+d])][2] = 0
            elif ori == 'd':
                while -d < dis:
                    self.maze_grid[tuple([xdr,ydr+d])][2] = 1
                    d -= 1
                    self.maze_grid[tuple([xdr,ydr+d])][0] = 1
                self.maze_grid[tuple([xdr,ydr+d])][2] = 0
                if ydr+d > 0:
                    d -= 1
                    self.maze_grid[tuple([xdr,ydr+d])][0] = 0
            elif ori == 'r':
                while d < dis:
                    self.maze_grid[tuple([xdr+d,ydr])][1] = 1
                    d += 1
                    self.maze_grid[tuple([xdr+d,ydr])][3] = 1
                self.maze_grid[tuple([xdr+d,ydr])][1] = 0
                if xdr+d < self.maze_dim-1:
                    d += 1
                    self.maze_grid[tuple([xdr+d,ydr])][3] = 0

            elif ori == 'l':
                while -d < dis:
                    self.maze_grid[tuple([xdr+d,ydr])][3] = 1
                    d -= 1
                    self.maze_grid[tuple([xdr+d,ydr])][1] = 1
                self.maze_grid[tuple([xdr+d,ydr])][3] = 0
                if xdr+d > 0:
                    d -= 1
                    self.maze_grid[tuple([xdr+d,ydr])][1] = 0

    def modify_qtable(self):
        # modify the q_table so that the robot will not choose the 
        # direction leading to the wall.
        for ii in [0,1,2,3]:
            if self.maze_grid[tuple(self.location)][ii] == 0:
                self.q_table[tuple(self.location)][ii] -= 3.

    def choose_movement(self):
        # using the q_learning method, a best action is selected
        current_row = self.q_table[tuple(self.location)]
        action_score = max(current_row)
        action_index = [ii for ii in [0,1,2,3] if current_row[ii]== action_score]
        
        # eplison-greedy exploration
        if len(action_index) > 1:
            if random.random() <= self.exploration_rate:
                random.shuffle(action_index)

        # the action is selected
        action_direction = self.dir_SEQ[action_index[0]]
        # from the current heading to the specific heading
        rotation,movement = self.dir_CON[self.heading][action_direction]

        return rotation,movement,action_index[0]

    def move(self, rotation, movement):
        # rotate and move the robot for the given rotation and movement
        self.heading = self.dir_ROT[self.heading][rotation]
        if movement > 0:
            self.location[0] += movement*self.dir_MOV[self.heading][0]
            self.location[1] += movement*self.dir_MOV[self.heading][1]
        elif movement < 0:
            self.location[0] += -movement*self.dir_MOV[self.dir_REV[self.heading]][0]
            self.location[1] += -movement*self.dir_MOV[self.dir_REV[self.heading]][1]
        self.maze_grid[tuple(self.location)][4] += 1

    def update_qtable(self,action):
        special_reward = self.special_reward()
        original_val = self.q_table[tuple(self.pre_location)][action]
        estimated_val = self.gamma*max(self.q_table[tuple(self.location)]) + special_reward
        self.q_table[tuple(self.pre_location)][action] = (1-self.alpha)*original_val + self.alpha*estimated_val
        # print original_val,estimated_val

    def special_reward(self):
        if self.location in self.aim:
            return 10
        compare = []

        # direction award
        for pos in self.aim:
            dx1 = abs(self.pre_location[0] - pos[0])
            dx2 = abs(self.location[0] - pos[0])
            dy1 = abs(self.pre_location[1] - pos[1])
            dy2 = abs(self.location[1] - pos[1])
            d1 = dx1 + dy1
            d2 = dx2 + dy2
            if d1 > d2:
                compare.append(1.)
            else:
                compare.append(0.)

        reward = 0.25*sum(compare) - 0.5 * self.maze_grid[tuple(self.pre_location)][4]

        if self.location in self.near_aim:
        	if self.maze_grid[tuple(self.location)][4] >= 3:
        		reward -= 5
       	if sum(self.maze_grid[tuple(self.location)][:3]) == 1:
       		reward -= 5
        # dead end reward 
        return reward

    def path_print(self):
        plain = [];
        for ii in range(self.maze_dim):
            plain.append(['_|' for jj in range(self.maze_dim)])
        for ii in self.path:
            idx = ii[1][0]
            idy = self.maze_dim-1 - ii[1][1]
            plain[idy][idx] = ii[0] + '|'    

        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                print plain[ii][jj],
            print 
        
