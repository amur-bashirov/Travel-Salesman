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

def reducted_row(row, smallest):
    if smallest != 0 or smallest != inf:
        for i in range(len(row)):
            if row[i] != inf:
                row[i] = row[i] - smallest
    return row

    
    
def smallest_from_col(edges, col_index):
    smallest = inf
    smallest_index = -1
    for i in range(len(edges)):
        if edges[i][col_index] < smallest:
            smallest = edges[i][col_index]
            smallest_index = i
    return smallest, smallest_index


def reducted_col(edges, col_index, smallest):
    if smallest != 0 and smallest != inf:
        for i in range(len(edges)):
            if edges[i][col_index] != inf:
                edges[i][col_index] -= smallest
    return edges





def reduction(edges):
    graph = copy.deepcopy(edges)
    lower_bound = 0
    n_rows = len(graph)


    for i in range(n_rows):
        smallest, smallest_index = smallest_from_row(graph[i])
        graph[i] = reducted_row(graph[i], smallest)
        if smallest != inf:
            lower_bound += smallest




    n_cols = len(graph[0]) if n_rows > 0 else 0
    for j in range(n_cols):
        smallest, _ = smallest_from_col(graph, j)
        graph = reducted_col(graph, j, smallest)
        if smallest != inf:
            lower_bound += smallest

    return graph, lower_bound


# def infinity_row(outgoing_edges):
#     for i in range(len(outgoing_edges)):
#         outgoing_edges[i] = inf
#     return outgoing_edges
#
# def infinity_col(edges, col_index):
#     for i in range(len(edges)):
#         edges[i][col_index] = inf
#     return edges



# def choosing_edge(edges, initial_lb, chosen_branch, ignored_branches):
#
#     options = []
#     graphs = []
#     outgoing_edges = edges[chosen_branch]
#
#
#
#     for i in range(len(outgoing_edges)):
#
#         if chosen_branch in ignored_branches:
#             if i in ignored_branches[chosen_branch]:
#                 continue
#
#         copy_g = copy.deepcopy(edges)
#         cost = outgoing_edges[i]
#
#
#         copy_g[chosen_branch] = infinity_row(copy_g[chosen_branch])
#         copy_g = infinity_col(copy_g, i)
#
#         copy_g, lower_bound = reduction(copy_g)
#         lower_bound = cost + lower_bound + initial_lb
#
#         options.append(lower_bound)
#         graphs.append(copy_g)
#
#     smallest, smallest_index = smallest_from_row(options)
#     graph = graphs[smallest_index]
#     graph[smallest_index][chosen_branch] = inf
#
#     return smallest, smallest_index, graph











def main():

    graph = [
        [inf, inf, inf, inf],
        [0, inf, inf, 10],
        [inf, inf, inf, inf],
        [6, inf, inf, inf]
    ]

    graph2 = [
        [inf, inf, inf, inf],
        [0, inf, inf, 0],
        [inf, inf, inf, inf],
        [0, inf, inf, inf]
    ]


    timer = Timer(10000)


    result, lower_bound = reduction (graph)
    print(f"Actual   result: {result} and lower_bound: {lower_bound}")
    print(f"Expected result: {graph2} and lower_bound: {16}")



if __name__ == "__main__":
    main()