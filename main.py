import pygame
from pygame.locals import *
import sys
import algorithms

COLORS = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 255, 0),
          'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'grey': (128, 128, 128), 'brown': (139, 115, 85)}

class Grid:
    def __init__(self):
        self.num_cols = 60
        self.num_rows = 60
        self.window_size = (900, 900)
        
        self.cell_width = self.window_size[0]//self.num_cols
        self.cell_height = self.window_size[1]//self.num_rows 
        self.start = (5, 5)
        self.goal = (self.num_rows-5, self.num_cols - 5)
        self.nodes_dict = {(i, j): Node(self, (i, j)) for i in range(self.num_rows) for j in range(self.num_cols)}
        # making sure user chooses search algorithm '1' or '2'
        tries = 10
        self.type = '' # the type of search algorithm to use
        alg_type = input('Choose Search Algorithm: UCS: 1, A*: 2\n:')
        for i in range(tries):
            try:
                if(i>0):
                    alg_type = input('Type 1 or 2 to choose an algorithm: ')
                if(alg_type not in ['1', '2']):
                    if(i == tries-1):
                        raise Exception('Too many invalid attempts')
                    continue
            except Exception as e:
                print(e)
                sys.exit()
            else:
                self.type = alg_type
                break
        self.alg = algorithms.Algorithm(self, self.type, self.start, self.goal)
    
    def build_find(self): # DONE: calls methods to draw on window (draw: gravel, walls, start, goal) (loop until user presses enter key)
        # -------------------------------------- Pygame Window Making Section --------------------------------------------------
        pygame.init()
        pygame.display.set_caption('Search Visualization')
        self.clock = pygame.time.Clock() # clock object to keep track of time to control framerate of game       
        self.window = pygame.display.set_mode(self.window_size)
        self.window.fill(COLORS['black']) # making the window background black
        self.initialize_grid()
        # ---------------------------------- End -----------------------------------------------------------------------
        print("Left-click and drag to make wall. Right-click and Drag to make gravel\
             (higher cost of traversal)\nPress 'Enter' to start search")
        start_search = False
        search_ended = False
        while True:
            for event in pygame.event.get(): # returns a list of all events that occur since init
                if(event.type == QUIT): # event occurs when user presses x to close window
                    pygame.quit()
                    sys.exit()
                elif(event.type == MOUSEMOTION and not search_ended): # event occurs when user moves mouse
                    if(pygame.mouse.get_pressed(3)[0] and not pygame.mouse.get_pressed(3)[2]): # checks if user is only left-clicking on mouse while it is moving
                        curr_node = self.get_node() # the current node user wants to color
                        if(not curr_node.is_start and not curr_node.is_goal): # check to make sure don't overwrite start or goal (flags were set on lines 49,51)
                            curr_node.clear_node() 
                            curr_node.is_wall = True
                            curr_node.cost =  -1 # cost of travelling through wall not positive
                            self.draw(curr_node)
                    elif(pygame.mouse.get_pressed(3)[2] and not pygame.mouse.get_pressed(3)[0]):
                        curr_node = self.get_node()
                        if(not curr_node.is_start and not curr_node.is_goal):
                            curr_node.clear_node()
                            curr_node.is_gravel = True
                            curr_node.cost = 5 # higher cost for travelling through gravel
                            self.draw(curr_node)
                elif(event.type == KEYDOWN):
                    if(event.key == K_RETURN):
                        start_search = True
            if(start_search):
                self.find_path()
                start_search = False
                search_ended = True

    def initialize_grid(self): # DONE: helper method to quickly initialize the white grid
        for node in self.nodes_dict.values():
            if(node.coords == self.start):
                node.is_start = True
                node.dist = 0 # distance from start to start is zero
            elif(node.coords == self.goal):
                node.is_goal = True
            node.draw(self.window) # using the node draw method so I can manually update the window here after all the rectangles have been drawn
        pygame.display.update()
    
    def draw(self, node):
        node.draw(self.window)
        pygame.display.update()

    def find_path(self):  # initializes algorithm of choice and finds the path/drawing with methods
        # if the algorithm fails to find a path in the search method it returns and I have to pygame.quit()/sys.exit() here
        while(not self.alg.search_failed):
            recolor_list = self.alg.search()
            if(self.alg.path_found): # Drawing the path back to the start node
                goal_node = recolor_list[0]
                path = self.alg.get_path(goal_node) # list of coords leading from goal to start
                for path_coords in path:
                    node = self.nodes_dict[path_coords]
                    node.is_path = True
                    self.draw(node)
                return
            for node in recolor_list:
                self.draw(node)

    def get_node(self): # DONE: gets the node whose cell in the window is being clicked on by the mouse
        pos = pygame.mouse.get_pos()
        cell_coords = Node.get_cell_coords(pos, self)
        return self.nodes_dict[cell_coords]

class Node:
    def __init__(self, grid, coords):
        self.grid = grid
        self.coords = (coords[0], coords[1]) # the node's coordinates (0-74)
        self.cost = 1 # cost of travelling through default white nodes
        self.dist = 1000 # sys.maxsize # the current shortest distance of a path to this node

        self.is_start = False # COLOR: yellow
        self.is_goal = False # COLOR: red
        self.is_wall = False # node is a wall (can't pass through) COLOR: black
        self.is_gravel = False # node is gravel higher cost color: COLOR: grey
        self.is_frontier = False # node is frontier node (in the pq) COLOR: blue
        self.is_checked = False # node is checked don't queue it again as the quickest path to it has been found COLOR: green
        self.is_path = False
        pass

    def draw(self, window):
        color = COLORS['white']
        if(self.is_wall):
            color = COLORS['black']
        else: # order here matters
            if(self.is_start):
                color = COLORS['yellow']
            elif(self.is_goal):
                color = COLORS['red']
            elif(self.is_gravel):
                color = COLORS['grey']
            if(self.is_frontier):
                color = COLORS['blue']
            if(self.is_checked):
                color = COLORS['green']
            if(self.is_path):
                color = COLORS['yellow']
                if(self.is_gravel):
                    color = COLORS['brown']
        pixel_coords = Node.get_pixel_coords(self.coords, self.grid)
        cell = pygame.Rect(pixel_coords[0], pixel_coords[1], self.grid.cell_width-1, self.grid.cell_height-1)
        pygame.draw.rect(window, color, cell)

    def clear_node(self): # DONE: helper method to clear node flags (can't have is_wall = True and is_gravel = True)
        self.is_wall = False
        self.is_gravel = False

    # x, y may have to be flipped because the cell coordinates (0-74) are (row, column) but the pixels (0-899) (column, row)
    @staticmethod
    def get_pixel_coords(coords, grid):  # DONE: method to get top left pixel coords for each cell for coloring
        x = coords[1]
        y = coords[0]
        return (x * grid.cell_width, y * grid.cell_height)
    @staticmethod
    def get_cell_coords(pos, grid): #DONE: method to get the cell coordinates (0,74) given the position of the mouse to see what cell to color
        pix_x_pos = pos[1]
        pix_y_pos = pos[0]
        return (pix_x_pos//grid.cell_width, pix_y_pos//grid.cell_height)

def main():
    grid = Grid()
    grid.build_find()

if __name__ == '__main__':
    main()