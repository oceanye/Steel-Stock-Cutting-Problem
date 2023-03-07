import os
import re
import openpyxl
from tkinter import filedialog
from tkinter import *


def extract_data_from_file(filepath):
    """
    从NCX文件中提取数据
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    data = []
    for line in lines:
        if 'T2:MD' in line:
            match = re.search(r'X:(\d+)\s+Y:\*+\s+V:\s*(\d+)\s+B:\*+\s+T1:\*+\s+T2:MD(\d+)\s+T3:\*+\s+PAT:', line)
            if match:
                x, v, row = int(match.group(1)), int(match.group(2)), int(match.group(3))
                data.append((x, v, row))

    data = sorted(data, key=lambda x: x[2])
    return data


def process_folder(folder_path):
    """
    处理NCX文件夹中的所有文件
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['filename', '序号', 'X', 'V', 'Length(X_diff)'])
    for file in os.listdir(folder_path):
        if file.endswith('.txt') and file.startswith('NCX_'):
            filepath = os.path.join(folder_path, file)
            filename = os.path.splitext(file)[0]
            filename = '_'.join(filename.split('_')[0:2])
            file_index = filename.split('_')[-1]
            data = extract_data_from_file(filepath)
            if data:
                for i in range(1, len(data)):
                    x_diff = data[i][0] - data[i-1][0]
                    if x_diff != 0:
                        ws.append([filename, file_index, data[i][0], data[i][1], x_diff])
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
