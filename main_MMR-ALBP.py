import random
import copy
from SolutionRepresentation import encoding
from SolutionRepresentation import decoding
from MinMaxRegret import findCriticalStation
from Exploitation import ShrinkingEncircling
from Exploitation import SpiralUpdating
from CplexModel_ALBP import ALBP

# Data
PrecedenceTasks = [                                       # immediate precedence tasks of task i
    [],
    [1],
    [1],
    [1],
    [1],
    [1, 2],
    [1, 3, 4, 5],
    [1, 2, 6],
    [1, 3, 4, 5, 7],
    [1, 2, 6, 8],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
]
pm = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
      [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
time_interval = [[81, 91], [109, 119], [65, 75], [51, 61], [92, 102], [77, 87],
                 [51, 61], [50, 60], [43, 53], [45, 55], [76, 86]]
init_timelist = []
for _ in time_interval:
    init_timelist.append(_[0])
nb_station = 5
nb_pop = 10
max_it = 10


def evaluate_maxregret(scenarios):
    max_regret = 0
    for dic in scenarios:
        criticalTasks = list(dic.values())[:]
        scenario_time = []
        for tsk in range(len(pm)):
            scenario_time.append(time_interval[tsk][0] if tsk not in criticalTasks else time_interval[tsk][1])
        scenario_bestct = ALBP(scenario_time, nb_station, PrecedenceTasks)
        scenario_regret = list(dic.keys())[0] - scenario_bestct
        max_regret = max(scenario_regret, scenario_regret)
    return max_regret


def optimal(population):
    optimal_value = min(_['MaxRegret'] for _ in population)
    for _ in population:
        if _['MaxRegret'] == optimal_value: return _


'''initialization '''
pop = []
for _ in range(nb_pop):
    solution = decoding(encoding(pm), init_timelist, nb_station)
    scnrs = findCriticalStation(solution, time_interval)
    solution['MaxRegret'] = evaluate_maxregret(scnrs)
    pop.append(solution)
best_solution = optimal(pop)
print(best_solution)
''''''
it = 1
while it <= max_it:
    for i in range(nb_pop):
        if random.random() < 0.5:
            if random.random() < 0.5:
                new_x_seq = ShrinkingEncircling(pop[i]['Sequence'], best_solution['Sequence'], 4)
            else:
                y = random.sample(pop, 1)
                new_x_seq = ShrinkingEncircling(pop[i]['Sequence'], y[0]['Sequence'], 4)
        else:
            new_x_seq = SpiralUpdating(pop[i]['Sequence'], best_solution['Sequence'], 4)
        new_x = decoding(new_x_seq, init_timelist, nb_station)
        x_scnrs = findCriticalStation(new_x, time_interval)
        new_x['MaxRegret'] = evaluate_maxregret(x_scnrs)
        pop[i] = copy.deepcopy(new_x)
    best_solution = optimal(pop)
    it += 1
print(best_solution)

