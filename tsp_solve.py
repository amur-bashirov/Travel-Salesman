import math
import random
from collections import deque
import copy
import queue

from tsp_core import Tour, SolutionStats, Timer, score_tour, Solver
from tsp_cuttree import CutTree
from math import inf

from branch_and_bound import reduction

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


def add_stats(stats,timer, n_nodes_expanded,
              n_nodes_pruned, cut_tree, string, tour,edges, bssf_cost=0):


    cost = score_tour(tour, edges)
    solution_stats = SolutionStats(
        tour=tour,
        score=cost,
        time=timer.time(),
        max_queue_size=1,
        n_nodes_expanded=n_nodes_expanded,
        n_nodes_pruned=n_nodes_pruned,
        n_leaves_covered=cut_tree.n_leaves_cut(),
        fraction_leaves_covered=cut_tree.fraction_leaves_covered()
    )


    if string == "greedy":
        cost = score_tour(tour, edges)
        print(f"Score: {cost}, Tour: {tour}")
        if not math.isinf(cost):
            if not stats:
                stats.append(solution_stats)
            elif stats[-1].score > cost:
                stats.append(solution_stats)
        return stats
    elif string == "branch and bound" or string == "dfs":
        if cost < bssf_cost:
            bssf_cost = cost
            stats.append(solution_stats)
        return stats, bssf_cost




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
                stats = add_stats(stats, timer, n_nodes_expanded,
                                  n_nodes_pruned, cut_tree, "greedy", tour, edges)
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
    bssf_cost = inf
    stack = [[0]]
    while stack and not timer.time_out():
        path = stack.pop()
        outgoing_edges = [i for i in range(len(edges)) if i not in path]
        for city in outgoing_edges:
            new_path = path + [city]

            if len(new_path) == len(edges):
                stats, bssf_cost = add_stats(stats, timer, n_nodes_expanded,
                                  n_nodes_pruned, cut_tree, "dfs", new_path, edges, bssf_cost)
                continue

            stack.append(new_path)
            n_nodes_expanded += 1


    if not stats:
        result = empty_stats(timer)
        return result
    return stats


def branch_and_bound(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges)
    max_queue_size = 1

    new_timer = Timer(20)
    stat = greedy_tour(edges, new_timer)
    if not stat:
        bssf_cost = inf
    else:
        bssf_cost = stat[-1].score
        stats.append(stat[-1])

    for i in range(len(edges)): edges[i][i] = inf
    initial_graph, initial_lb = reduction(edges)

    stack = [([0], initial_graph, initial_lb)]


    while stack and not timer.time_out():

        path, reduced_graph, lb = stack.pop()
        n_nodes_expanded += 1


        if lb >= bssf_cost:
            n_nodes_pruned += 1
            cut_tree.cut(path)
            continue


        if len(path) == len(edges):
            stats, bssf_cost = add_stats(stats, timer, n_nodes_expanded,
                n_nodes_pruned, cut_tree, "branch and bound", path, edges, bssf_cost)
            continue


        last = path[-1]
        remaining = [i for i in range(len(edges)) if i not in path]
        for nxt in remaining:


            new_graph = copy.deepcopy(reduced_graph)

            move_cost = new_graph[last][nxt]
            for j in range(len(edges)):      new_graph[last][j] = inf
            for i in range(len(edges)):      new_graph[i][nxt] = inf
            new_graph[nxt][last] = inf

            new_graph, extra_lb = reduction(new_graph)
            new_lb = lb + extra_lb + move_cost


            if new_lb < bssf_cost:
                stack.append((path + [nxt], new_graph, new_lb))
                max_queue_size = max(max_queue_size, len(stack))
            else:
                n_nodes_pruned += 1
                cut_tree.cut(path + [nxt])



    if not stats:
        result = empty_stats(timer)
        return result
    return stats




def branch_and_bound_smart(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats, n_nodes_expanded, n_nodes_pruned, cut_tree = initial_variables(edges)
    max_queue_size = 1

    new_timer = Timer(3)
    stat = greedy_tour(edges, new_timer)
    if not stat:
        bssf_cost = inf
    else:
        bssf_cost = stat[-1].score
        stats.append(stat[-1])

    for i in range(len(edges)): edges[i][i] = inf
    initial_graph, initial_lb = reduction(edges)

    iteration = ([0], initial_graph, initial_lb)

    priority_queue = queue.PriorityQueue()
    priority_queue.put((1,iteration))

    while not priority_queue.empty() and not timer.time_out():


        score, (path, reduced_graph, lb) = priority_queue.get()
        n_nodes_expanded += 1

        if lb >= bssf_cost:
            n_nodes_pruned += 1
            cut_tree.cut(path)
            continue

        if len(path) == len(edges):
            stats, bssf_cost = add_stats(stats, timer, n_nodes_expanded,
                                         n_nodes_pruned, cut_tree, "branch and bound", path, edges, bssf_cost)
            continue

        last = path[-1]
        remaining = [i for i in range(len(edges)) if i not in path]
        for nxt in remaining:

            new_graph = copy.deepcopy(reduced_graph)

            move_cost = new_graph[last][nxt]
            for j in range(len(edges)):      new_graph[last][j] = inf
            for i in range(len(edges)):      new_graph[i][nxt] = inf
            new_graph[nxt][last] = inf

            new_graph, extra_lb = reduction(new_graph)
            new_lb = lb + extra_lb + move_cost

            if new_lb < bssf_cost:
                score = new_lb - 2 * (len(path)+1)
                priority_queue.put((score,(path + [nxt], new_graph, new_lb)))
                max_queue_size = max(max_queue_size, priority_queue.qsize())
            else:
                n_nodes_pruned += 1
                cut_tree.cut(path + [nxt])

    if not stats:
        result = empty_stats(timer)
        return result
    return stats


def main():
    graph = [
        [0, 2, 3, 5],
        [2, 0, 2, 3],
        [3, 2, 0, 4],
        [5, 4, 3, 0]
    ]

    timer = Timer(10000)


    stats =  branch_and_bound_smart(graph, timer)
    if not stats:
        print("No stats")
    print(f"Stats: {stats}")



if __name__ == "__main__":
    main()