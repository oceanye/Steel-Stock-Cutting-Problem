import cv2
import numpy as np


# 标记鼠标点击事件
def mouse_callback(event, x, y, flags, param):
    global selecting, selected_color, lower_color, upper_color

    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        selected_color = image_hsv[y, x]
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        selected_color = None

        # 提取选中颜色的范围
        if selected_color is not None:
            lower_color = np.array([max(selected_color[0] - color_threshold, 0),
                                    max(selected_color[1] - color_threshold, 0),
                                    max(selected_color[2] - color_threshold, 0)])
            upper_color = np.array([min(selected_color[0] + color_threshold, 255),
                                    min(selected_color[1] + color_threshold, 255),
                                    min(selected_color[2] + color_threshold, 255)])


# 加载图像
image = cv2.imread('input.png')
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 颜色范围及阈值参数
selected_color = None
lower_color = None
upper_color = None
color_threshold = 30

# 选择区域的参数
select_option = True  # 设置为True以启用选择区域功能
selecting = False

# 创建窗口并绑定鼠标回调函数
cv2.namedWindow('Input')
cv2.setMouseCallback('Input', mouse_callback)

while True:
    # 显示输入图像
    cv2.imshow('Input', image)

    if selected_color is not None:
        # 根据颜色范围创建掩码
        mask = cv2.inRange(image_hsv, lower_color, upper_color)

        # 进行形态学操作，以便更好地定义区域的形状
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morphology = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 查找轮廓
        contours, _ = cv2.findContours(morphology, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 筛选四边形区域
        quadrilateral_contours = []
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            if len(approx) == 4:
                quadrilateral_contours.append(approx)

        # 绘制红色边界
        output = image.copy()
        for contour in quadrilateral_contours:
            cv2.drawContours(output, [contour], -1, (0, 0, 255), 2)

        # 显示结果图像
        cv2.imshow('Output', output)

    key = cv2.waitKey(1)
    if key == 27:  # 按下ESC键退出程序
        break

    if select_option:
        if key == ord('r'):  # 按下'r'键重置选中颜色
            selected_color = None
        elif key == ord('s') and selected_color is not None:  # 按下's'键保存选中的颜色范围
            lower_color = np.array([max(selected_color[0] - color_threshold, 0),
                                    max(selected_color[1] - color_threshold, 0),
                                    max(selected_color[2] - color_threshold, 0)])
            upper_color = np.array([min(selected_color[0] + color_threshold, 255),
                                    min(selected_color[1] + color_threshold, 255),
                                    min(selected_color[2] + color_threshold, 255)])
            np.savetxt('color_range.txt', np.concatenate((lower_color, upper_color)), fmt='%d')
            print('颜色范围已保存到color_range.txt文件')

cv2.destroyAllWindows()
