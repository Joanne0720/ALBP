import random
import copy
import time
from Exploitation import ShrinkingEncircling
from Exploitation import SpiralUpdating

# d_PrecedenceTasks = [  # immediate precedence tasks of task i
#     [],
#     [1],
#     [1],
#     [1],
#     [1],
#     [1, 2],
#     [1, 3, 4, 5],
#     [1, 2, 6],
#     [1, 3, 4, 5, 7],
#     [1, 2, 6, 8],
#     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# ]
#
# d_timelist = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]
# d_nb_station = 5
# d_nb_pop = 100
# d_max_it = 10


# ----------------------------------------------------------------------------
class BalancingSolution:
    def __init__(self, TimeList, nbStations, PrecedenceTasks, taskSequence=None):
        # raw data
        if taskSequence is None:
            taskSequence = []
        self.TaskSequence = taskSequence
        self.TimeList = TimeList
        self.nbStations = nbStations
        self.PrecedenceTasks = PrecedenceTasks
        # objects
        self.CycleTime = -1
        self.TaskAssignment = []
        self.WorkLoad = []

    def randomSequence(self):
        # encoding
        self.TaskSequence = []
        M = copy.deepcopy(self.PrecedenceTasks)
        for _ in range(len(M)):
            choices = []
            for i in range(len(M)):
                if not M[i] and i not in self.TaskSequence:
                    choices.append(i)
            nxtask = random.choice(choices)
            self.TaskSequence.append(nxtask)
            for j in M:
                if nxtask + 1 in j:
                    j.remove(nxtask + 1)

    def decoding(self):
        # decoding
        init_cycletime, cycletime = max(sum(self.TimeList) // self.nbStations, max(self.TimeList)), sum(self.TimeList)
        while cycletime > init_cycletime:
            task_unassigned = self.TaskSequence[:]
            workload, potential_workload = [], []
            station_num = 0
            task_to_station = []
            while station_num < self.nbStations and task_unassigned:
                currTime, currTasks = 0, []
                while task_unassigned and currTime + self.TimeList[task_unassigned[0]] <= init_cycletime:
                    currTime += self.TimeList[task_unassigned[0]]
                    currTasks.append(task_unassigned.pop(0))
                workload.append(currTime)
                task_to_station.append(currTasks)
                station_num += 1
            if task_unassigned:
                workload[-1] += sum(self.TimeList[_] for _ in task_unassigned)
                task_to_station[-1] += task_unassigned
            for m in range(len(workload) - 1):
                potential_task = task_to_station[m + 1][0]
                potential_workload.append(workload[m] + self.TimeList[potential_task])
            cycletime, init_cycletime = max(workload), min(potential_workload)
        self.CycleTime = cycletime
        self.TaskAssignment = task_to_station
        self.WorkLoad = workload

    def printSolution(self):
        print("*************************** Solution ***************************")
        print("Assignment of Tasks to Workstations:")
        for station in range(len(self.TaskAssignment)):
            print('\tWorkstation%d: Task' % (station+1), end=" ")
            for i in self.TaskAssignment[station]:
                print(i+1, end=" ")
            print()
        print('Cycle time =', self.CycleTime)


# ----------------------------------------------------------------------------
class BalancingPopulation:
    def __init__(self, TimeList, nbStations, PrecedenceTasks, nbPop):
        self.nbPop = nbPop
        self.population = []
        for _ in range(nbPop):
            sol = BalancingSolution(TimeList,nbStations,PrecedenceTasks)
            sol.randomSequence()
            sol.decoding()
            self.population.append(sol)

    def bestSolution(self):
        best, minimum_CT = self.population[0], self.population[0].CycleTime
        for _ in self.population:
            if _.CycleTime < minimum_CT:
                best, minimum_CT = _, _.CycleTime
        return best


# ----------------------------------------------------------------------------
def WOAforALBP(TimeList,nbStations,PrecedenceTasks,nbWhales,maxIter,opt=None):
    start = time.process_time()
    # initialization
    P = BalancingPopulation(TimeList, nbStations, PrecedenceTasks, nbWhales)
    bestSol = P.bestSolution()
    # iteration
    it = 1
    while it <= maxIter:
        for sol in P.population:
            if random.random() < 0.5:
                y = bestSol if random.random() < 0.5 else random.sample(P.population, 1)[0]
                sol.TaskSequence = ShrinkingEncircling(sol.TaskSequence, y.TaskSequence, 4)
            else:
                sol.TaskSequence = SpiralUpdating(sol.TaskSequence, bestSol.TaskSequence, 4)
            sol.decoding()
        bestSol = P.bestSolution()
        if opt and bestSol.CycleTime <= opt: break
        # print('Cycle time =', bestSol.CycleTime)
        it += 1
    end = time.process_time()
    # print("CPU time of WOA for ALBP: %.3fs" % (end - start))
    return bestSol, end - start

#
# if __name__ == "__main__":
#     t=[7, 19, 15, 5, 12, 10, 8, 16, 2, 6, 21, 10, 9, 4, 14, 7, 14, 17, 10, 16, 1, 9, 25, 14, 14, 2, 10, 7, 20]
#     n=7
#     p=[[], [], [1], [3], [4], [2], [], [5, 6], [7], [9], [8], [7], [5], [10], [10, 12], [8, 14], [11, 13], [16], [15], [17], [19], [18, 21], [20, 22], [23], [1, 7], [2], [26], [23], [24, 25, 27, 28]]
#     bestSol,cputime = WOAforALBP(d_timelist, d_nb_station, d_PrecedenceTasks, d_nb_pop, d_max_it)
#     # print solution
#     bestSol.printSolution()
