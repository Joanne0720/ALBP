import random
import copy


def encoding(precedence_matrix):
    taskSequence = []
    n = len(precedence_matrix)
    M = copy.deepcopy(precedence_matrix)
    for _ in range(n):
        taskSet = []
        for j in range(n):
            if sum(_[j] for _ in M) == 0 and j not in taskSequence: taskSet.append(j)
        task = random.choice(taskSet)
        taskSequence.append(task)
        for j in range(n): M[task][j] = 0
    return taskSequence


def decoding(task_sequence, time_list, nb_station):
    init_cycletime, cycletime = sum(time_list) / nb_station, sum(time_list)
    while cycletime > init_cycletime:
        task_unassigned = task_sequence[:]
        workload, potential_workload = [], []
        station_num = 0
        task_to_station = []
        while station_num < nb_station:
            currTime, currTasks = 0, []
            while task_unassigned and currTime + time_list[task_unassigned[0]] <= init_cycletime:
                currTime += time_list[task_unassigned[0]]
                currTasks.append(task_unassigned.pop(0))
            workload.append(currTime)
            task_to_station.append(currTasks)
            station_num += 1
        if task_unassigned:
            workload[-1] += sum(time_list[_] for _ in task_unassigned)
            task_to_station[-1] += task_unassigned
        for m in range(len(workload) - 1):
            potential_task = task_to_station[m + 1][0]
            potential_workload.append(workload[m] + time_list[potential_task])
        cycletime, init_cycletime = max(workload), min(potential_workload)
    return {'Sequence': task_sequence, 'CycleTime': cycletime, 'Assignment': task_to_station, 'Workload': workload}
