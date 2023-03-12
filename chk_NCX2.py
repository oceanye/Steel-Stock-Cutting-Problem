import os
import re
from collections import OrderedDict

import openpyxl
from tkinter import filedialog
from tkinter import *
import math

def extract_data_from_file(filepath):
    """
    从NCX文件中提取数据
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    data = []
    data_detail=[]
    for line in lines:

            match = re.search(r'X:(\d+)\s+Y:\*+\s+V:\s*(\d+)\s+B:\*+\s+T1:\*+\s+T2:([a-zA-Z]{1,2}\d+)\s+T3:\*+\s+PAT:', line)
            if match:
                x, v, D = int(match.group(1)), int(match.group(2)), match.group(3)
                data_detail .append((x,v,D))
                if 'MD' in D:
                    data.append((x, v, D))

    data = sorted(data, key=lambda x: x[0])
    data_detail = sorted(data_detail, key=lambda x: x[0])

    grouped_data = []
    current_group = []
    current_t2 = "MD"
    i=0
    gap_x=[]
    gap_y=[]
    ecc_start = []
    ecc_end =[]
    for item in data_detail:
        if (current_t2 in item[2]) == False:

            current_group.append((item[0],item[1],item[2]))
        else:
            if current_group == []:
                i=i+1
                d_MD_x = item[0] #以MD标定，形成相对长度
                continue
            else:




                sorted_points_x = sorted(current_group, key=lambda p: (p[0], p[1]))
                gap_x.append(cal_group_gap(sorted_points_x))

                ecc_start.append((cal_group_ecc(i-1,sorted_points_x, data, "start")))
                ecc_end.append((cal_group_ecc(i-1,sorted_points_x, data, "end")))

                sorted_points_y = sorted(current_group, key=lambda p: (p[1], p[0]))
                if is_collinear([d[:2] for d in sorted_points_y]):
                    distances=[]
                    for i in range(len(sorted_points_y[:]) - 1):
                        x1, y1 = sorted_points_y[i][0],sorted_points_y[i][1]
                        x2, y2 = sorted_points_y[i+1][0],sorted_points_y[i+1][1]
                        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        distances.append(str(distance))
                    gap_y.append(str(len(distances))+"排:"+','.join(distances))
                else:
                    gap_y.append(cal_group_gap(sorted_points_y))

                grouped_data.append(current_group)
                current_group = []
            continue



    return data,gap_x,gap_y,ecc_start,ecc_end

def cal_group_ecc(i,sorted_points_x, data, info):
    x_MD= [pair[0] for pair in data]
    x_MD=list(OrderedDict.fromkeys(x_MD))



    if (info == "start"):
        ecc_i = 0
        x_coord = min([pair[0] for pair in sorted_points_x])
        ecc = x_coord - x_MD[i-1+ecc_i]

    else:
        ecc_i =1
        x_coord = max([pair[0] for pair in sorted_points_x])
        ecc = x_MD[i - 1 + ecc_i]-x_coord



    return ecc
def cal_group_gap(sorted_points):
    #计算螺栓群信息
    #x_gap = [current_group[i+1][0] - current_group[i][0] for i in range(len(current_group)-1)]
    #y_gap = [current_group[i + 1][1] - current_group[i][1] for i in range(len(current_group) - 1)]

    #print(x_gap)
    #print(y_gap)




    if (sorted_points[1][0] - sorted_points[0][0]) == 0:
        slope = None
    else:
        slope = (sorted_points[1][1] - sorted_points[0][1]) / (sorted_points[1][0] - sorted_points[0][0])

    line_group_current=[]
    line_group=[]

    for i in range(len(sorted_points)-1):

        x1=sorted_points[i][0]
        y1=sorted_points[i][0]
        x2 = sorted_points[i + 1][0]
        y2 = sorted_points[i + 1][0]
        if (x2 - x1) == 0:
            slope_current = None
        else:
            slope_current=(y2-y1)/(x2-x1)

        if (slope == slope_current or line_group_current==[]):
            line_group_current.append((sorted_points[i],sorted_points[i+1]))
        else:
            line_group.append(line_group_current)
            #slope=None
            line_group_current=[]
    if line_group_current != []:
        line_group.append(line_group_current)

    gap_list = []
    #if line_group==2:
   #     return '2排:'+str(math.sqrt((line_group[0][0][0][0]-line_group[1][0][0][0])**2+(line_group[0][0][0][1]-line_group[1][0][0][1])**2))

    for i in range(len(line_group) - 1):
        x0 = line_group[i][0][0][0]  # [连线分组-排数][排内直线数][x-coord][y-coord]
        y0 = line_group[i][0][0][1]
        x1 = line_group[i + 1][0][0][0]
        y1 = line_group[i + 1][0][0][1]
        x2 = line_group[i + 1][0][1][0]
        y2 = line_group[i + 1][0][1][1]

        d = distance_to_line(x0, y0, x1, y1, x2, y2)
        if d>500:
            d_str = '/'
        elif d==0:
            continue
        else:
            d_str=str(round(d,2))
        gap_list.append(d_str)

    if len(gap_list)>1 and gap_list[-1]=='/':
        gap_list[-1]='/,1排'
    if len(gap_list)>0:
        return str(len(gap_list)+1)+'排:'+','.join(gap_list)
    else:
        return '1排'


def distance_to_line(x0, y0, x1, y1, x2, y2):
    """计算点 (x0, y0) 到直线 (x1, y1) - (x2, y2) 的距离"""
    if x2-x1 == 0:
        return math.fabs(x1-x0)
    else:
        v = (x2 - x1, y2 - y1)
        w = (-v[1], v[0])
        c = -w[0]*x1 - w[1]*y1
        d = math.fabs(w[0]*x0 + w[1]*y0 + c)
        e = math.sqrt(w[0]*w[0] + w[1]*w[1])
        return d / e


def is_collinear(points):
    if len(points) < 3:
        return True

    x1, y1 = points[0]
    x2, y2 = points[1]
    slope = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')

    for i in range(2, len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        new_slope = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')
        if math.isinf(slope) and math.isinf(new_slope):
            continue
        if slope != new_slope:
            return False
    return True

def process_folder(folder_path):
    """
    处理NCX文件夹中的所有文件
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.column_dimensions['E'].width = 20.0
    ws.column_dimensions['F'].width = 20.0
    ws.append(['filename', '序号', 'X', 'V','Gap_x','Gap_y','ecc_start','ecc_end', 'Length(X_diff)'])
    for file in os.listdir(folder_path):
        if file.endswith('.txt') and file.startswith('NCX_'):
            filepath = os.path.join(folder_path, file)
            filename = os.path.splitext(file)[0]
            filename = '_'.join(filename.split('_')[0:2])
            file_index = filename.split('_')[-1]
            data,gap_x,gap_y,ecc_start,ecc_end = extract_data_from_file(filepath)
            if data:
                for i in range(1, len(data)):
                    x_diff = data[i][0] - data[i-1][0]
                    if x_diff != 0:
                        print(i)
                        ecc_start_bar = ecc_start[int(i / 2 - 0.5)]
                        ecc_end_bar = ecc_end[int(i/2-0.5)]

                        if ecc_start_bar > x_diff * 0.5:
                            ecc_start_bar =""
                        if ecc_end_bar > x_diff*0.5:
                            ecc_end_bar = ""

                        ws.append([filename, file_index, data[i][0], data[i][1], gap_x[int(i/2-0.5)],gap_y[int(i/2-0.5)],ecc_start_bar,ecc_end_bar,x_diff])
            wb.save(folder_path+'\output.xlsx')


def select_folder():
    """
    打开文件夹选择窗口
    """
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path


if __name__ == '__main__':
    folder_path = select_folder()
    process_folder(folder_path)
