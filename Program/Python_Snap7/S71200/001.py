db=\
"""
Temperature Real 0.0
Cold Bool 4.0
"""
offsets = { "Bool":2,"Int": 2,"Real":4,"DInt":6,"String":256}
itemlist = filter(lambda a: a!='',db.split('\n'))

deliminator=' '

# for x in itemlist:
#     print(x)
items = [{"name": x.split(deliminator)[0],"datatype": x.split(deliminator)[1],"bytebit": x.split(deliminator)[2]} for x in itemlist]

print(items)


# [
# #     {'name': 'Temperature', 'datatype': 'Real', 'bytebit': '0.0'},
# #     {'name': 'Cold', 'datatype': 'Bool', 'bytebit': '4.0'},
# #     {'name': 'RPis_to_Buy', 'datatype': 'Int', 'bytebit': '6.0'},
# #     {'name': 'Db_test_String', 'datatype': 'String', 'bytebit': '8.0'}

seq,length = [x['bytebit'] for x in items],[x['datatype'] for x in items]
print(seq)
# ['0.0', '4.0', '6.0', '8.0']
print(length)
# ['Real', 'Bool', 'Int', 'String']

#获取索引值
idx = seq.index(max(seq))
print(idx)
# 3
length = int(max(seq).split('.')[0]) + (offsets[length[idx]])
print(length)



