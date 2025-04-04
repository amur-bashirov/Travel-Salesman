import math
import random
from collections import deque
import copy

from tsp_core import Tour, SolutionStats, Timer, score_tour, Solver
from tsp_cuttree import CutTree
from math import inf

def random_tour(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats = []
    n_nodes_expanded = 0
    n_nodes_pruned = 0
    cut_tree = CutTree(len(edges))

    while True:
        if timer.time_out():
            return stats

        tour = random.sample(list(range(len(edges))), len(edges))
        n_nodes_expanded += 1

        cost = score_tour(tour, edges)
        if math.isinf(cost):
            n_nodes_pruned += 1
            cut_tree.cut(tour)
            continue

        if stats and cost > stats[-1].score:
            n_nodes_pruned += 1
            cut_tree.cut(tour)
            continue

        stats.append(SolutionStats(
            tour=tour,
            score=cost,
            time=timer.time(),
            max_queue_size=1,
            n_nodes_expanded=n_nodes_expanded,
            n_nodes_pruned=n_nodes_pruned,
            n_leaves_covered=cut_tree.n_leaves_cut(),
            fraction_leaves_covered=cut_tree.fraction_leaves_covered()
        ))

    if not stats:
        return [SolutionStats(
            [],
            math.inf,
            timer.time(),
            1,
            n_nodes_expanded,
            n_nodes_pruned,
            cut_tree.n_leaves_cut(),
            cut_tree.fraction_leaves_covered()
        )]

def empty_stats(timer) -> list[SolutionStats]:
    n_nodes_expanded = 0
    n_nodes_pruned = 0
    cut_tree = CutTree(0)

    return [SolutionStats(
        [],
        math.inf,
        timer.time(),
        1,
        n_nodes_expanded,
        n_nodes_pruned,
        cut_tree.n_leaves_cut(),
        cut_tree.fraction_leaves_covered()
    )]


def initial_variables(edges, stats=[]):
    if not stats:
        stats = []
    else:
        stats = copy.deepcopy(stats)
    n_nodes_expanded = 0
    n_nodes_pruned = 0
    cut_tree = CutTree(len(edges))
    return stats, n_nodes_expanded, n_nodes_pruned, cut_tree


def greedy_tour(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges)

    cities = deque(range(len(edges)))
    print(cities)

    def set_next(current_city, edges, tour, initial_city):
        outgoing_edges = edges[current_city]

        smallest = float('inf')
        smallest_index = 0
        finished = False
        index = -1
        if len(tour) != len(edges)-1:
            for edge in outgoing_edges:
                index += 1
                if  index not in tour and edge != 0 and index != initial_city:
                    stop = False
                    if edge <= smallest:
                        smallest = edge
                        smallest_index = index
        else:
            finished = True
            first = outgoing_edges[initial_city]
            smallest_index = initial_city




        next_city = smallest_index
        tour.add(smallest_index)
        return next_city, tour, finished


    while cities:

        print()
        initial_city = cities.popleft()  # Efficiently removes the first element
        print("Processing tour for city:", initial_city)  # Process the current_city

        set_tour = set()
        tour = [initial_city]
        current_city = initial_city
        while True:

            if timer.time_out():
                return stats

            next_city, set_tour, finished  = set_next(current_city, edges, set_tour, initial_city)


            if finished:

                cost = score_tour(tour, edges)
                print(f"Score: {cost}, Tour: {tour}")
                if not math.isinf(cost):
                    if not stats:
                        stats.append(SolutionStats(
                            tour=tour,
                            score=cost,
                            time=timer.time(),
                            max_queue_size=1,
                            n_nodes_expanded=n_nodes_expanded,
                            n_nodes_pruned=n_nodes_pruned,
                            n_leaves_covered=cut_tree.n_leaves_cut(),
                            fraction_leaves_covered=cut_tree.fraction_leaves_covered()
                        ))
                    elif stats[-1].score > cost:
                        stats.append(SolutionStats(
                            tour=tour,
                            score=cost,
                            time=timer.time(),
                            max_queue_size=1,
                            n_nodes_expanded=n_nodes_expanded,
                            n_nodes_pruned=n_nodes_pruned,
                            n_leaves_covered=cut_tree.n_leaves_cut(),
                            fraction_leaves_covered=cut_tree.fraction_leaves_covered()
                        ))
                break

            tour.append(next_city)
            print(f"From {current_city} to next city: {next_city}")
            current_city = next_city
            n_nodes_expanded += 1

        stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges, stats)
        continue

    if not stats:
        result = empty_stats(timer)
        return result

    print(len(cities))
    return stats




def dfs(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges)

    return []


def branch_and_bound(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges)



    # set the diagonal to inf before reducing matrices
    for i in range(len(edges)): edges[i][i] = inf  
    return []


def branch_and_bound_smart(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    cut_tree = CutTree(len(edges))

    return []


def main():
    # Example graph represented as an adjacency matrix
    graph = [
        [0, 9, inf, 8, inf],
        [inf, 0, 4, inf, 2],
        [inf, 3, 0, 4, inf],
        [inf, 6, 7, 0, 12],
        [1, inf, inf, 10, 0]
    ]

    # Initialize the timer with a 10-second limit
    timer = Timer(10000)

    # Run the greedy algorithm
    stats = greedy_tour(graph, timer)
    print(f"Stats: {stats}")



if __name__ == "__main__":
    main()