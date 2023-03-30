import re
from tkinter import filedialog, messagebox
from tkinter import *
import openpyxl
import os


def extract_data_from_file(filepath):
    # 读取文件
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # 正则匹配并提取数据
    data = []
    for line in lines:
        match = re.search(r'X:(\d+(?:\.\d+)?)\s+Y:\*+\s+V:\s*(\d+)\s+B:\*+\s+T1:\*+\s+T2:([a-zA-Z]{1,2}\d+)\s+T3:\*+\s+PAT:', line)
        if match:
            data.append({'x': float(match.group(1)), 'v': float(match.group(2)), 't2': match.group(3)})

    # 分组
    groups = []
    last_md = None

    L_barlength = []

    L_m = []
    L_n = []
    L_x_spacing = []
    L_y_spacing = []

    L_x_start = []
    L_x_end = []

    L_start_shape_x = []
    L_start_shape_y = []
    L_end_shape_x = []
    L_end_shape_y = []

    L_ind=[]



    for d in data:
        if 'MD' in d['t2']:
            if last_md is not None:
                groups.append(last_md + [d])
            last_md = [d]
        elif last_md is not None:
            last_md.append(d)

    # 删除group中的子项，如果子项length==2
    for i, group in enumerate(groups):
        if len(group) == 2:
            groups.pop(i)

    # 输出结果
    # for i, group in enumerate(groups):
    #     print(f"Group {i + 1}:")
    #     for d in group:
    #         print(f"X:{d['x']} V:{d['v']} T2:{d['t2']}")

    # 分别计算每个Group，计算其中子项中，第一个MD和最后一个MD的X差值，并记录到数据bar_length中






    for i in range(len(groups)):
        x_group = GetBoltXGroup(groups[i])
        group_m = []
        group_n = []
        group_x_spacing = []
        group_y_spacing = []

        L_barlength.append(groups[i][-1]['x'] - groups[i][0]['x'])

        L_ind.append(i+1)
        #如果group[i]的length==2，则continue
        if len(groups[i]) == 2:
            b_start_shape_x=""
            b_start_shape_y=""
            b_end_shape_x=""
            b_end_shape_y=""
            x_start=""
            x_end = ""


        else:
            x_start, x_end = get_x_start_end(groups[i])
            for i in range(len(x_group)):
                m, n, x_spacing, y_spacing = check_grid(x_group[i])
                group_m.append(m)
                group_n.append(n)
                group_x_spacing.append(x_spacing)
                group_y_spacing.append(y_spacing)
            b_start_shape_x,b_start_shape_y,b_end_shape_x,b_end_shape_y=GetBoltShape(x_start, x_end, group_x_spacing,group_y_spacing, group_m, group_n)

        # L_m.append(group_m)
        # L_n.append(group_n)
        # L_x_spacing.append(group_x_spacing)
        # L_y_spacing.append(group_y_spacing)
        L_x_start.append(x_start)
        L_x_end.append(x_end)
        L_start_shape_x.append(b_start_shape_x)
        L_start_shape_y.append(b_start_shape_y)
        L_end_shape_x.append(b_end_shape_x)
        L_end_shape_y.append(b_end_shape_y)


        #将x_start中的0替换为""
        for i in range(len(L_x_start)):
             if L_x_start[i] == 0:
                 L_x_start[i] = ""
             if L_x_end[i] == 0:
                 L_x_end[i] = ""



    return (L_ind,L_barlength,L_x_start,L_x_end,L_start_shape_x,L_start_shape_y,L_end_shape_x,L_end_shape_y)

def GetBoltShape(g_x_start, g_x_end, g_x_spacing, g_y_spacing, g_m, g_n):
    if g_x_start != 0 and g_x_end !=0:
        g_start_shape_x = str(g_m[0]) + 'x' + str(g_x_spacing[0])
        g_start_shape_y = str(g_n[0]) + 'x' + str(g_y_spacing[0])
        g_end_shape_x = str(g_m[1]) + 'x' + str(g_x_spacing[1])
        g_end_shape_y = str(g_n[1]) + 'x' + str(g_y_spacing[1])
    else:
        g_shape_x = str(g_m[0]) + 'x' + str(g_x_spacing[0])
        g_shape_y = str(g_n[0]) + 'x' + str(g_y_spacing[0])
        if g_x_start !=0:

            g_start_shape_x = g_shape_x
            g_start_shape_y = g_shape_y
            g_end_shape_x=""
            g_end_shape_y=""
        elif g_x_end !=0:
            g_start_shape_x=""
            g_start_shape_y=""
            g_end_shape_x = g_shape_x
            g_end_shape_y = g_shape_y

    g_start_shape_x=CheckShape(g_start_shape_x)
    g_start_shape_y=CheckShape(g_start_shape_y)
    g_end_shape_x=CheckShape(g_end_shape_x)
    g_end_shape_y=CheckShape(g_end_shape_y)


    return (g_start_shape_x,g_start_shape_y,g_end_shape_x,g_end_shape_y)

#建立一个函数CheckShape，输入g_start_shape_x,如果是1x0，则替换为”单排“
def CheckShape(bolt_shape):
    if bolt_shape == "1x0":
        bolt_shape = "单排"
    elif "-1" in bolt_shape:
        bolt_shape = "非等间距"
    else:
        bolt_shape = bolt_shape
    return bolt_shape

