import PySimpleGUI as sg
import time

# 创建窗口布局
layout = [
    [sg.Text('Progress:', size=(10, 1)), sg.ProgressBar(100, orientation='h', size=(20, 20), key='progress')],
    [sg.Text('Output:', size=(10, 1)), sg.Multiline(size=(50, 10), key='output', autoscroll=True)]
]

# 创建窗口并设置主题
sg.theme('DarkBlue3')
window = sg.Window('Progress and Output', layout,finalize=True)

# 执行程序
for i in range(1, 101):
    # 更新进度条
    window['progress'].update(i)

    # 打印输出
    output_text = f'{i}\n'
    window['output'].print(output_text)

    # 暂停一段时间，模拟程序执行
    time.sleep(0.1)

# 关闭窗口
window.close()
