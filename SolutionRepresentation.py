import numpy as np
import random


def encoding(precedence_matrix):
    matrix = np.array(precedence_matrix)
    result = []
    for _ in range(len(matrix)):
        taskSet = []
        for i in range(len(matrix)):
            if all(matrix[i, :]) == 0 and i not in result: taskSet.append(i)
        task = random.choice(taskSet)
        result.append(task)
        for n in range(len(matrix)): matrix[n, task] = 0
    return result


def decoding(task_sequence, time_list, nb_station):
    init_cycletime, cycletime = sum(time_list) / nb_station, sum(time_list)
    while cycletime > init_cycletime:
        start = 0
        assignment_task = {}
        workload = []
        potential_workload = []
        for m in range(nb_station - 1):
            end, stationTime = start, time_list[start]
            while stationTime <= init_cycletime:
                end += 1
                stationTime += time_list[task_sequence[end]]
            assignment_task[m] = task_sequence[start:end]
            workload.append(stationTime - time_list[task_sequence[end]])
            start = end
        assignment_task[m+1] = task_sequence[start:]
        workload.append(sum(time_list[_] for _ in assignment_task[m+1]))
        for m in range(len(workload) - 1):
            potential_task = assignment_task[m+1][0]
            potential_workload.append(workload[m] + time_list[potential_task])
        cycletime, init_cycletime = max(workload), min(potential_workload)
    return cycletime, assignment_task