#建立一个函数 GetBoltXGroup，输入group[0]，除去T2包含MD项，按照X差值进行分类，当X差值大于等于100时，将其分为一组
def GetBoltXGroup(group):
    x_group = []
    x_group.append([])
    for i in range(1, len(group)-1):
        if group[i]['x'] - group[i - 1]['x'] >= 100:
            x_group.append([group[i]])
        else:
            x_group[-1].append(group[i])

    #remove the null in x_group
    x_group = [x for x in x_group if x != []]
    return x_group

#建立一个函数GetGroupMesh，输入x_group[0]，除去第一位与最后一位的数，判定是否属于一个m行n列的正交网格，并输出行间距与列间距
def check_grid(points):
    """
    判断一组点是否可以组成正交网格，并输出网格的 x 间距和 y 间距。
    """

    x_list = [p['x'] for p in points]
    y_list = [p['v'] for p in points]
    x_sorted = sorted(set(x_list))
    y_sorted = sorted(set(y_list))
    delta_x = [x_sorted[i+1] - x_sorted[i] for i in range(len(x_sorted)-1)]
    delta_y = [y_sorted[i+1] - y_sorted[i] for i in range(len(y_sorted)-1)]
    if len(delta_y) == 0:
        print("无法组成正交网格1")
        return

    if len(delta_x) == 0 and all(d == delta_y[0] for d in delta_y):
        y_spacing = delta_y[0]
        n = int((y_sorted[-1] - y_sorted[0]) // y_spacing + 1)
        if n >= 2 and  y_spacing * (n-1) == y_sorted[-1] - y_sorted[0]:
            print(f"可以组成 {1}*{n} 的正交网格，x 间距为 {0}，y 间距为 {y_spacing}")
            return (1, n, 0, y_spacing)

    elif all(d == delta_x[0] for d in delta_x) and all(d == delta_y[0] for d in delta_y):
        x_spacing = delta_x[0]
        y_spacing = delta_y[0]
        m = int((x_sorted[-1] - x_sorted[0]) // x_spacing + 1)
        n = int((y_sorted[-1] - y_sorted[0]) // y_spacing + 1)
        if m >= 2 and n >= 2 and x_spacing * (m-1) == x_sorted[-1] - x_sorted[0] and y_spacing * (n-1) == y_sorted[-1] - y_sorted[0]:
            print(f"可以组成 {m}*{n} 的正交网格，x 间距为 {x_spacing}，y 间距为 {y_spacing}")
            return (m, n, x_spacing, y_spacing)
        else:
            print("无法组成正交网格2")


    else:
        print("无法组成正交网格3-Y向不等距")
        return (-1, -1, -1, -1)

    return (1, 1, 0, 0)




def process_folder(folder_path):
    """
    处理NCX文件夹中的所有文件
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.column_dimensions['E'].width = 20.0
    ws.column_dimensions['F'].width = 20.0
    ws.column_dimensions['G'].width = 20.0
    ws.column_dimensions['H'].width = 20.0
    ws.append(['文件名', '序号', '单构件长度', '螺栓偏移-起点','列螺栓排布-起点','行螺栓排布-起点','螺栓偏移-终点','列螺栓排布-终点','行螺栓排布-终点'])
    for file in os.listdir(folder_path):
        if file.endswith('.txt') and file.startswith('NCX_'):
            filepath = os.path.join(folder_path, file)
            filename = os.path.splitext(file)[0]
            filename = '_'.join(filename.split('_')[0:2])
            file_index = filename.split('_')[-1]
            List_ind,List_length,List_x_start,List_x_end,List_start_shape_x,List_start_shape_y,List_end_shape_x,List_end_shape_y = extract_data_from_file(filepath)

            for i in range(len(List_length)):
                print(filename, List_ind[i],List_length[i],List_x_start[i],List_start_shape_x[i],List_start_shape_y[i],List_x_end[i],List_end_shape_x[i],List_end_shape_y[i])
                ws.append([filename, List_ind[i],List_length[i],List_x_start[i],List_start_shape_x[i],List_start_shape_y[i],List_x_end[i],List_end_shape_x[i],List_end_shape_y[i]])
            wb.save(folder_path + '\\NCX_校核结果.xlsx')


def select_folder():
    """
    打开文件夹选择窗口
    """
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path

#建立一个函数get_x_start_end,输入x_group,离遍计算x_group中第2项至倒数第2项的x值，分别与第1项和最后1项做差，与第1项做差的最小值记作x_start，与最后1项做差的最小值记作x_end
def get_x_start_end(x_group):
    x_start = []
    x_end = []
    for i in range(1, len(x_group) - 1):
        x_start.append(abs(x_group[i]['x'] - x_group[0]['x']))
        x_end.append(abs(x_group[i]['x'] - x_group[-1]['x']))
    x_start_offset = min(x_start)
    x_end_offset = min(x_end)

    if x_start_offset > 100:
        x_start_offset = 0;
    if x_end_offset > 100:
        x_end_offset = 0;
    return x_start_offset, x_end_offset


if __name__ == '__main__':
    folder_path = select_folder()
    process_folder(folder_path)
