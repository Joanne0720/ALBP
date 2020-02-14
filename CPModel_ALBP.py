from docplex.cp.model import CpoModel
from docplex.cp.config import context

context.solver.agent = 'local'
context.solver.local.execfile = '/Applications/CPLEX_Studio_Community129/cpoptimizer/bin/x86-64_osx/cpoptimizer'

""" Initialize the problem data """
# operating time of task i
TaskTime = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]

# number of workstations
nbStations = 5

# immediate precedence tasks of task i
PrecedenceTasks = [
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
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

""" Prepare the data for modeling """
# tasks set
TASKS = range(len(TaskTime))
# workstations set
WORKSTATIONS = range(nbStations)

""" Build the model """
# Create CPO model
myModel = CpoModel()

# Assign tasks to workstation
WhichWorkstation = myModel.integer_var_list(len(TASKS), 0, nbStations - 1)

# Cycle time
CycleTime = myModel.integer_var(max(TaskTime) / nbStations, sum(TaskTime))

# Add station load constraints
for k in WORKSTATIONS:
    load = 0
    for i in TASKS:
        flag = WhichWorkstation[i] == k
        load += TaskTime[i] * flag
    myModel.add(load <= CycleTime)

# Add precedence constraints
for i in TASKS:
    for j in PrecedenceTasks[i]:
        myModel.add(WhichWorkstation[j] <= WhichWorkstation[i])

# Create model objective
myModel.add(myModel.minimize(CycleTime))

""" Solve model """
r = myModel.solve(FailLimit=100000, TimeLimit=10)

""" Print solution """
r.print_solution()
