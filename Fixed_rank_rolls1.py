import random
import math
import copy
import re

global idx_status # idx_status = 0 数组顺序ok，=1 数组顺序需调整

def sum_list(list1, loc_of_sum_list1):
    #输入一个数列，并指定数位，将该数位之前的数据求和
    total = 0
    for i in range(loc_of_sum_list1):
        total = list1[i] + total
    return total

def gen_list(length_of_list):
    #生成一个随机数串
    rand_list = []
    for i in range(length_of_list):
         rand_list.append(int(random.uniform(0.3,11.5)*100)*10)
    return rand_list

#print(gen_list(8))


#list1 = gen_list(8)
#list1 = [7390, 610, 3440, 1690, 3790, 4080, 7290, 4690]

#print(list1)

def find_slice_loc(list_sum,roll_length):
    #找到整数切分段
    num_roll=math.ceil(list_sum[-1]/roll_length)
    roll_slice_list = []
    for i in range(num_roll):
        for i_r in range(len(list_sum)):
            if list_sum[i_r]>roll_length*(i+1):
                roll_slice_list.append(i_r+1)
                break
    return(roll_slice_list)




def len_sum(list1):
    list_sum = []
    for i in range(len(list1)+1):
        s=sum_list(list1,i)
        list_sum.append(s)
    return(list_sum)

def slice_last(list1,roll_length):
    loc_list = find_slice_loc(len_sum(list1),roll_length)
    loc = loc_list[-1]

    list1_last = list1[loc-2:] #若最后一段过短，将最后一段切除，单独下料，例如总长24450，两根整料必须会有余量450
    list1 = list1[:loc-2]

    print(list1[-1])
    print(list1,list1_last)
    return(list1,list1_last)



def evaluate_list(list1, roll_length,min_len):
    list_temp =[]
    sub_list = [] #存储切分方案
    idx_status = 0
    list_sum = len_sum(list1)
    slice_loc = find_slice_loc(list_sum, roll_length)

    global length_pre,length_post

    length_pre = 0
    length_post=0

    print('---------------------------')
    print('长度信息：',list1)
    print('前序求和：',list_sum)
    print('切分位置：',slice_loc)
    #print(slice_loc)

    for i in range(len(slice_loc)):
        slice_i = slice_loc[i]

        if list1[slice_i-2] < min_len*2:
            print(list1[slice_i-2],'分段处过短，需调整')
            idx_status = 1
            loc = slice_i-2
            break


        if (list_sum[slice_i-1]-roll_length*(i+1)) < min_len:
            print('前半段过短，需调整')
            idx_status = 1
            loc = slice_i-1
            break
        if (list1[slice_i-2]-(list_sum[slice_i - 1] - roll_length * (i + 1))) < min_len:
            print('后半段过短，需调整')
            idx_status = 1
            loc = slice_i-1
            break


        # A-前一组切断后的后半段； B-切断后的前半段

        if i==0: #切第一根
            length_pre_i = list_sum[slice_i - 1] - roll_length * (i + 1)# A段长度
            length_post_i = list1[slice_i-2]-(list_sum[slice_i - 1] - roll_length * (i + 1)) # B段长度
        else:
            slice_j = slice_loc[i-1] # 前一根
            length_pre_j = list_sum[slice_j - 1] - roll_length * (i + 1-1)# A段长度
            length_pre_i = list_sum[slice_i - 1] - roll_length * (i + 1)# A段长度
            length_post_i = list1[slice_i-2]-(list_sum[slice_i - 1] - roll_length * (i + 1))


        if i==0: #切第一根
            sp_j = slice_loc[i]
            list_temp=(list1[:sp_j-1])
            list_temp[-1] = str(list_temp[-1]) + "(A"+str(length_pre_i)+")"
        else:    #切第二根~切最后一刀，输出至倒数第二根
            sp_i = slice_loc[i - 1]
            sp_j = slice_loc[i]
            list_temp=list1[sp_i-2:sp_j-1]
            list_temp[0] = str(list_temp[0]) + "(B"+str(length_post_i)+")"
            list_temp[-1]= str(list_temp[-1])+ "(A"+str(length_pre_j)+")"





        print('第',i+1,'个',roll_length,'切分段：',list1[slice_i-2],'/前段：', length_pre_i,'+后段：', length_post_i )
        print('  该分段长度布置:',list_temp)

        sub_list.append(list_temp)

        if i == (len(slice_loc)-1): # 最后一段信息
            sp_i = slice_loc[-1]
            list_temp=list1[sp_i-2:]
            list_temp[0] = str(list_temp[0]) + "(B"+str(length_post_i)+")"
            print('第',i+2,'个',roll_length,'切分段(末段)')
            print('  该分段长度布置:',list_temp)
            sub_list.append(list_temp)



    if idx_status == 0:




        total_bar = math.ceil((list_sum[-1])/roll_length)



       # print('  该分段长度布置:',list_temp)
        print('完成切分，该组序列OK，循环讨论总长度',list_sum[-1],'，共计需要',roll_length,'整料',total_bar,'根')
        #print('剩余长度',roll_length-(list_sum[-1]%roll_length))
        loc = len(list1)
    return(idx_status,loc,sub_list)

