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
    t = [7, 19, 15, 5, 12, 10, 8, 16, 2, 6, 21, 10, 9, 4, 14, 7, 14, 17, 10, 16, 1, 9, 25, 14, 14, 2, 10, 7, 20]
    n = 7
    p = [[], [], [1], [3], [4], [2], [], [5, 6], [7], [9], [8], [7], [5], [10], [10, 12], [8, 14], [11, 13], [16], [15],
         [17], [19], [18, 21], [20, 22], [23], [1, 7], [2], [26], [23], [24, 25, 27, 28]]
    m = ALBP_Model(t, n, p)
    print(m.cputime)
    print(m.objective_value)