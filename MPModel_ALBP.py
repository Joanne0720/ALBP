from docplex.mp.model import Model
import time


def ALBP_Model(TaskTime, nbStations, PrecedenceTasks):
    start = time.process_time()
    """Initialize the problem data"""
    TASKS = range(len(TaskTime))  # tasks set
    WORKSTATIONS = range(nbStations)  # workstations set

    '''Create model'''
    myModel = Model()

    '''Create model variables'''
    assign_task_to_station = myModel.binary_var_matrix(TASKS, WORKSTATIONS, name='Assignment')
    cycle_time = myModel.integer_var(0, name='Cycle time')

    '''Create constraints'''
    for k in WORKSTATIONS:
        myModel.add(myModel.sum(TaskTime[i] * assign_task_to_station[i, k] for i in TASKS) <= cycle_time)
    for i in TASKS:
        myModel.add(myModel.sum(assign_task_to_station[i, k] for k in WORKSTATIONS) == 1)
        for j in PrecedenceTasks[i]:
            myModel.add(myModel.sum(k * assign_task_to_station[j-1, k] for k in WORKSTATIONS) <= myModel.sum(
                kk * (assign_task_to_station[i, kk]) for kk in WORKSTATIONS))

    '''Create model objective'''
    myModel.minimize(cycle_time)

    sol = myModel.solve()
    assert sol
    end = time.process_time()
    # print("CPU time of MIP ALBP: %.3fs" % (end - start))
    myModel.cputime = end - start
    return myModel


if __name__ == "__main__":
    '''Default problem data'''
    d_TaskTime = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]  # operating time of task i
    d_nbStations = 5  # number of workstations
    d_PrecedenceTasks = [  # immediate precedence tasks of task i
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
    m = ALBP_Model(d_TaskTime, d_nbStations, d_PrecedenceTasks)
    print(m.objective_value)