def ID_search(tempList):
    # 调用该数组（对应Value），即可得到其中的ID值，每次一个唯一值
    if len(tempList) == 0:
        id ="已经没有该值的ID了"
        tempID = id
    else:
        id = tempList.pop(0)
        tempID = id
    return tempID

def findKV(length,dict1):
    # findKV方法能找到所有的length=200（Value）的所有ID（Key），返回数组
    keyList=[]
    findKeyByValue = [k for k,v in dict1.items() if v == length]
    keyList.extend(findKeyByValue)
    tempList = keyList
    if len(tempList) >= 1:
        global dtKey
        dtKey = tempList.pop()
        del dict1[dtKey]
    return dtKey

def find_ID_list(sub_list,dict1):

    sub_list_A = copy.deepcopy(sub_list)
    for i in range(len(sub_list)):
        for j in range(len(sub_list[i])):
            temp_length = sub_list[i][j]
            #print(str(temp_length).isdigit())
            #if (str(temp_length)[-1]=='B'): #True
            if 'B' in str(temp_length):  # True
                del sub_list_A[i][j]

    for i in range(len(sub_list_A)):
        for j in range(len(sub_list_A[i])):
            ID_suffix = []
            temp_len=sub_list_A[i][j]
            temp_ID = int(re.sub("\((.+?)\)","",str(temp_len)))#int(re.sub("\D","",str(temp_len)))
            if isinstance(temp_len,str):
                pattern = re.compile("[a-zA-Z]")
                ID_suffix = pattern.findall(str(list(temp_len)))#list(temp_len)[-1]
            sub_list_A[i][j] = str(findKV(temp_ID,dict1)).strip("[").strip("]")+str(ID_suffix).strip("[").strip("]").strip("'")
            #print(sub_list_A[i][j])

    sub_ID_list = copy.deepcopy(sub_list_A)
    for i in range(len(sub_list_A)):
        for j in range(len(sub_list_A[i])):
            temp_oriLen = sub_list_A[i][j]
            temp_oriID = int(re.sub("\D", "", str(temp_oriLen)))
#            if (str(temp_oriLen)[-1] == 'A'):  # True
            if 'A' in str(temp_oriLen):  # True
                sub_ID_list[i+1].insert(0,str(temp_oriID)+'B')
    return sub_ID_list
#n = 10

#list1 = gen_list(n)


#list1 表示各段长度
#这个是超级长的暴躁版List,仅供测试娱乐
#list1 = [700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,11000,10200,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150,500,600,700,800,850,900,1000,1100,1200,750,760,810,3500,2000,6000,7000,8000,780,650,780,150]

#这个是正常测试长度，供调试
list1 = [8680, 1080, 4190, 9390, 4030, 2630, 11430, 8460, 8000, 4030, 2630, 11430, 8460, 8000, 2670]

#ID 表示各段编号，目前是生成顺序的数列，后续导入Tekla模型编号
ID_list = range(1,len(list1)+1)

# 将list列和ID列组合
dict1 = dict(zip(ID_list, list1))
originDict1 = dict(zip(ID_list, list1))


list1_last = []

t= 0
idx_status = 1

while idx_status == 1:
    print('迭代次数:',t)
    if sum_list(list1,len(list1))%12000 < 650: #切去最后一段
        [list1,list1_last]=slice_last(list1,12000)


    [idx_status, loc,sub_list] = evaluate_list(list1, 12000, 650)
    # print('状态：',idx_status)
    if idx_status == 1:
        if loc > 5:
            list1_a = list1[:loc - 5]
            list1_b = list1[loc - 5:]
            random.shuffle(list1_b)
            list1 = list1_a + list1_b
        else:
            random.shuffle(list1)
        # print(list1)
        t = t + 1
    else:

        if len(list1_last)>0:  # 切去最后一段
            sub_list.append(list1_last)
            print('另计最后单根构件，构件长度',list1_last)
        #--------------------------------------------------
        print('分段结果：',sub_list)#输出分段结果
        print('分段ID值：',find_ID_list(sub_list, dict1))
        print('原始字典：',originDict1)

        #--------------------------------------------------
        break


