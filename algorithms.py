import heapq as q
import math

DIRECTIONS = [(0, 1), (0,-1), (1, 0), (-1, 0), (-1, 1), (-1, -1), (1, -1), (1, 1)]  # global

class Algorithm:
    def __init__(self, grid, type: str, start, goal):
        self.grid = grid
        self.type = type
        self.start = start
        self.goal = goal
        self.frontier = [(0, self.start)] # adding the start node to the frontier for searching
        self.path_back = {}
        self.running_cost = 0
        self.path_found = False
        self.search_failed = False

    def search(self):
        working_nodes = [] # stores the nodes that get their flags changed so I can recolor them
        if(self.frontier): # empty list evaluates to False
            _, node_coords = q.heappop(self.frontier)
            node = self.grid.nodes_dict[node_coords]
            if(not node.is_checked):
                node.is_checked = True
                working_nodes.append(node)
                children = self.get_children(node) # these children are nodes
                for child in children:
                    cost = node.dist + child.cost  # distacne to child through node
                    if(child.coords == self.goal):
                        self.path_found = True
                        child.is_path = True
                        self.path_back[child.coords] = node.coords
                        child.dist = cost # the final cost of getting here
                        return [child] #return a list with just the child node
                    elif(cost < child.dist):
                        self.path_back[child.coords] = node.coords
                        child.dist = cost
                        if(self.type is "2"): # user chose Astar
                            q.heappush(self.frontier, (cost + self.heuristic(child), child.coords))
                        else:
                            q.heappush(self.frontier, (cost, child.coords))
                        child.is_frontier = True
                        working_nodes.append(child)
        else:  # if frontier empties then we failed to find path
            print('No path exists')
            self.search_failed = True
        return working_nodes

    def get_children(self, node): # DONE: returns the children for a given node
        children = []
        for dir in DIRECTIONS:
            res = tuple(map(sum, zip(node.coords, dir)))
            if(res[0] in range(self.grid.num_rows) and res[1] in range(self.grid.num_cols)):
                child = self.grid.nodes_dict[res]
                if(not child.is_wall):
                    children.append(child)
        return children

    def get_path(self, node): # method to make list path from goal to start node
        path_list = [node.coords]
        curr_coords = node.coords
        while(curr_coords != self.start): 
            parent_coords = self.path_back[curr_coords]
            path_list.append(parent_coords)
            curr_coords = parent_coords
        return path_list

    def heuristic(self, node):
        euclid_dist = math.sqrt((node.coords[0] - self.goal[0])**2 + (node.coords[1] - self.goal[1])**2)
        return euclid_dist