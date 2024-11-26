

def single_component(w1,b1,ID3):
    consumed_big_rolls=[]
    consumed_sub_rolls=[]
    demand_sub_rolls=[]
    #consumed_sub_rolls的第i项，为[0, b1的对应项, [b1的对应项]]
    #历遍b1，生成consumed_sub_rolls的第i项，为[0, b1的对应项, [b1的对应项]]
    for i in range(len(ID3)):
        for j in range(len(ID3[i])):

            consumed_sub_rolls.append([[w1[i]]])
            consumed_big_rolls.append([1,w1[i],consumed_sub_rolls[i][0]])
            demand_sub_rolls.append([[ID3[i][j]]])
            #ID3[i].pop(0)
    # print(consumed_sub_rolls)
    # print(w1)
    # print(b1)
    # print(ID3)

    return (consumed_big_rolls,consumed_sub_rolls,demand_sub_rolls)
