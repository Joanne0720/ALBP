import random
import copy
from SolutionRepresentation import encoding
from SolutionRepresentation import decoding
from Exploitation import ShrinkingEncircling
from Exploitation import SpiralUpdating

pm = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
      [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
timelist = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]
nb_station = 5
nb_pop = 100
max_it = 10
#  s = [0, 3, 2, 7, 6, 4, 1, 8, 9, 5, 10]


def optimal(population):
    optimal_value = min(_['CycleTime'] for _ in population)
    for _ in population:
        if _['CycleTime'] == optimal_value: return _


'''initialization '''
pop = []
for _ in range(nb_pop):
    s = encoding(pm)
    pop.append(decoding(s, timelist, nb_station))
best_solution = optimal(pop)
print(best_solution)
''' '''
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
        new_x = decoding(new_x_seq, timelist, nb_station)
        pop[i] = copy.deepcopy(new_x)
    best_solution = optimal(pop)
    it += 1
print(best_solution)
