from CplexModel_ALBP import ALBP
from docplex.cp.model import CpoModel
from docplex.cp.config import context
context.solver.agent = 'local'
context.solver.local.execfile = '/Applications/CPLEX_Studio_Community129/cpoptimizer/bin/x86-64_osx/cpoptimizer'

"""Initialize the problem data"""

TaskTimeMin = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]  # operating time of task i
TaskTimeMax = [181, 209, 165, 151, 192, 177, 151, 150, 143, 145, 176]
nbStations = 5  # number of workstations
PrecedenceTasks = [  # immediate precedence tasks of task i
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

"""Prepare the data for modeling"""

TASKS = range(len(TaskTimeMin))  # tasks set
WORKSTATIONS = range(nbStations)  # workstations set
# SCENARIOS = [0]  # scenarios set


"""Build the model"""

'''Create CPO model'''
myModel = CpoModel()
'''Assign tasks to workstation'''
WhichWorkstation = myModel.integer_var_list(len(TASKS), 0, nbStations - 1)
'''Cycle time'''
CycleTime = myModel.integer_var(max(TaskTimeMin), sum(TaskTimeMax))

# Regret = myModel.integer_var()
# TaskTimeScenario = myModel.integer_var_list(TASKS)
# OptimalCycleTime = myModel.integer_var(ub=sum(TaskTimeMax))

'''Create constraints'''
# s = 0
# for i in TASKS:
#     myModel.add_if_then(WhichWorkstation[i, 0] == 1, TaskTimeScenario[i] == TaskTimeMax[i])
#     myModel.add_if_then(WhichWorkstation[i, 0] == 0, TaskTimeScenario[i] == TaskTimeMin[i])
# temp = []
# for _ in TASKS:
#     temp.append(TaskTimeScenario[s, _])
# OptimalCycleTime[s] = ALBP(temp, nbStations, PrecedenceTasks)
# myModel.add(CycleTime == sum(TaskTimeMax[i] * WhichWorkstation[i, 1] for i in TASKS))
# myModel.add(Regret >= CycleTime)

'''ALBP constraints'''
# Add station load constraints
for k in WORKSTATIONS:
    load = 0
    for i in TASKS:
        flag = WhichWorkstation[i] == k
        load += TaskTimeMin[i]*flag
    myModel.add(load <= CycleTime)

# Add precedence constraints
for i in TASKS:
    for j in PrecedenceTasks[i]:
        myModel.add(WhichWorkstation[j] <= WhichWorkstation[i])
''''''
'''Create model objective'''
myModel.add(myModel.minimize(CycleTime))


r = myModel.solve(FailLimit=100000, TimeLimit=10)
r.print_solution()