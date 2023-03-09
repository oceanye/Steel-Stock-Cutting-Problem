import numpy as np

# 定义矩阵X
X = np.array([[0, 0],
              [1, 0],
              [1, 1],
              [2, 1],
              [3, 1],
              [2, 0],
              [0, 1],
              [0, 2],
              [1, 2],
              [2, 2],
              [2, 3],
              [3, 2]])

# 定义矩阵A
A = np.zeros((66, 2))
for i in range(11):
    for j in range(i + 1, 12):
        x1, y1 = X[i]
        x2, y2 = X[j]
        A[i * 6 + j - 1, :] = [y1 - y2, x2 - x1]
        A[i * 6 + j - 1, 1] *= -1
        A[i * 6 + j - 1, 2] = x1 * y2 - x2 * y1

# 定义矩阵B
B = np.linalg.lstsq(A, np.zeros((66,)))[0]

# 分类直线属于Lg1还是Lg2
Lg1 = []
Lg2 = []
for i in range(66):
    x, y = B[i]
    if np.any((X == [x, y]).all(axis=1)):
        Lg1.append([A[i, 0], A[i, 1]])
    else:
        Lg2.append([A[i, 0], A[i, 1]])

# 计算Lg1中相邻两条直线之间的距离
distances = []
for i in range(len(Lg1) - 1):
    dist = np.abs(np.linalg.norm(Lg1[i]) / np.linalg.norm(Lg1[i + 1]))
    distances.append(dist)

print("Lg1中相邻两条直线之间的距离为：", distances)
