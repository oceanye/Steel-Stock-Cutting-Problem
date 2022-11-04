
import Fixed_rank_rolls_v2
#这个是正常测试长度，供调试
list1 = [8680, 1080, 4180, 9390]

#ID 表示各段编号，目前是生成顺序的数列，后续导入Tekla模型编号
ID_list =[['1', '2'], ['3', '4', '5'], ['6', '7', '8', '9', '10', '11', '12', '13'], ['14', '15']]

Fixed_rank_rolls_v2.rank_rolls(list1,ID_list)
