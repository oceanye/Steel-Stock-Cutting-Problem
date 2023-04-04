import numpy as np
import sqlite3
import test8_ortools_stock_cutter_1d
import copy

import argparse
import Fixed_rank_rolls_v2

global parent_length


import argparse
import shared_variable

import logging

import PySimpleGUI as sg
import time

import sys



logging.basicConfig(level=logging.WARNING,
                    filename='./log_main.txt',
                    filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')



parser = argparse.ArgumentParser(description='套料设置')
parser.add_argument("-l","--roll_length",default=12000, type=int,help='整料长度(mm)')
parser.add_argument("-t","--roll_type",default='rank_roll', type=str,help='套料方式=opt_method,rank_roll')
parser.add_argument("-r","--split_length",default=600, type=int,help='最小切分长度(mm)')
parser.add_argument("-g","--roll_gap",default=5, type=int,help="循环套料拼接焊缝尺寸(mm)")
parser.add_argument("-m","--largesmall_mode",default=0,type=int,help='1-Large_mode;0-Small_mode')
args = parser.parse_args()


shared_variable.parent_length = args.roll_length
para_option=args.roll_type
shared_variable.split_length = args.split_length
shared_variable.roll_gap = args.roll_gap
shared_variable.largesmall_mode = args.largesmall_mode








#print(parent_length)

#Folderpath = filedialog.askdirectory()
#ssss = r"Z:\数字化课题\结构数字化课题\02 工作文件\2021 11 22 套料优化py脚本\2021 12 29 套料优化更新\Tekla_NCX_database.db"
# Test
ssss = r"Tekla_NCX_database.db"


cnR = sqlite3.connect(ssss)
print("Opened database successfully")

section=[]
length=[]
id=[]
material=[]
weight=[]
numb=[]
c = cnR.cursor()
cursor1 = c.execute("SELECT Section,Length,ID_list,Material,Weight,Number_list from Import_table")
for row in cursor1:
    section.append(row[0])
    length.append(round(float(row[1]),2)) # length is described with float
    id.append(row[2])
    material.append(row[3])
    weight.append(round(row[4],2))
    numb.append(row[5])

cnR.commit()

arr_section = np.array(section)
arr_length = np.array(length)
arr_id = np.array(id)
arr_material = np.array(material)
arr_weight = np.array(weight)
arr_numb = np.array(numb)

arr_data = [arr_section,arr_length,arr_id,arr_material,arr_weight]
arr_data2=np.transpose(arr_data)



# dt=np.dtype([('','S100')])
data = np.empty([len(section), 5], dtype='S100')


# for i in range(len(section)):
#     # print(type(section[i]))
#     # print(type(length[i]))
#     # print(type(id[i]))
#     #
#     # print((section[i]))
#     # print((length[i]))
#     # print((id[i]))
#
#
#     data[i][0]=(section[i])
#     data[i][1]=(length[i])
#     data[i][2]=(id[i])
#     #data[i][2]=bytes(temp1,encoding='utf-8')
#




# for i_data in range(len(data)):
#     for j_data in range(len(data[0])):
#         temp_data  =  data[i_data][j_data]
#         temp_data1 = temp_data.decode('utf-8')
#         data[i_data][j_data]=temp_data1
#
# print('----bbbb-----')
# print(np.shape(data))
# print(type(data[0][0]))
# print(type(data[0][1]))
# print(type(data[0][2]))
#
# print((data[0][0]))
# print((data[0][1]))
# print((data[0][2]))
#
# print(data[0])
# print((data[0][:]))
#
p = r'input_section_table.txt'
outfile = open ("out_member_group.txt","w")
# #
# #
# with open(p,encoding = 'utf-8') as f:
#     data_org = np.loadtxt(f,str,delimiter = " ")
#     #print(data_org[:])
#
#
#
# print("-----------qq-------")
# print(type(data_org[0][0]))
# print(type(data_org[0][1]))
# print(type(data_org[0][2]))
# print(np.shape(data_org))

data = arr_data2




section_list=np.unique(data[:,0])


def One_dim_list(ele):
    # 将输入的ele list 转换为1维数组，便于索引
    c_dot = 0
    len_ele = len(ele)
    key_ele_list = []
    for i_ele in ele:
        if(str(i_ele).count(","))>0:
    #        c_dot = c_dot + str(i_id).count(",")
            key_ele_list.extend(i_ele.split(","))
        else:
            key_ele_list.append(str(i_ele))
    #print(len_id+c_dot)
    #print(len(key_id_list))
    return(key_ele_list)

def pair_id_numb(k_id):
    k=[]
    if isinstance(k_id,int):
        k = str(k_id)
    else:
        for ki in k_id.split(","):

            ki_val,sufx = check_org_ID(ki)
            #print(key_id.index(ki_val))
            k.append(key_numb[key_id.index(ki_val)]+sufx)
    #print('----20221107-----')
    #print(k)

    return(k)

def Select_Section(section,data):
    (ni,nj)=list(np.shape(data))
#    print((ni,nj))
    del_i=[]
    data = np.insert(data, nj, 0, axis=1)
    for i in range(0,ni):
#        print(" check",data[i])
        if data[i][0] != section:
            # print(data[i])
            # print(i)
            del_i.append(i)
            #data1=np.delete(data,[i],0)
            #print("delete",del_i)
        else:
#            print(type(str(data[i][nj-1])))
            data[i][nj]=(str(data[i][2])).count(",")+1 # the quanity of bars is recorded in the last index
            #print("keep:",i)
    data1=np.delete(data,del_i,0)
    (tni,tnj)=list(np.shape(data1))


    return(data1)


def width_tol(w,tol):
    # print(w)
    w = [(i+tol) for i in w]
    # print(w)
    return(w)

def check_org_length(var):

    if str(var).__contains__('-'):
        val_len = round(float(var.split('-')[1]),2)
    else:
        val_len=round(float(var),2)
    return(val_len)
def check_org_ID(var):
    #print(var)
    if str(var).__contains__('A'):
        var_ID = var.strip('A')
        var_sufx='A'
    elif str(var).__contains__('B'):
        var_ID = var.strip('B')
        var_sufx='B'
    else:
        var_ID = var
        var_sufx=""

    return(var_ID,var_sufx)
def substi_len(val_len,len1,mat1,wei1):

    #print("val_len",val_len)
    # print("len1",len1)
    val_len=check_org_length(val_len)
    len1=list(map(float, list(len1)))
    #print("len1",len1)
    ii = len1.index(val_len)

    return [mat1[ii],wei1[ii]]




str1="********* 3mm tolerance is considered in each member ******\n"
outfile.write(str1)

section=[]
ratio=[]
unused=[]
lenlist=[]
idlist=[]
matlist=[]
weightlist=[]



#-----id 和 numb 建立匹配关系，用于索引构件编号(number_list)------#

global key_id
global key_numb
key_id = One_dim_list(id)
key_numb= One_dim_list(numb)

#print(key_id)
#print(key_numb)
#-----------------------------------------------------------#

#---------------------套料方式-------------------------------#
#para_option = "rank_roll" #(opt_method,rank_roll)

cnR = sqlite3.connect(ssss)
sql_Del_From = 'DELETE FROM rank_roll_table'
cnR.execute(sql_Del_From)
cnR.commit()

#------------------------------------------------------------#

# sg.one_line_progress_meter('截面类型', i + 1, len(section_list), '')


iter0=0

if len(section_list) > 1:
    # 定义窗口布局
    layout = [
        [sg.Text('套料进度:', size=(10, 1)), sg.ProgressBar(len(section_list), orientation='h', size=(50, 20), key='progress')],
    ]#'Output:', size=(10, 1)), sg.Multiline(size=(50, 10), key='output', autoscroll=True)


    # 创建窗口
    window = sg.Window('套料进度', layout,finalize=True)


for s in section_list:

    iter0 = iter0 + 1
    # 更新进度条

    if len(section_list)>1:
        window['progress'].update_bar(iter0)
        window.refresh()









    section_data = Select_Section(s, data)
    # print(section_data)
    print("-----------\n-----------\n","Section",s,":\n-----------\n",)
    [w1,ID1,b1,mat1,wei1]=[section_data[:,1],section_data[:,2],section_data[:, -1],section_data[:,3],section_data[:,4]]
    # demand_sub_rolls_lenth_list, ID_list, demand_sub_rolls_quantity, material_list, weight_list

    w1=list(map(float,list(w1)))
    b1=list(map(int,list(b1)))

    # print("w1:",w1)
    # print("b1:",b1)


    if para_option=="opt_method": # 优化套料需要在输入端考虑3mm 杆件之间间隙，循环套料在套料过程中考虑
        w1=width_tol(w1,3) # 3mm is tol
    else:
        w1=w1

    str1="------------\n"+"Section: "+str(s)+":\n"
    outfile.write(str1)
    #logging.info(str1)

    ID2= list(ID1)
    ID3=ID2
    for i_ID2 in range(0,len(ID2)):

        ID3[i_ID2]=ID2[i_ID2].split(",")
    # print("ID3[0]",ID3[0])
   # print("ID2_[0][0]",ID2[0][0])
   #  print("ID3_len",len(ID3[0]))
   #  print("ID3_type", type(ID3))

    # for i_ID1 in range(0,len(ID1)):
    #     ID1[i_ID1]=ID1[i_ID1].tostring().split(",")
    #     print("type_i_ID1",type(ID1[i_ID1]))
    # for i_ID3 in ID1:
    #     print("type_i_ID3",type(i_ID3))
    #
    # for si in range(0,len(w1)):
    #     print("Length:",w1[si],"ID:",ID1[si])




    #test2_MIP.CSP_MIP(w1, b1)
    #test3_gurobipy.CSP_gurobipy(w1,b1,ID1)

    if para_option =="opt_method":
        [consumed_big_rolls, consumed_sub_rolls,demand_sub_rolls]=test8_ortools_stock_cutter_1d.CSP_ortools(w1,b1,ID3)
    elif para_option =="rank_roll":
        [consumed_big_rolls, consumed_sub_rolls,demand_sub_rolls]=Fixed_rank_rolls_v2.rank_rolls(w1,ID3)


    print('')
    # print(rst1)
    # print(rst2)
    # print(type(w[1]))
    # print(type(w))
    # print(b)
    # print("big",consumed_big_rolls[0])
    # print("sub",consumed_sub_rolls[0])
    consumed_sub_rolls_weight = copy.deepcopy(consumed_sub_rolls)
    consumed_sub_rolls_material = copy.deepcopy(consumed_sub_rolls)



    for ic in range(len(consumed_sub_rolls_material)):
        for jc in range(len(consumed_sub_rolls_material[ic][0])):
            i_len = consumed_sub_rolls[ic][0][jc]
            #print("i_len",i_len)
            [consumed_sub_rolls_material[ic][0][jc],consumed_sub_rolls_weight[ic][0][jc]]= substi_len(i_len,w1,mat1,wei1)


    # print("---weight group22----")
    # print("length mat",len(consumed_sub_rolls_material))
    # print(consumed_sub_rolls_material)


    outfile.write("Usage info+Length_arrangement:"+str(consumed_big_rolls)+"\n")
    outfile.write("ID_Group:"+str(demand_sub_rolls).replace("[[","[").replace("]]","]").replace("', '",",").replace("'","").replace("[[","(").replace("]]",")").replace("], [","),(")+"\n")
    # print("------------------------")
    # print(consumed_big_rolls)
    # print(demand_sub_rolls)
    # print("------------------------")

    for i in range(len(consumed_big_rolls)):
        temp1=consumed_big_rolls[i]
        section.append(s)
        ratio.append(temp1[0])
        unused.append(temp1[1])

        temp2 = ''
        for i in range(len(temp1[2])):
            if para_option=="opt_method":
                temp2 = temp2 + str(check_org_length(temp1[2][i])-3) + ","
            else:
                temp2= temp2 + str(check_org_length(temp1[2][i])) + ","
        lenlist.append(temp2[0:-1])



    for j in range(len(demand_sub_rolls)):
        temp3 = ''
        temp4 = ''
        temp5 = ''
        for i in range(len(demand_sub_rolls[j][0])):

            temp3=temp3+(demand_sub_rolls[j][0][i])+","#check_org_ID
            temp4=temp4+consumed_sub_rolls_material[j][0][i]+","
            temp5=temp5+consumed_sub_rolls_weight[j][0][i]+","
        idlist.append(temp3[0:-1])
        matlist.append(temp4[0:-1])
        weightlist.append(temp5[0:-1])




    time.sleep(1)



outfile.close()

#window.close()





tbl1 = []
for tt in range(9):
    tbl1.append([])
for i in range(0, len(section)):



    tbl1[0].append("'"+section[i]+"'")
    tbl1[1].append(i+1)
    tbl1[2].append(ratio[i])
    tbl1[3].append(unused[i])
    tbl1[4].append("'"+str(lenlist[i])+"'")
    tbl1[5].append("'"+str(idlist[i])+"'")
    tbl1[6].append("'"+str(matlist[i])+"'")
    tbl1[7].append("'"+str(weightlist[i])+"'")
    tbl1[8].append("'"+str(pair_id_numb(idlist[i])).replace("[","").replace("]","").replace("'","")+"'")
#    print(pair_id_numb(idlist[i]))
tbl1_T = list(zip(*tbl1))

#print("--------")
#print(tbl1[8])
#print(tbl1[8][0])
#print("--------")

cnR = sqlite3.connect(ssss)
cnR.execute("drop table if exists Output_table;")
cnR.execute('''
CREATE TABLE Output_table
    (
    Section           STRING,
    Bar_group           STRING,
    Usage_ratio           REAL,
    Unusage_Length           REAL,
    Length_List           STRING,
    ID_List           STRING,    
    Material_List           STRING,
    Weight_List           STRING,
    Number_List           STRING);''')
cnR.commit()
sql_insert = "INSERT INTO Output_table(Section,Bar_group,Usage_ratio,Unusage_Length,Length_List,ID_List,Material_List,Weight_List,Number_List) VALUES"
sql_values = ""
sql_values1 = ""
for i in range(len(tbl1_T)):
    a = []
    List = tbl1_T[i]
    for j in range(len(List)):
        s = str(List[j])
        a.append(s)
    for k in range(0, len(a)):
        sql_values += a[k]
        sql_values += ","
    sql_values1 = "(" + sql_values.strip(',') + ")"
    sql_todo = sql_insert + sql_values1
    cuY = cnR.cursor()
    cuY.execute(sql_todo)
    sql_values = ""
    sql_value1 = ""
cnR.commit()
