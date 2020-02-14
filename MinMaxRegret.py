def findCriticalStation(solution, time_interval):
    ass = solution['Assignment'][:]
    scenario = []  # tasks to be set to upper time
    for criticalStation in range(len(solution['Workload'])):
        workload = []
        for m in range(len(solution['Workload'])):
            t = sum(time_interval[_][0] for _ in ass[m]) if m != criticalStation else sum(
                time_interval[_][1] for _ in ass[m])
            workload.append(t)
        if workload.index(max(workload)) == criticalStation:
            scenario.append({max(workload): ass[criticalStation]})
    return scenario

