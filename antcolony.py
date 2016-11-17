import random
import pdb
import pprint
import time
from termcolor import cprint, colored
from collections import defaultdict


xbound = 70
ybound = 70
nests = ((25,25), (40,20))
badgoal = (8,3)
goodgoal = (15,18)
goals = ((8,3), (15,18), (54, 5))
goals = [(random.randrange(1,xbound-1), random.randrange(1,ybound-1)) for i in range(2)]
decayrate = 0.002
antcount = 5


class Ant(object):

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.carrying_food = False
        self.history = [(self.xpos, self.ypos)]
        self.wandertime = 5


    def getweight(self, offset_x, offset_y):

        meanweight = sum((world[self.xpos-1][self.ypos],
                         world[self.xpos+1][self.ypos],
                         world[self.xpos][self.ypos+1],
                         world[self.xpos][self.ypos-1]))/4

        weight = world[self.xpos + offset_x][self.ypos + offset_y]
        weight = weight - meanweight + (random.random() - 0.5)
        return [(offset_x, offset_y), weight]


    def update_history(self):
        self.history.append((self.xpos, self.ypos))
        if len(self.history) > 50:
            self.history = self.history[-50:]


    def update_pheromone(self):
        level = world[self.xpos][self.ypos] + 1
        if level > 9:
            level = 9
        world[self.xpos][self.ypos] = level
        pheromones[str((self.xpos, self.ypos))] = level


    def wander(self):

        xnew, ynew = random.choice(((-1,0), (1,0), (0,-1), (0,1)))
        if (self.xpos + xnew, self.ypos + ynew) == self.history[-1]:
            xnew, ynew = xnew*-1, ynew*-1
        #pdb.set_trace()
        self.xpos, self.ypos = self.xpos + xnew, self.ypos + ynew


    def go_home(self):
        if (self.xpos, self.ypos) in nests:
            self.carrying_food = False
        try:
            self.xpos, self.ypos = self.history.pop()
        except IndexError:
            self.history = [(self.xpos, self.ypos)]
        self.check_bounds()
        self.update_pheromone()


    def follow_pheromone(self):
        acc = (0, (0,0))
        for cell in ((-1,0), (1,0), (0,-1), (0,1)):
            x = cell[0] + self.xpos
            y = cell[1] + self.xpos
            try:
                if world[x][y] > acc[0]:
                    acc = (world[x][y], (x,y))
                    self.xpos, self.ypos = acc[1]
            except IndexError:
                pass
        if acc[0] == 0:
            self.wander()


    def check_bounds(self):
        if self.xpos >= xbound:
            self.xpos, self.ypos = random.choice(nests)
            self.carrying_food = False
        if self.xpos <= 0:
            self.xpos, self.ypos = random.choice(nests)
            self.carrying_food = False
        if self.ypos >= ybound:
            self.xpos, self.ypos = random.choice(nests)
            self.carrying_food = False
        if self.ypos <= 0:
            self.xpos, self.ypos = random.choice(nests)
            self.carrying_food = False


    def update(self):
        self.carrying_food = False # bypassing go_home
        if not self.carrying_food:
            if self.wandertime > 0:
                self.wandertime -= 1
                self.wander()

            else:
                if self.history[-1] == self.history[-2]:
                    self.wander()
                else:
                    if world[self.xpos][self.ypos] == 0:
                        self.wander()
                    else:
                        self.follow_pheromone()
            self.check_bounds()
            self.update_pheromone()
            if (self.xpos, self.ypos) in goals:
                self.carrying_food = True
            self.update_history()
        else:
            self.go_home()


def drawgrid():
    grid = [''.join([str(round(char)) for char in row]) for row in world]

    for nest in nests:
        row = list(grid[nest[0]])
        row[nest[1]] = '^'
        grid[nest[0]] = ''.join(row)
    for goal in goals:
        row = list(grid[goal[0]])
        row[goal[1]] = '*'
        grid[goal[0]] = ''.join(row)
    for ant in ants:
        row = list(grid[ant.xpos])
        row[ant.ypos] = '-'
        grid[ant.xpos] = ''.join(row)

    colorgrid = []
    for row in grid:
        crow = ""
        for char in list(row):
            try:
                if int(char) == 0:
                    crow += char
                elif int(char) == 1:
                    crow += colored(char, 'red')
                elif int(char) == 2:
                    crow += colored(char, 'magenta')
                elif int(char) == 3:
                    crow += colored(char, 'yellow')
                else:
                    crow += colored(char, 'blue')
            except ValueError:
                crow += colored(char, 'cyan')
        colorgrid.append(crow)
    for row in colorgrid:
        print(row)

if __name__ == '__main__':


    pheromones = defaultdict(lambda: 0)

    world = [[0 for i in range(xbound)] for j in range(ybound)]

    ants = [Ant(*random.choice(nests)) for i in range(antcount)]


    timestep = 0
    while True:
        timestep += 1
        for pos in pheromones:
            xpos, ypos = map(int, pos.replace('(', '').replace(')', '').replace(' ', '').split(','))
            if pheromones[pos] > decayrate:
                # calculate the pheromone evaporation
                world[xpos][ypos] = max(world[xpos][ypos] - decayrate*(pheromones[pos]**2), 0)

            else:
                world[xpos][ypos] = 0
        for pos in pheromones.keys():
            if pheromones[pos] == 0:
                del pheromones[pos]
#    for rowidx, row in enumerate(world):
#        for colidx, col in enumerate(row):
#            if col > decayrate:
#                world[rowidx][colidx] = col - decayrate
#            else:
#                world[rowidx][colidx] = 0
        #time.sleep(0.1)
        for ant in ants:
            ant.update()
        if timestep % 20 == 0:
            drawgrid()

