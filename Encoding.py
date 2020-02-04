import numpy as np
import random


class Solution:
    def encoding(self, pm):  # input precedence matrix
        matrix = np.array(pm)
        result = []

        for _ in range(len(matrix)):
            taskSet = []
            for i in range(len(matrix)):
                if all(matrix[:, i]) == 0 and i not in result: taskSet.append(i)
            task = random.choice(taskSet)
            result.append(task)
            for n in range(len(matrix)): matrix[task, n] = 0

        return result


p = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
      [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
r = Solution()
print(r.encoding(p))
