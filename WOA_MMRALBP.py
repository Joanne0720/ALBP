import random
import copy
import time
from Exploitation import ShrinkingEncircling
from Exploitation import SpiralUpdating
from MPModel_ALBP import ALBP_Model
from WOA_ALBP import WOAforALBP
import DataGenerator

# Data
d_TaskTimeMin = [7, 1, 6, 8, 15, 11, 3, 12, 8, 14, 4, 8, 5, 21, 3, 8, 6, 3, 1, 4, 43, 13, 6, 25, 24, 6, 4, 17, 4, 5, 1, 2, 11, 2, 4, 9, 2, 6, 3, 1, 21, 1, 2, 4, 4]
d_TaskTimeMax = [14, 9, 12, 16, 31, 14, 15, 14, 13, 19, 8, 10, 8, 36, 8, 15, 12, 6, 1, 8, 84, 22, 33, 32, 44, 11, 6, 17, 4, 5, 7, 2, 25, 5, 5, 15, 2, 13, 3, 1, 37, 12, 3, 9, 4]
d_nbStations = 8  # number of workstations
_, d_PrecedenceTasks = DataGenerator.loadData('data/KILBRID.IN2')

# Parameters
d_nb_pop = 50
d_max_it = 50


# ----------------------------------------------------------------------------
class RobustBalancingSolution:
    def __init__(self, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks, taskSequence=None):
        # raw data
        if taskSequence is None:
            taskSequence = []
        self.TaskSequence = taskSequence
        self.TaskTimeMin = TaskTimeMin
        self.TaskTimeMax = TaskTimeMax
        self.nbStations = nbStations
        self.PrecedenceTasks = PrecedenceTasks
        # objects
        self.CycleTime = -1
        self.TaskAssignment = []
        self.WorkLoad = []
        self.MaxRegret = -1

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
        TaskSequence = self.TaskSequence
        nbStations = self.nbStations
        TimeList = self.TaskTimeMin
        init_cycletime, cycletime = max(sum(TimeList) // self.nbStations, max(TimeList)), sum(TimeList)
        while cycletime > init_cycletime:
            task_unassigned = TaskSequence[:]
            workload, potential_workload = [], []
            station_num = 0
            task_to_station = []
            while station_num < nbStations and task_unassigned:
                currTime, currTasks = 0, []
                while task_unassigned and currTime + TimeList[task_unassigned[0]] <= init_cycletime:
                    currTime += TimeList[task_unassigned[0]]
                    currTasks.append(task_unassigned.pop(0))
                workload.append(currTime)
                task_to_station.append(currTasks)
                station_num += 1
            if task_unassigned:
                workload[-1] += sum(TimeList[_] for _ in task_unassigned)
                task_to_station[-1] += task_unassigned
            for m in range(len(workload) - 1):
                potential_task = task_to_station[m + 1][0]
                potential_workload.append(workload[m] + TimeList[potential_task])
            cycletime, init_cycletime = max(workload), min(potential_workload)
        self.CycleTime = cycletime
        self.TaskAssignment = task_to_station
        self.WorkLoad = workload

    def evaluateMaxRegret(self):
        # find worst-case scenario of solution
        max_regret = 0
        for station in range(len(self.TaskAssignment)):
            s = dict()
            # 1.calculate task time list
            task_time = self.TaskTimeMin[:]
            for _ in self.TaskAssignment[station]:
                task_time[_] = self.TaskTimeMax[_]
            # 2.calculate optimal cycle time
            # OptimalCT = ALBP_Model(task_time, self.nbStations, self.PrecedenceTasks).objective_value
            sol, _ = WOAforALBP(task_time, self.nbStations, self.PrecedenceTasks, 30, 30)
            OptimalCT = sol.CycleTime
            # 3.calculate cycle time of solution
            CT = max(sum(task_time[task] for task in self.TaskAssignment[k]) for k in range(len(self.TaskAssignment)))
            # 4.calculate regret
            Regret = CT - OptimalCT
            # find worst-case scenario: s
            if Regret > max_regret:
                max_regret = Regret
        self.MaxRegret = max_regret

    def printSolution(self):
        print("*************************** Solution ***************************")
        print("Assignment of Tasks to Workstations:")
        for station in range(len(self.TaskAssignment)):
            print('\tWorkstation%d: Task' % (station + 1), end=" ")
            for i in self.TaskAssignment[station]:
                print(i + 1, end=" ")
            print()
        print('Max regret value =', self.MaxRegret)


# ----------------------------------------------------------------------------
class RobustBalancingPopulation:
    def __init__(self, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks, nbPop):
        self.nbPop = nbPop
        self.population = []
        for _ in range(nbPop):
            sol = RobustBalancingSolution(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks)
            sol.randomSequence()
            sol.decoding()
            sol.evaluateMaxRegret()
            self.population.append(sol)

    def bestSolution(self):
        best, min_MaxRegret = self.population[0], self.population[0].MaxRegret
        for _ in self.population:
            if _.MaxRegret < min_MaxRegret:
                best, min_MaxRegret = _, _.MaxRegret
        return best


# ----------------------------------------------------------------------------
def WOAforMMRALBP(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks, nbWhales, maxIter, opt=None):
    start = time.process_time()
    # initialization
    P = RobustBalancingPopulation(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks, nbWhales)
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
        if opt and bestSol.MaxRegret <= opt: break
        # print('Cycle time =', bestSol.CycleTime)
        it += 1
    end = time.process_time()
    # print("CPU time of WOA for MMRALBP: %.3fs" % (end - start))
    return bestSol, end - start


if __name__ == "__main__":
    bestSol = WOAforMMRALBP(d_TaskTimeMin, d_TaskTimeMax, d_nbStations, d_PrecedenceTasks, d_nb_pop, d_max_it)
    # print solution
    bestSol.printSolution()
