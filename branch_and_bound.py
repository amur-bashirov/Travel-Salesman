import copy
from math import inf
from collections import deque

from tsp_core import Tour, SolutionStats, Timer, score_tour, Solver



def smallest_from_row(row):
    smallest = inf
    smallest_index = -inf
    for i in range(len(row)):
        if row[i] < smallest:
            smallest = row[i]
            smallest_index = i
    return smallest, smallest_index

def reducted_row(row, smallest, lower_bound):
    if smallest != 0 or smallest != inf:
        lower_bound += smallest
        for i in range(len(row)):
            if row[i] != inf:
                row[i] = row[i] - smallest
    return row, lower_bound

    
    
def smallest_from_col(edges, col_index):
    smallest = inf
    smallest_index = -1
    for i in range(len(edges)):
        if edges[i][col_index] < smallest:
            smallest = edges[i][col_index]
            smallest_index = i
    return smallest, smallest_index


def reducted_col(edges, col_index, smallest, lower_bound):
    if smallest != 0 and smallest != inf:
        lower_bound += smallest
        for i in range(len(edges)):
            if edges[i][col_index] != inf:
                edges[i][col_index] -= smallest
    return edges, lower_bound





def reduction(edges):
    graph = copy.deepcopy(edges)
    lower_bound = 0
    n_rows = len(graph)


    for i in range(n_rows):
        smallest, smallest_index = smallest_from_row(graph[i])
        graph[i], lower_bound = reducted_row(graph[i], smallest, lower_bound)




    n_cols = len(graph[0]) if n_rows > 0 else 0
    for j in range(n_cols):
        smallest, _ = smallest_from_col(graph, j)
        graph, lower_bound = reducted_col(graph, j, smallest, lower_bound)

    return graph, lower_bound


def infinity_row(outgoing_edges):
    for i in range(len(outgoing_edges)):
        outgoing_edges[i] = inf
    return outgoing_edges

def infinity_col(edges, col_index):
    for i in range(len(edges)):
        edges[i][col_index] = inf
    return edges



def choosing_edge(edges, initial_lb, chosen_branch):

    options = []
    graphs = []
    outgoing_edges = edges[chosen_branch]



    for i in range(len(outgoing_edges)):

        copy_g = copy.deepcopy(edges)
        cost = outgoing_edges[i]


        copy_g[chosen_branch] = infinity_row(copy_g[chosen_branch])
        copy_g = infinity_col(copy_g, i)

        copy_g, lower_bound = reduction(copy_g)
        lower_bound = cost + lower_bound + initial_lb

        options.append(lower_bound)
        graphs.append(copy_g)

    smallest, smallest_index = smallest_from_row(options)
    graph = graphs[smallest_index]
    graph[smallest_index][chosen_branch] = inf

    return smallest, smallest_index, graph











def main():

    graph = [
        [inf, 7, 9, inf],
        [8, inf, 10, 5],
        [6, 4, inf, 3],
        [inf, 2, 1, inf]
    ]

    graph2 = [
        [inf, 0, 2, inf],
        [0, inf, 5, 0],
        [0, 1, inf, 0],
        [inf, 1, 0, inf]
    ]


    timer = Timer(10000)


    result, lower_bound = reduction (graph)
    print(f"Actual   result: {result} and lower_bound: {lower_bound}")
    print(f"Expected result: {graph2} and lower_bound: {19}")



if __name__ == "__main__":
    main()