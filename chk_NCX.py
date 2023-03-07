import glob
import os
import re
import openpyxl

files = glob.glob('NCX_*.txt')

data_dict = {}

for file in files:
    # 获取文件名
    filename = os.path.basename(file)
    filename_no_ext = os.path.splitext(filename)[0]

    # 截取需要的部分
    prefix, suffix = filename.split('_', 3)[:2]
    new_filename = f"{prefix}_{suffix}"

    # 读取文本文件
    with open(file, 'r') as f:
        lines = f.readlines()

    # 初始化变量
    x_md = None
    v_md = None
    data = []

    # 处理每行数据
    for line in lines:
        # 判断是否为 MD 行
        if 'T2:MD' in line:
            # 提取 X 和 V 字段的值
            x_match = re.search(r'X:(\d+)', line)
            v_match = re.search(r'V:\s*(\d+)', line)

            if x_match and v_match:
                x = int(x_match.group(1))
                v = int(v_match.group(1))

                # 计算 X_diff 值
                if x_md is not None:
                    x_diff = x - x_md
                    if x_diff != 0:
                        data.append([x, v, x_diff])

                # 更新 x_md 和 v_md 值
                x_md = x
                v_md = v

    # 保存数据到字典中
    data_dict[new_filename] = data

# 初始化 Excel 文件
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.append(['File Name', 'X', 'V', 'X_diff'])

# 将数据保存到同一个 sheet 中
for filename in sorted(data_dict.keys(), key=lambda x: int(re.search(r'NCX_(\d+)', x).group(1))):
    for row in data_dict[filename]:
        worksheet.append([filename, row[0], row[1], row[2]])

# 保存 Excel 文件
workbook.save('output.xlsx')
