list = ['1 abc','2 dbe','3 efg']
num_list = []
counter = 0
while counter < len(list):
    num = list[counter]
    length = len(num)
    c = 0
    while c < length:
        try:
            ele = num[c]
            integer = int(ele)
            num_list.append(integer)
            c = c + 1
        except Exception as e:
            #print(e)
            c = c + 1
    counter = counter+1
print(num_list)
