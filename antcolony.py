import random
import time
from termcolor import cprint, colored
from collections import defaultdict


class Ant(object):

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.carrying_food = False
        self.history = [(self.xpos, self.ypos)]
        self.wandertime = 5


    def getweight(self, offset_x, offset_y, world):
        # Not sure whether I want to fix this or not.

        raise NotImplementedError

  #      meanweight = sum((world[self.xpos-1][self.ypos],
  #                       world[self.xpos+1][self.ypos],
  #                       world[self.xpos][self.ypos+1],
  #                       world[self.xpos][self.ypos-1]))/4

  #      weight = world[self.xpos + offset_x][self.ypos + offset_y]
  #      weight = weight - meanweight + (random.random() - 0.5)
  #      return [(offset_x, offset_y), weight]


    def update_history(self):
        self.history.append((self.xpos, self.ypos))
        if len(self.history) > 50:
            self.history = self.history[-50:]



    def wander(self):
        '''Go to a random nearby square. Except if we were just there.'''
        xnew, ynew = random.choice(((-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,1), (1,-1)))
        if (self.xpos + xnew, self.ypos + ynew) == self.history[-1]:
            xnew, ynew = xnew*-1, ynew*-1
        self.xpos, self.ypos = self.xpos + xnew, self.ypos + ynew


    def go_home(self, nests):
        '''This follows the path the ant took to the food back to the nest. Not very useful yet.'''
        if (self.xpos, self.ypos) in nests:
            self.carrying_food = False
        try:
            self.xpos, self.ypos = self.history.pop()
        except IndexError:
            self.history = [(self.xpos, self.ypos)]
        self.check_bounds()


    def follow_pheromone(self, world):
        '''If on a pheromone tile, '''
        acc = (0, (0,0))
        for cell in ((-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,1), (1,-1)):
            x = cell[0] + self.xpos
            y = cell[1] + self.xpos
            try:
                if world[x][y] > acc[0]:
                    acc = (world[x][y], (x,y))
                    self.xpos, self.ypos = acc[1]
            except IndexError:
                pass
        if acc[0] == 0 or acc[0] > 7:
            self.wander()



    def check_bounds(self, nests):
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


    def update(self, world, nests):
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
                        self.follow_pheromone(world)
            self.check_bounds(nests)
            self.update_history()
        else:
            self.go_home(nests)

def update_pheromone(world, pheromones, xpos, ypos):
    level = world[xpos][ypos] + 1
    if level > 9:
        level = 9
    world[xpos][ypos] = level
    pheromones[str((xpos, ypos))] = level
    return world, pheromones

def move_ants(world, nests, goals, ants):

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
    return grid

def drawgrid(grid):
    #print("\n"*120)
    colorgrid = []
    for row in grid:
        crow = ""
        for char in list(row):
            try:
                if int(char) == 0:
                    crow += ' '
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
    print("0123456789"*(xbound//10))
    for idx, row in enumerate(colorgrid):
        print(row + ' %d' % idx)

xbound = 70
ybound = 70
nests = ((25,25), (40,20))
goals = [(random.randrange(1,xbound-1), random.randrange(1,ybound-1)) for i in range(2)]
decayrate = 0.002
antcount = 25
pheromones = defaultdict(lambda: 0)
world = [[0 for i in range(xbound)] for j in range(ybound)]

if __name__ == '__main__':
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
        time.sleep(0.01)
        for ant in ants:
            ant.update(world, nests)
        grid = move_ants(world, nests, goals, ants)
        for ant in ants:
            world, pheromones = update_pheromone(world,pheromones, ant.xpos, ant.ypos)
        if timestep % 10 == 0:
            drawgrid(grid)

