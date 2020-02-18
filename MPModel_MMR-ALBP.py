from docplex.mp.model import Model
from MPModel_ALBP import ALBP


def build_mmralbp_model(ExtremeScenarios, nbStations, PrecedenceTasks):
    m = Model(name='MMR-ALBP')
    TASKS = range(len(PrecedenceTasks))  # tasks set
    WORKSTATIONS = range(nbStations)  # workstations set
    SCENARIOS = range(len(ExtremeScenarios))  # tasks set
    # --- Create variables. ---
    assignment = m.binary_var_matrix(TASKS, WORKSTATIONS, name='Assignment')
    cycletime = m.integer_var_list(SCENARIOS, name='Cycle time')
    regret = m.integer_var(lb=0, name='Regret')
    m.assignment = assignment
    m.regret = regret
    m.cycletime = cycletime
    # --- add constraints ---
    for s in SCENARIOS:
        # Regret
        m.add_constraint(regret >= cycletime[s] - ExtremeScenarios[s]['Optimal CT'])
        # Cycle time
        m.add_constraints(
            m.sum(ExtremeScenarios[s]['Task Time'][i] * assignment[i, k] for i in TASKS) <= cycletime[s] for k in
            WORKSTATIONS)
    # Each task must be assigned.
    m.add_constraints(m.sum(assignment[i, k] for k in WORKSTATIONS) == 1 for i in TASKS)
    # # Each workstation at least 1 task
    # m.add_constraints(m.sum(assignment[i, k] for i in TASKS) >= 1 for k in WORKSTATIONS)
    # Precedence relationships
    for i in TASKS:
        m.add_constraints(
            m.sum(k * assignment[j - 1, k] for k in WORKSTATIONS) <= m.sum(
                kk * assignment[i, kk] for kk in WORKSTATIONS) for j in PrecedenceTasks[i]
        )

    # Tweak some CPLEX parameters
    # m.parameters.mip.limits.solutions = 1

    # --- set objective ---
    # objective is to minimize max regret, i.e. max(cycle time - optimal cycle time)
    m.add_kpi(m.min(cycletime), 'Cycle time of solution')
    m.minimize(regret)

    return m


def find_worst_scenario(Assignment, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks):
    TASKS = range(len(TaskTimeMin))  # tasks set
    WORKSTATIONS = range(nbStations)  # workstations set
    nbStations = len(Assignment[0])
    # find worst-case scenario of solution
    Scenarios = []
    for station in WORKSTATIONS:
        s = dict()
        # 1.calculate task time list
        temp_time = []
        for i in TASKS:
            temp_time.append(
                TaskTimeMax[i] * Assignment[i][station] + TaskTimeMin[i] * (1 - Assignment[i][station]))
        s['Task time list'] = temp_time[:]
        # 2.calculate optimal cycle time
        [s['Optimal CT'], _] = ALBP(temp_time, nbStations, PrecedenceTasks)
        # 3.calculate cycle time of solution
        s['CT'] = max(sum(temp_time[i] * Assignment[i][k] for i in TASKS) for k in WORKSTATIONS)
        # 4.calculate regret
        s['Regret'] = s['CT'] - s['Optimal CT']
        Scenarios.append(s)
    max_regret_of_solution = max(Scenarios[_]['Regret'] for _ in WORKSTATIONS)
    # find worst-case scenario: s
    for s in range(len(Scenarios)):
        if Scenarios[s]['Regret'] == max_regret_of_solution:
            break
    # The set of scenarios is updated in order to include its worst-case scenario
    print(Scenarios[s])
    return {'Task Time': Scenarios[s]['Task time list'], 'Optimal CT': Scenarios[s]['Optimal CT']}


def add_cuts(m, ExtremeScenarios, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks):
    TASKS = range(len(TaskTimeMin))  # tasks set
    WORKSTATIONS = range(nbStations)  # workstations set
    Assignment = [[0] * d_nbStations for i in TASKS]
    for i in TASKS:
        for j in range(d_nbStations):
            if m.assignment[(i, j)].solution_value == 1:
                Assignment[i][j] = 1
    s = find_worst_scenario(Assignment, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks)
    ExtremeScenarios.append(s)
    newm = build_mmralbp_model(ExtremeScenarios, d_nbStations, d_PrecedenceTasks)
    return newm


def print_solution(m):
    Matrix = m.assignment
    for i in range(len(d_TaskTimeMin)):
        for j in range(d_nbStations):
            if Matrix[(i, j)].solution_value == 1:
                print('Task %d is assigned to workstation %d' % (i, j))


# default data
d_TaskTimeMin = [81, 109, 65, 51, 92, 77, 51, 50, 43, 45, 76]  # operating time of task i
d_TaskTimeMax = [121, 159, 135, 71, 132, 107, 71, 70, 63, 65, 106]  # operating time of task i
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
[ct, _] = ALBP(d_TaskTimeMin, d_nbStations, d_PrecedenceTasks)
ExtremeScenarios = [{'Task Time': d_TaskTimeMin[:], 'Optimal CT': ct}]

m = build_mmralbp_model(ExtremeScenarios, d_nbStations, d_PrecedenceTasks)
sol = m.solve()
assert sol
m.print_solution()
for _ in range(20):
    m = add_cuts(m, ExtremeScenarios, d_TaskTimeMin, d_TaskTimeMax, d_nbStations, d_PrecedenceTasks)
    sol = m.solve()
    print(m.regret.solution_value)
# m2 = ALBP(d_TaskTimeMin,d_nbStations,d_PrecedenceTasks)
# m2.solve()
# m2.print_solution()
