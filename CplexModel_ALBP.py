from docplex.mp.model import Model

# '''Initialize the problem data'''
# TaskTime = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]  # operating time of task i
# nbStations = 5                                            # number of workstations
# TASKS = range(len(TaskTime))                              # tasks set
# WORKSTATIONS = range(nbStations)                          # workstations set
# PrecedenceTasks = [                                       # immediate precedence tasks of task i
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


def ALBP(TaskTime, nbStations, PrecedenceTasks):

    """Initialize the problem data"""
    TASKS = range(len(TaskTime))  # tasks set
    WORKSTATIONS = range(nbStations)  # workstations set

    '''Create model'''
    myModel = Model()

    '''Create model variables'''
    assign_task_to_station = myModel.binary_var_matrix(TASKS, WORKSTATIONS)
    cycle_time = myModel.integer_var(0)

    '''Create constraints'''
    for k in WORKSTATIONS:
        myModel.add(sum(TaskTime[i] * assign_task_to_station[i, k] for i in TASKS) <= cycle_time)
    for i in TASKS:
        myModel.add(sum(assign_task_to_station[i, k] for k in WORKSTATIONS) == 1)
        for j in PrecedenceTasks[i]:
            myModel.add(sum(k * assign_task_to_station[j, k] for k in WORKSTATIONS) <= sum(
                kk * (assign_task_to_station[i, kk]) for kk in WORKSTATIONS))

    '''Create model objective'''
    myModel.minimize(cycle_time)

    return myModel.solve().get_objective_value()
