from docplex.mp.model import Model
from MPModel_ALBP import ALBP_Model
import time


# ----------------------------------------------------------------------------
# Prepare the data for modeling
# ----------------------------------------------------------------------------
def load_data(mdl, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks):
    # raw data
    mdl.TaskTimeMin = TaskTimeMin
    mdl.TaskTimeMax = TaskTimeMax
    mdl.nbStations = nbStations
    mdl.PrecedenceTasks = PrecedenceTasks
    # transactional data
    mdl.TASKS = range(len(PrecedenceTasks))
    mdl.WORKSTATIONS = range(nbStations)


def setup_variables(mdl):
    # --- Create variables. ---
    # the dictionary of decision variables, one variable for each assignment
    mdl.assignment = mdl.binary_var_matrix(mdl.TASKS, mdl.WORKSTATIONS, name='Assignment')
    mdl.regret = mdl.integer_var(lb=0, name='Regret')


def setup_initial_constraints(mdl):
    assignment = mdl.assignment
    TASKS, WORKSTATIONS, PrecedenceTasks = mdl.TASKS, mdl.WORKSTATIONS, mdl.PrecedenceTasks
    # --- Add constraints ---
    # Each task must be assigned.
    mdl.add_constraints(mdl.sum(assignment[i, k] for k in WORKSTATIONS) == 1 for i in TASKS)
    # Each workstation at least 1 task
    mdl.add_constraints(mdl.sum(assignment[i, k] for i in TASKS) >= 1 for k in WORKSTATIONS)
    # Precedence relationships
    for i in TASKS:
        mdl.add_constraints(
            mdl.sum(k * assignment[j - 1, k] for k in WORKSTATIONS) <= mdl.sum(
                kk * assignment[i, kk] for kk in WORKSTATIONS) for j in PrecedenceTasks[i]
        )


def setup_objective(mdl):
    # --- set objective ---
    # objective is to minimize max regret, i.e. max(cycle time - optimal cycle time)
    mdl.minimize(mdl.regret)


def add_cuts(mdl):
    TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks = mdl.TaskTimeMin, mdl.TaskTimeMax, mdl.nbStations, mdl.PrecedenceTasks
    TASKS, WORKSTATIONS = mdl.TASKS, mdl.WORKSTATIONS
    A = [[0] * nbStations for _ in TASKS]
    for i in TASKS:
        for j in WORKSTATIONS:
            if mdl.assignment[(i, j)].solution_value == 1:
                A[i][j] = 1
    # find worst-case scenario of solution
    max_regret, worst_case = 0, {}
    for station in WORKSTATIONS:
        s = dict()
        # 1.calculate task time list
        task_time = []
        for i in TASKS:
            task_time.append(TaskTimeMax[i] * A[i][station] + TaskTimeMin[i] * (1 - A[i][station]))
        s['Task time'] = task_time[:]
        # 2.calculate optimal cycle time
        s['Optimal CT'] = ALBP_Model(task_time, nbStations, PrecedenceTasks).objective_value
        # 3.calculate cycle time of solution
        CT_ = max(sum(task_time[i] * A[i][k] for i in TASKS) for k in WORKSTATIONS)
        # 4.calculate regret
        Regret_ = CT_ - s['Optimal CT']
        # find worst-case scenario: s
        if Regret_ > max_regret:
            worst_case, max_regret = s, Regret_
    # print(worst_case)
    # The set of scenarios is updated in order to include its worst-case scenario
    mdl.add_constraints(
        mdl.regret >= mdl.sum(worst_case['Task time'][i] * mdl.assignment[i, k] for i in TASKS) -
        worst_case['Optimal CT'] for k in WORKSTATIONS)
    return worst_case


def solve(mdl):
    start = time.process_time()
    # mdl.parameters.mip.limits.solutions = 1
    sol = mdl.solve()
    assert sol
    cut, newcut, nbCuts = {}, add_cuts(mdl), 1
    while newcut != cut:
        # print(mdl.objective_value)
        sol = mdl.solve()
        assert sol
        cut, newcut = newcut, add_cuts(mdl)
        nbCuts += 1
    end = time.process_time()
    print("CPU time for MIP MMRALBP: %.3fs" % (end - start))
    print("#cuts = %d" % (nbCuts-1))


def print_information(mdl):
    print("#tasks = %d" % len(mdl.PrecedenceTasks))
    print("#workstations = %d" % mdl.nbStations)


def print_solution(mdl):
    print("*************************** Solution ***************************")
    print("Assignment of Tasks to Workstations:")
    for i in mdl.TASKS:
        for j in mdl.WORKSTATIONS:
            if mdl.assignment[i, j].solution_value == 1:
                print('\tTask %d: workstation %d' % (i, j))
    print('Max regret = %d' % mdl.objective_value)


# ----------------------------------------------------------------------------
# Build the model
# ----------------------------------------------------------------------------
def build_mmralbp_model(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks):
    mdl = Model(name='MMR-ALBP')
    load_data(mdl, TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks)
    setup_variables(mdl)
    setup_initial_constraints(mdl)
    setup_objective(mdl)
    return mdl


def run(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks):
    model = build_mmralbp_model(TaskTimeMin, TaskTimeMax, nbStations, PrecedenceTasks)
    solve(model)
    return model

# ----------------------------------------------------------------------------
# Solve the model and display the result
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # ----------------------------------------------------------------------------
    # Default data
    # ----------------------------------------------------------------------------
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
    # Build model
    model = build_mmralbp_model(d_TaskTimeMin, d_TaskTimeMax, d_nbStations, d_PrecedenceTasks)
    print_information(model)
    # Solve the model and print solution
    solve(model)
    print_solution(model)


