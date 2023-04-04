import random
import math
import copy
import re
import sqlite3

import shared_variable

import logging

global idx_status  # idx_status = 0 数组顺序ok，=1 数组顺序需调整
global slice_bar_info  # 按顺序记录杆件长度与切断点


logging.basicConfig(level=logging.WARNING,
                    filename='./log_rank_roll.txt',
                    filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')




def sum_list(list1, loc_of_sum_list1):
    # 输入一个数列，并指定数位，将该数位之前的数据求和

    total = loc_of_sum_list1*shared_variable.tol # 考虑循环套料两两之间，增加3mm间隙
    for i in range(loc_of_sum_list1):
        total = list1[i] + total
    return round(float(total),2)


def gen_list(length_of_list):
    # 生成一个随机数串
    rand_list = []
    for i in range(length_of_list):
        rand_list.append(int(random.uniform(0.3, 11.5) * 100) * 10)
    return rand_list


# print(gen_list(8))


# list1 = gen_list(8)
# list1 = [7390, 610, 3440, 1690, 3790, 4080, 7290, 4690]

# print(list1)

def find_slice_loc(list_sum, roll_length):
    # 找到整数切分段
    num_roll = math.ceil(list_sum[-1] / roll_length)
    roll_slice_list = []

    for i in range(num_roll):
         for i_r in range(len(list_sum)):
            if list_sum[i_r] > roll_length * (i + 1):
                 roll_slice_list.append(i_r + 1)
                 break
    return (roll_slice_list)


def len_sum(list1):
    list_sum = []
    for i in range(len(list1) + 1):
        s = sum_list(list1, i)
        list_sum.append(s)
    return (list_sum)


def slice_last(list1, roll_length):
    loc_list = find_slice_loc(len_sum(list1), roll_length)
    loc = loc_list[-1]

    list1_last = list1[loc - 2:]  # 若最后一段过短，将最后一段切除，单独下料，例如总长24450，两根整料必须会有余量450
    list1 = list1[:loc - 2]

    print(list1[-1])
    print(list1, list1_last)
    return (list1, list1_last)


def evaluate_list(list1, roll_length, min_len):
    list_temp = []
    sub_list = []  # 存储切分方案
    idx_status = 0
    list_sum = len_sum(list1)
    slice_loc = find_slice_loc(list_sum, roll_length)
    global slice_bar_info

    print('---------------------------')

    print('长度信息：', list1)
    print('前序求和：', list_sum)
    print('切分位置：', slice_loc)


    logging.debug('切分位置：', slice_loc)
    # print(slice_loc)

    for i in range(len(slice_loc)):
        slice_i = slice_loc[i]
        if list1[slice_i - 2] < min_len * 2:
            print(list1[slice_i - 2], '分段处过短，需调整')
            idx_status = 1
            loc = slice_i - 2
            break

        if (list_sum[slice_i - 1] - roll_length * (i + 1)) < min_len:
            print('前半段过短，需调整')
            idx_status = 1
            loc = slice_i - 1
            break
        if (list1[slice_i - 2] - (list_sum[slice_i - 1] - roll_length * (i + 1))) < min_len:
            print('后半段过短，需调整')
            idx_status = 1
            loc = slice_i - 1
            break

        # A-前一组切断后的后半段； B-切断后的前半段
        if i == 0:  # 切第一根
            sp_j = slice_loc[i]
            list_temp = (list1[:sp_j - 1])
            list_temp[-1] = str(list_temp[-1]) + "A"
        else:  # 切第二根~切最后一刀，输出至倒数第二根
            sp_i = slice_loc[i - 1]
            sp_j = slice_loc[i]
            list_temp = list1[sp_i - 2:sp_j - 1]
            list_temp[0] = str(list_temp[0]) + "B"
            list_temp[-1] = str(list_temp[-1]) + "A"

        splitGroupNo = str(i + 1)
        splitItemID = str(list_temp[-1])
        splitLengthA = str(round(list1[slice_i - 2] - (list_sum[slice_i - 1] - roll_length * (i + 1)),2))
        splitLengthB = str(round(list_sum[slice_i - 1] - roll_length * (i + 1),2))
        # print('查看组号： ' + splitGroupNo)
        # print('查看ID： ' + splitItemID)
        # print('查看A长： ' + splitLengthA)
        # print('查看B长： ' + splitLengthB)

        cuttingInfo = []

        cuttingInfo.append(splitGroupNo)
        cuttingInfo.append(splitItemID)
        cuttingInfo.append(splitLengthA)
        cuttingInfo.append(splitLengthB)

        slice_bar_info.append(cuttingInfo)

        # slice_bar_info.append(str(list_temp[-1])+str(list1[slice_i - 2] - (list_sum[slice_i - 1] - roll_length * (i + 1)))+'B'+str(list_sum[slice_i - 1] - roll_length * (i + 1)))
        # print(slice_bar_info)

        # print('第',i+1,'个',roll_length,'切分段：',list1[slice_i-2],'/前段(A)：', list1[slice_i-2]-(list_sum[slice_i - 1] - roll_length * (i + 1)),'/后段(B)：', list_sum[slice_i - 1] - roll_length * (i + 1))
        # print('  该分段长度布置:',list_temp)

        sub_list.append(list_temp)

        if i == (len(slice_loc) - 1):  # 最后一段信息
            sp_i = slice_loc[-1]
            list_temp = list1[sp_i - 2:]
            list_temp[0] = str(list_temp[0]) + "B"
            print('第', i + 2, '个', roll_length, '切分段(末段)')
            print('  该分段长度布置:', list_temp)
            sub_list.append(list_temp)

    if idx_status == 0:
        total_bar = math.ceil((list_sum[-1]) / roll_length)

        # print('  该分段长度布置:',list_temp)
        print('完成切分，该组序列OK，循环套料总长度', list_sum[-1], '，共计需要', roll_length, '整料', total_bar, '根')
        # print('剩余长度',roll_length-(list_sum[-1]%roll_length))
        loc = len(list1)
    return (idx_status, loc, sub_list)


def ID_search(tempList):
    # 调用该数组（对应Value），即可得到其中的ID值，每次一个唯一值
    if len(tempList) == 0:
        id = "已经没有该值的ID了"
        tempID = id
    else:
        id = tempList.pop(0)
        tempID = id
    return tempID


def findKV(length, dict1):
    # findKV方法能找到所有的length=200（Value）的所有ID（Key），返回数组
    keyList = []
    findKeyByValue = [k for k, v in dict1.items() if v == float(length)]
    keyList.extend(findKeyByValue)
    tempList = keyList
    if len(tempList) >= 1:
        global dtKey
        dtKey = tempList.pop()
        del dict1[dtKey]
    return dtKey


def find_ID_list(sub_list, dict1):
    sub_list_A = copy.deepcopy(sub_list)
    for i in range(len(sub_list)):
        for j in range(len(sub_list[i])):
            temp_length = sub_list[i][j]
            # print(str(temp_length).isdigit())
            if (str(temp_length)[-1] == 'B'):  # True
                del sub_list_A[i][j]

    for i in range(len(sub_list_A)):
        for j in range(len(sub_list_A[i])):
            ID_suffix = []
            temp_len = sub_list_A[i][j]
            temp_ID = re.sub(r"[A,B]", "", str(temp_len))
            if isinstance(temp_len, str):
                ID_suffix = list(temp_len)[-1]
            sub_list_A[i][j] = str(findKV(temp_ID, dict1)).strip("[").strip("]") + str(ID_suffix).strip("[").strip("]")
            # print(sub_list_A[i][j])

    sub_ID_list = copy.deepcopy(sub_list_A)
    for i in range(len(sub_list_A)):
        for j in range(len(sub_list_A[i])):
            temp_oriLen = sub_list_A[i][j]
            temp_oriID = int(re.sub(r"[A,B]", "", str(temp_oriLen)))
            if (str(temp_oriLen)[-1] == 'A'):  # True
                sub_ID_list[i + 1].insert(0, str(temp_oriID) + 'B')
    return sub_ID_list


# n = 10

# list1 = gen_list(n)


# list1 表示各段长度
# 这个是超级长的暴躁版List,仅供测试娱乐
# list1 = [700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,11000,10200,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150]

# 这个是正常测试长度，供调试
# list1 = [8680, 1080, 4180, 9390, 4030, 2630, 11430, 8460, 8000, 4030, 2630, 11430, 8460, 8000, 2670]

# ID 表示各段编号，目前是生成顺序的数列，后续导入Tekla模型编号
# ID_list =  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']



def rank_output(dataAna):
    num_bar = dataAna[-1][1]

    consumed_big_rolls = [[[] for i in range(3)] for j in range(num_bar)]
    consumed_sub_rolls = [[[]] for j in range(num_bar)]
    demand_sub_rolls = [[[]] for i in range(num_bar)]

    print(consumed_big_rolls)
    for i in dataAna:

        if i[0].__contains__('A'):
            l = i[3]
        elif i[0].__contains__('B'):
            l = i[4]
        else:
            l = i[2]

        consumed_big_rolls[i[1] - 1][0] = 1
        consumed_big_rolls[i[1] - 1][1] = 0
        consumed_big_rolls[i[1] - 1][2].append(l)

        consumed_sub_rolls[i[1] - 1][0].append(l)

        demand_sub_rolls[i[1] - 1][0].append(i[0])

    # print(consumed_big_rolls)
    # print(consumed_sub_rolls)
    # print(demand_sub_rolls)
    return (consumed_big_rolls, consumed_sub_rolls, demand_sub_rolls)


def rank_rolls(list_temp, ID_list_temp):

    make_print_to_file(path='./log')

    ID_list = []
    list1 = []
    global slice_bar_info
    # 将list列和ID列组合

    n = 0
    for ii in ID_list_temp:
        for jj in ii:
            ID_list.append(jj)
            list1.append(list_temp[n])
        n = n + 1

    print(ID_list)
    print(list1)

    dict1 = dict(zip(ID_list, list1))
    originDict1 = dict(zip(ID_list, list1))

    list1_last = []

    t = 0
    idx_status = 1

    sqlItemList = []
    dataDic = {}

    sql_ID = '123A';
    sql_Group_No = 0;
    sql_Length_NC = 0;
    sql_Length_A = 0;
    sql_Length_B = 0;
    INFO = 'ABC';

    while idx_status == 1:
        slice_bar_info = []
        print('迭代次数:', t)

        #if sum_list(list1, len(list1)) % 12000 < 650:  # 切去最后一段???20221107
        #   [list1, list1_last] = slice_last(list1, 12000)
        if sum_list(list1, len(list1))> shared_variable.parent_length :
            [idx_status, loc, sub_list] = evaluate_list(list1, shared_variable.parent_length , shared_variable.split_length)
        else:
            [idx_status,loc,sub_list]=[0,len(list1),[list1]]
        # print('状态：',idx_status)
        if idx_status == 1:
            l_r = round(len(list1)/2)

            if loc > l_r: # 针有较多短构件，设定阈值，前5根排好后，即不作调整，避免过多迭代
                list1_a = list1[:loc - l_r]
                list1_b = list1[loc - l_r:]
                random.shuffle(list1_b)
                list1 = list1_a + list1_b
            else:
                random.shuffle(list1)

            t = t + 1
            # if loc < 5:
            #     random.shuffle(list1)
            # elif (loc<=10 and loc >5):
            #     list1_a = list1[:loc - 5]
            #     list1_b = list1[loc - 5:]
            #     random.shuffle(list1_b)
            #     list1 = list1_a + list1_b
            # elif (loc<=20 and loc>10):
            #     list1_a = list1[:loc - 10]
            #     list1_b = list1[loc - 10:]
            #     random.shuffle(list1_b)
            #     list1 = list1_a + list1_b
            # else:
            #     list1_a = list1[:loc - 20]
            #     list1_b = list1[loc - 20:]
            #     random.shuffle(list1_b)
            #     list1 = list1_a + list1_b
            # print(list1)
            # t = t + 1
        else:

            #if len(list1_last) > 0:  # 切去最后一段
            #    sub_list.append(list1_last)
            #   print('另计最后单根构件，构件长度', list1_last)
            # --------------------------------------------------
            groupNo = find_ID_list(sub_list, dict1)
            print('分段结果：', sub_list)  # 输出分段结果
            print('分段ID值：', groupNo)  # find_ID_list(sub_list, dict1))
            print('原始字典：', originDict1)
            print('分段AB长:', slice_bar_info)

            dataClean = copy.deepcopy(sub_list)
            for i in range(len(slice_bar_info)):
                # print(len(sub_list))
                # print(len(slice_bar_info))
                if sub_list[i][-1] == slice_bar_info[i][1]:
                    # print(slice_bar_info[i][2])
                    # print(dataClean[i][-1])
                    dataClean[i][-1] = round(float(slice_bar_info[i][2]),2)
                    dataClean[i + 1][0] = round(float(slice_bar_info[i][3]),2)
                    # print('clean:', dataClean)
                else:
                    print('!=')

            dataAna = []
            anaInfo = 'None'
            for i, j in zip(groupNo, dataClean):
                for l in range(len(i)):
                    sql_ID = i[l]
                    sql_Group_No = dataClean.index(j) + 1

                    if str((i[l][-1])).__contains__('A'):
                        sql_Length_A = j[l]-shared_variable.roll_gap
                        # dataAna.append([sql_ID,sql_Group_No,0,sql_Length_A,0,anaInfo])
                        sql_Length_NC = originDict1[str(i[l]).strip('A')]  # 原杆件长度
                        dataAna.append(
                            [sql_ID, sql_Group_No, sql_Length_NC, str(sql_Length_A) + "-" + str(sql_Length_NC), 0,
                             anaInfo])  # i[l][-1].strip('A')
                    elif str((i[l][-1])).__contains__('B'):
                        sql_Length_B = j[l]
                        sql_Length_NC = originDict1[str(i[l]).strip('B')]  # 原杆件长度
                        dataAna.append(
                            [sql_ID, sql_Group_No, sql_Length_NC, 0, str(sql_Length_B) + "-" + str(sql_Length_NC),
                             anaInfo])  # i[l][-1].strip('B')

                    else:
                        sql_Length_NC = j[l]
                        dataAna.append([sql_ID, sql_Group_No, sql_Length_NC, 0, 0, anaInfo])
            # --------------------------------------------------
            break

    # print('数据清洗:', dataClean)
    # print('数据分析:', dataAna)

    ######################################################
    #conn = sqlite3.connect('test1.db')
    cnR = sqlite3.connect(r"Tekla_NCX_database.db")
    c = cnR.cursor()
    print("数据库打开成功")

    #sql_Del_From = 'DELETE FROM Analysis_table'

    #c.execute(sql_Del_From)
    #conn.commit()
    # print ("Analysis_table 已清空")

    exampleValues = ['13A', 2, 10000, 0, 0, 'None']

    sql = "INSERT INTO rank_roll_table (ID,Group_No,Length_NC,Length_A,Length_B,INFO) VALUES (?,?,?,?,?,?)"

    for no in range(len(dataAna)):

        c.execute(sql, (dataAna[no][0], dataAna[no][1], dataAna[no][2], dataAna[no][3], dataAna[no][4], dataAna[no][5]))
        cnR.commit()
        # print ("数据插入成功")

    cnR.close()
    print("数据库已更新")
    ###################test1#########################

    [consumed_big_rolls, consumed_sub_rolls, demand_sub_rolls] = rank_output(dataAna)

    return (consumed_big_rolls, consumed_sub_rolls, demand_sub_rolls)

#
# conn = sqlite3.connect('test1.db')
# c = conn.cursor()
# print ("数据库打开成功")
#
# sql_Del_From_TNC = 'DELETE FROM Tekla_NCX_table'
#
# c.execute(sql_Del_From_TNC)
# conn.commit()
# print ("Tekla_NCX_table 已清空")
#
# example_NCX_Import = [['BH500*200*8*12', 'Q345B', 532.47, 7880, '11, 12, 13A', 'H61, H61, H61'],['BH600*300*10*16', 'Q345B', 1151.5, 9600, '21, 22', 'H252, H252'],['BH600*250*10*14', 'Q345B', 1126.33, 11280, '31, 32, 33A', 'H107, H107, H107']]
#
# sql = "INSERT INTO Tekla_NCX_table (Section,Material,Weight,Length,ID_list,Number_list) VALUES (?,?,?,?,?,?)"
#
#
# dataAna_NCX = []
#
# for no in range(len(example_NCX_Import)):
#     c.execute(sql, (example_NCX_Import[no][0], example_NCX_Import[no][1], example_NCX_Import[no][2], example_NCX_Import[no][3], example_NCX_Import[no][4], example_NCX_Import[no][5]))
#     conn.commit()
#     print ("数据插入成功")
#
# conn.close()


####################NCX#######################
# conn = sqlite3.connect('Tekla_NCX_database_test')
# c = conn.cursor()
# print ("NCX数据库打开成功")

def make_print_to_file(path='./log'):
    '''
    path， it is a path for save your log about fuction print
    example:
    use  make_print_to_file()   and the   all the information of funtion print , will be write in to a log file
    :return:
    '''
    import sys
    import os
    import sys
    import datetime

    class Logger(object):
        def __init__(self, filename="循环套料.log", path="./"):
            self.terminal = sys.stdout
            self.path = os.path.join(path, filename)
            self.log = open(self.path, "a", encoding='utf8', )
            print("save:", os.path.join(self.path, filename))

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    fileName = datetime.datetime.now().strftime('Rank_roll_Log' + '%Y_%m_%d_%H')
    sys.stdout = Logger(fileName + '.log', path=path)

    #############################################################
    # 这里输出之后的所有的输出的print 内容即将写入日志
    #############################################################
    print(fileName.center(60, '*'))





