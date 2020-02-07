from SolutionRepresentation import encoding
from SolutionRepresentation import decoding
from Exploitation import ShrinkingEncircling

pm = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
     [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
timelist = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]
nb_station = 5
nb_pop = 2
max_it = 5
pop = []

'''initialization '''
for _ in range(nb_pop):
    s = encoding(pm)
    pop.append(decoding(s, timelist, nb_station))
''' '''
# for it in range(1, max_it+1):
print(pop[0])
print(pop[1])
new_seq = ShrinkingEncircling(pop[0]['Sequence'], pop[1]['Sequence'], 4)
new_individual = decoding(new_seq, timelist, nb_station)
print(new_individual)