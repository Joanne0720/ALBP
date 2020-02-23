import random


def loadData(filename):
    f = open(filename, 'r')
    nbTasks = int(f.readline())
    taskTime = []
    for i in range(nbTasks):
        taskTime.append(int(f.readline()))
    PrecedenceTasks = []
    for i in range(nbTasks):
        PrecedenceTasks.append([])
    while True:
        line = f.readline().replace('\n', '').split(',')
        if int(line[0]) == -1: break
        PrecedenceTasks[int(line[1])-1].append(int(line[0]))
    return taskTime, PrecedenceTasks


def randomInterval(taskTime):
    TaskTimeMin, TaskTimeMax = [], []
    for i in range(len(taskTime)):
        TaskTimeMin.append(random.randint(1, taskTime[i]))
        TaskTimeMax.append(random.randint(TaskTimeMin[i], TaskTimeMin[i]+taskTime[i]))
    return TaskTimeMin, TaskTimeMax
