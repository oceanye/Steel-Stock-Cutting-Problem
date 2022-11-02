import copy
#from import_section_table import args
#import argparse

args = -1

child = [5000, 5100, 5200, 5300, 5400, 5500]
ID = [12345, 32312, 312312, 323222, 23332, 32132]



if args>0:
    parent_length = args.length
else:
    parent_length = 12000


print("-****************************",parent_length)

global gap_cut
global gap_bar
gap_cut = 3
gap_bar = 0



pos_child = []
pos_bar = []


def sum_list(list1, loc_of_sum_list1):
    total = 0
    for i in range(loc_of_sum_list1):
        total = list1[i] + total
    return total

def insert_bar_cut(pos,temp_child,gap_bar):
    bar = round(pos / parent_length,0)
    for i in range(len(temp_child)):
        if temp_child[i] > pos:
            temp_child[i] = temp_child[i]+bar*gap_bar
    return temp_child

def split_bar(pos_child_barcut,pos_bar,bar_group):
    bar = []
    bar_last = []
    for i in range(len(bar_group)):
        temp = []
        if i>0:
            temp.append(pos_bar[i-1])
        if i == 0:
            temp.extend(pos_child_barcut[0:bar_group[0]])
        else:
            i_start = bar_group[i-1]
            i_end = bar_group[i]
            temp.extend(pos_child_barcut[i_start:i_end])
        temp.append(pos_bar[i])
        bar.append(temp)
    bar_last.append(pos_bar[-2])
    bar_last.extend(pos_child_barcut[bar_group[-1]:])
    bar.append(bar_last)

    for i in range(len(bar)):
        bar_start = bar[i][0]
        for j in range(len(bar[i])):
            bar[i][j]=bar[i][j]-bar_start


    return bar

#构件分段，不计整料分缝
for i in range(len(child)+1):
    if i == 0:
        pos_child.append(0)
    else:
        pos_child.append(sum_list(child, i)+gap_cut/2+(i-1)*gap_cut)

#统计总根数
numb_bar = round((pos_child[-1]+len(child)*gap_bar)/parent_length)+1

#考虑整料分缝
pos_child_barcut = copy.deepcopy(pos_child)
for i in range(1,numb_bar):
    pos_child_barcut = insert_bar_cut(parent_length*(i), pos_child_barcut, gap_bar)
    pos_bar.append(parent_length*i+gap_cut*(i-1)+gap_cut/2)

#整合切断点位置
bar_group=[]
for i in range(len(pos_bar)):
    for j in range(len(pos_child_barcut)):
        if pos_child_barcut[j]>pos_bar[i]:
            bar_group.append(j)
            break

#拆分整料
bar = split_bar(pos_child_barcut,pos_bar,bar_group)

#-----考虑构件分段，每根零件间隙3mm-----#
print('考虑构件分段',sum_list(child, len(child)))

#-----考虑构件分段，每根零件间隙3mm-----#
print('考虑构件分段切割锯缝 pos_child = ',pos_child)

#-----考虑整料分段，每根整料间隙3mm-----#
print('考虑整料切割锯缝 pos_child_barcut=',pos_child_barcut)

#-----整料切断位置-------#
print('考虑整料切段点 pos_bar=',pos_bar)

#------锯料损耗---------#
print('锯料损耗',(numb_bar-1)*gap_bar+(len(child)-1)*gap_cut)

#------整料分组结果-----#
print('整料分组',bar_group)
print('分组长度',bar)