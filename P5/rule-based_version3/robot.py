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
        self.heading = 'u'
        self.maze_dim = maze_dim
        self.first_turn = False

        self.dir_NUM = ['u','r','d','l']
        self.dir_ROT = {'u':{-90:'l',0:'u',90:'r'},
                        'r':{-90:'u',0:'r',90:'d'},
                        'd':{-90:'r',0:'d',90:'l'},
                        'l':{-90:'d',0:'l',90:'u'}}
        self.dir_DEG = {'u':{'l':-90,'u':0,'r':90},
                        'r':{'u':-90,'r':0,'d':90},
                        'd':{'r':-90,'d':0,'l':90},
                        'l':{'d':-90,'l':0,'u':90}}
        self.dir_MOV = {'u': [0, 1], 
                        'r': [1, 0],
                        'd': [0, -1],
                        'l': [-1, 0]}
        self.rot_CHO = [-90,0,90]
        self.dir_REV = {'u': 'd', 
                        'r': 'l', 
                        'd': 'u', 
                        'l': 'r'}



        self.maze_grid = dict()
        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                self.maze_grid[tuple([ii,jj])] = [-1,-1,-1,-1,'N',0]
                # the first four element indciates the openning situation
                # 1 if opened, 0 if not, -1 means not detected
                # 1st element: up, 2nd element: right, 3rd element: down, 4th element: left
                # the fifth element indicates the route situation
                # N --- have NOT be detected
                # H --- have be detected in one direction
                # Y --- have be detected in both direction
                # S --- indicates a dead end in the path
                # the sixth element indicates the visited times
        self.maze_grid[(0,0)][2] = 0        
        self.maze_grid[(0,0)][5] = 1

        self.path = list()
        self.path.append(list([cp(self.heading), cp(self.location)]))

    def reset(self):

        self.path = list()
        self.path.append(list([cp(self.heading), cp(self.location)]))

        self.location = [0,0]
        self.heading = 'u'
        self.first_turn = False

        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                self.maze_grid[tuple([ii,jj])][5] = 0
        #self.maze_grid[(0,0)][4] = 'N'
        #self.maze_grid[(0,1)][4] = 'N'
        #self.maze_grid[(0,2)][4] = 'N'
        #self.maze_grid[(0,3)][4] = 'N'
        #self.maze_grid[(1,3)][4] = 'N'

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

        self.buildmaze(sensors)
                
        rotation, movement = self.chooseroute(sensors)



        self.move(rotation,movement)
        
        self.path.append([cp(self.heading), cp(self.location)])

        if rotation==0 and movement==0:
            return 'Reset','Reset'
        return rotation, movement

    def buildmaze(self, sensors):
        if self.maze_grid[tuple(self.location)][4] == 'Y':
            pass
        self.maze_grid[tuple(self.location)][4] == 'Y'
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

    def chooseroute(self,sensors):
        current_loc = self.maze_grid[tuple(self.location)][:4]
        openning_num = sum(self.maze_grid[tuple(self.location)][:4])
        if len(self.path)<= 1:
            # x =raw_input('!')
            return 0,1
        if openning_num == 1:
            rotation = 0
            movement = -1
            self.maze_grid[tuple(self.location)][4] = 'S'
        elif openning_num == 2:
            movement = 1
            if current_loc in [[1,0,1,0],[0,1,0,1]]:
                rotation = 0
            elif current_loc == [1,1,0,0]:
                if self.heading in ['l','u']:
                    rotation = 90  # clockwise
                elif self.heading in ['d','r']:
                    rotation = -90 # counterclockwise
            elif current_loc == [0,1,1,0]:
                if self.heading in ['u','r']:
                    rotation = 90 
                elif self.heading in ['l','d']:
                    rotation = -90
            elif current_loc == [0,0,1,1]:
                if self.heading in ['r','d']:
                    rotation = 90
                elif self.heading in ['u','l']:
                    rotation = -90
            elif current_loc == [1,0,0,1]:
                if self.heading in ['d','l']:
                    rotation = 90
                elif self.heading in ['r','u']:
                    rotation = -90
            else:
                print current_loc,
                print self.location
                x = raw_input('???')

            if self.first_turn == True:
                if self.maze_grid[tuple(self.path[-2][1])][4] == 'S':
                    # x = raw_input('x2')
                    rotation = -rotation
                    movement = -movement
                    self.maze_grid[tuple(self.location)][4] = 'S'
                elif self.maze_grid[tuple(self.location)][4] == 'S':
                    rotation = 0
                    movement = -movement
                # print self.location,self.maze_grid[tuple(self.location)]
                # x = raw_input('x2')
        elif openning_num in [3,4]:
            self.first_turn = True
            rotation, movement = self.choosedirection()
        else:
            print current_loc
            print self.location
            x = raw_input('???')

        if movement >0:
            mov_CHO = sensors[self.rot_CHO.index(rotation)]
            far_mov = mov_CHO if mov_CHO<=3 else 3
            movement = random.choice(range(1,far_mov+1))
        return rotation, movement

    def choosedirection(self):
        suggested_dir = list()
        mid_l = (self.maze_dim-1)/2
        mid_r = (self.maze_dim+1)/2
        loc_x = self.location[0]
        loc_y = self.location[1]
        rot = 0
        mov = 0

        if loc_x >= 0 and loc_x < mid_l:
            suggested_dir.append('r')
        elif loc_x > mid_r and loc_x <= self.maze_dim-1:
            suggested_dir.append('l')

        if loc_y >= 0 and loc_y < mid_l:
            suggested_dir.append('u')
        elif loc_y > mid_r and loc_y <= self.maze_dim-1:
            suggested_dir.append('d')

        if len(suggested_dir) == 0:
            return rot,mov
        else:
            avaliable_dir = self.dir_ROT[self.heading].values()
            compatible_dir = [dx for dx in suggested_dir if dx in avaliable_dir]
            final_dir = compatible_dir + list(set(avaliable_dir)-set(compatible_dir))
            dir_times = []
            del_list = []
            #print final_dir,
            for ii in final_dir:
                #print ii
                rot = self.dir_DEG[self.heading][ii]
                if self.maze_grid[tuple(self.location)][self.dir_NUM.index(self.dir_ROT[self.heading][rot])] == 0:
                    # blocked by wall
                    del_list.append(ii)
                    continue
                new_loc = self.find_pos(cp(self.location),cp(self.heading),rot,1)

                if self.maze_grid[tuple(new_loc)][4] == 'S':
                    # print 'pass2',new_loc,rot
                    del_list.append(ii)
                    continue
                dir_times.append(self.maze_grid[tuple(new_loc)][5])
            final_dir = [ii for ii in final_dir if ii not in del_list]
            #print final_dir,dir_times,
            temp_times = sorted(dir_times)
            final_dir = final_dir[dir_times.index(temp_times[0])]
            #print final_dir

            rot = self.dir_DEG[self.heading][final_dir]
            mov = 1
        return rot,mov

    def move(self, rotation, movement):
        # rotate and move the robot for the given rotation and movement
        self.heading = self.dir_ROT[self.heading][rotation]
        if movement > 0:
            self.location[0] += movement*self.dir_MOV[self.heading][0]
            self.location[1] += movement*self.dir_MOV[self.heading][1]
        elif movement < 0:
            self.location[0] += -movement*self.dir_MOV[self.dir_REV[self.heading]][0]
            self.location[1] += -movement*self.dir_MOV[self.dir_REV[self.heading]][1]
        self.maze_grid[tuple(self.location)][5] += 1

    def find_pos(self,location,heading,rotation,movement):
        new_heading = self.dir_ROT[heading][rotation]
        if movement > 0:
            location[0] += movement*self.dir_MOV[new_heading][0]
            location[1] += movement*self.dir_MOV[new_heading][1]
        elif movement < 0:
            location[0] += -movement*self.dir_MOV[self.dir_REV[new_heading]][0]
            location[1] += -movement*self.dir_MOV[self.dir_REV[new_heading]][1]
        return location

    def path_print(self):
        plain = [];
        cov = {'u':'^','d':'v','l':'<','r':'>'}
        for ii in range(self.maze_dim):
            plain.append(['_|' for jj in range(self.maze_dim)])
        for ii in self.path:
            idx = ii[1][0]
            idy = self.maze_dim-1 - ii[1][1]
            plain[idy][idx] = cov[ii[0]] + '|'    

        for ii in range(self.maze_dim):
            for jj in range(self.maze_dim):
                print plain[ii][jj],
            print 
    
