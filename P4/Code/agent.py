import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
##fh = open('data1.txt','w')

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env,alpha = 0.5, gamma = 0.5,eplison = 0.1):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.alpha = alpha
        self.gamma = gamma
        self.eplison = eplison
        self.score = 0

        # TODO: Initialize any additional variables here 
        self.action_scheme = env.valid_actions #** Action Scheme
        self.q_table = {}
        for dr in self.action_scheme:
            for lt in ['red','green']:
                for dron in self.action_scheme:
                    for drlf in self.action_scheme:
                        for drrt in self.action_scheme:
                            self.q_table[(dr,lt,dron,drlf,drrt)] = [0, 0, 0, 0] # The corresponding value for actions in self.action_scheme


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.score = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'])

        action = self.choose_action()
        # Execute action and get reward
        reward = self.env.act(self, self.action_scheme[action])
        self.score += reward

        # TODO: Learn policy based on state, action, reward
        alpha = self.alpha # learning rate
        gamma = self.gamma # discount factor
        inputs_new = self.env.sense(self)
        state_new = (self.planner.next_waypoint(), inputs_new['light'], inputs_new['oncoming'], inputs_new['left'], inputs_new['right'])
        self.q_table[self.state][action] = (1 - alpha) * self.q_table[self.state][action] + alpha * (reward + gamma * max(self.q_table[state_new]))

    def choose_action(self):
        currentaction = self.q_table[self.state]
        if random.random() >= self.eplison:
            actionscore = max(currentaction)      
            actionset = [ii for ii in range(len(currentaction)) if currentaction[ii]==actionscore ]
            return actionset[0]
        else:
            return random.choice([0,1,2,3])



def run(alpha = 0.5, gamma = 0.5, eplison = 0.1):
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent,alpha, gamma, eplison)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0001, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    score = sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    print ''
    score.append(float(e.success)/100)
    return score
    

if __name__ == '__main__':

## Get Multiple Outputs:    
##    res = dict()
##    for a in range(3,7):
##        for g in range (3,7):
##            for e in range (1,6):
##                alpha = float(a)/10
##                gamma = float(g)/10
##                eplison = float(e)/10
##                res[(alpha,gamma,eplison)] = run(alpha,gamma,eplison)
##            
##    for (keys,values) in res.items():
##        for ii in range(101):
##            fh.write(str(keys)+' '+str(ii+1)+' ')
##            fh.write(str(values[ii]))
##            fh.write('\n')
##    fh.close()
##        
##
##    print '\n\n\n___Fina Results___\n'
    run()
