import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

# 随机生成多边形
def generate_polygons(num, min_size, max_size):
    polygons = []
    for i in range(num):
        size = np.random.uniform(min_size, max_size)
        x = np.random.uniform(0, 1 - size)
        y = np.random.uniform(0, 1 - size)
        vertices = np.array([(x, y), (x + size, y), (x + size, y + size), (x, y + size)])
        polygons.append(Polygon(vertices))
    return polygons

# 计算适应度函数
def fitness(polygons):
    area = 0
    perimeter = 0
    intersection = 0
    for i, p in enumerate(polygons):
        area += p.area
        perimeter += p.length
        for j in range(i + 1, len(polygons)):
            intersection += p.intersection(polygons[j]).area
    return area + perimeter + intersection

# 回溯算法
def backtracking(polygons, bin_polygon, placed_polygons):
    global best_fitness
    global best_polygons
    # 计算当前剩余多边形的适应度下界
    remaining_fitness = fitness(polygons)
    if remaining_fitness >= best_fitness:
        return
    # 如果已经放置所有多边形，更新最优解
    if not polygons:
        best_fitness = remaining_fitness
        best_polygons = placed_polygons
        return
    # 选择最大的多边形进行放置
    index = np.argmax([p.area for p in polygons])
    polygon = polygons[index]
    for i in range(len(bin_polygon.exterior.coords) - 1):
        x1, y1 = bin_polygon.exterior.coords[i]
        x2, y2 = bin_polygon.exterior.coords[i + 1]
        for j in range(len(polygon.exterior.coords) - 1):
            x3, y3 = polygon.exterior.coords[j]
            x4, y4 = polygon.exterior.coords[j + 1]
            # 将多边形平移到指定位置
            dx = x1 - x3
            dy = y1 - y3
            polygon_translated = polygon.translate(dx, dy)
            # 检查是否与已经放置的多边形重叠
            overlap = False
            for placed_polygon in placed_polygons:
                if placed_polygon.intersects(polygon_translated):
                    overlap = True
                    break
            if not overlap:
                # 放置多边形
                polygons_new = polygons.copy()
                polygons_new.pop(index)
                placed_polygons_new = placed_polygons.copy()
                placed_polygons_new.append(polygon_translated)
                backtracking(polygons_new, bin_polygon, placed_polygons_new)

# 多边形套料函数
def polygon_packing(num_polygons, min_size, max_size):
    # 随机生成多边形
    polygons = generate_polygons(num_polygons, min_size, max_size)
    # 将所有多边形合并成一个二维平面
    bin_polygon = cascaded_union(polygons)
    # 初始化最优解
    global best_fitness
    global best_polygons
    best_fitness =[]
    best_polygons = []
    # 回溯算法求解最优解
    backtracking(polygons, bin_polygon, [])
    # 输出结果
    print('Number of polygons:', num_polygons)
    print('Min size:', min_size)
    print('Max size:', max_size)
    print('Best fitness:', best_fitness)
    # 绘制最优解
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    for polygon in best_polygons:
        patch = plt.Polygon(np.array(polygon.exterior), facecolor=np.random.rand(3,))
        ax.add_patch(patch)
    plt.show()

# 测试多边形套料函数
polygon_packing(num_polygons=10, min_size=0.1, max_size=0.3)
