from pypika import MySQLQuery, Table, Field, Order
import MySQLdb
import MySQLdb.cursors as cursors
import pprint
db = MySQLdb.connect(host="db.muhammadhilman.com",    # your host, usually localhost
                     user="hlmn",         # your username
                     passwd="liverpoolfc",  # your password
                     db="information_schema") 
key_column_usage = Table('key_column_usage')
# print key_column_usage.table_name
# exit()
tabel_master = 'kelas'
# def goblok1(row):
pattern = []
joinBoi = []
# def goblok2(row):

def findPattern(tabel, dari, join):
    if dari is None:
        dari = []
    if join is None:
        join = []
    # else:
    #     print(dari)
    q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name, Field('table_name'), key_column_usage.referenced_table_name, Field('column_name'),key_column_usage.referenced_column_name).orderby('table_name', order=Order.asc).where(
            key_column_usage.table_schema == 'mmt-its'
        ).where(
            key_column_usage.referenced_table_name.notnull()
        ).where(
            (key_column_usage.referenced_table_name == tabel) | (Field('table_name') == tabel)
        )
    cur = db.cursor()
    cur.execute(str(q))
    cur = list(cur)
    count = 0 #parent
    countChild = 0
    # print(cur)
    for row in cur:
        if row[2] == tabel and row[2] != tabel_master:
            count = count + 1
        if tabel == row[1] and row[1] != tabel_master:
            countChild = countChild + 1

    # print count
    fromRow = []
    joinRow = []
    # print(tabel)
    # print(cur)
    

    if len(cur) != count:
        # if len(cur) != countChild:
        for i, row in enumerate(cur):
            # print(row)
            fromRow.append(list(dari))
            joinRow.append(dict(join))
            # print(dari)
            if row[2] == tabel:
                if row[2] in fromRow[i]:
                    if row[1] not in fromRow[i]:
                        # print(tabel+'-'+row[2]+" > "+ row[1])
                        # print(row[2]+' start')
                        print(row[3]+'-'+row[4])
                        joinRow[i][row[1]] = {
                            'table_name' : row[1],
                            'column_name' : row[3],
                            'referenced_table_name' : row[2],
                            'referenced_column_name' : row[4]
                        }
                            
                        fromRow[i].append(row[1])
                        findPattern(row[1], fromRow[i], joinRow[i])
                        # print('continue :'+row[1]+' - '+row[2])
                    else:
                        continue 
                else:
                    if row[2] == tabel_master:
                        if len(dari) == 0:
                            fromRow[i].append(tabel_master)
                            joinRow[i][tabel_master] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                        fromRow[i].append(row[1])
                        joinRow[i][row[1]] = {
                            'table_name' : row[1],
                            'column_name' : row[3],
                            'referenced_table_name' : row[2],
                            'referenced_column_name' : row[4]
                        }
                        # print('pindah ke '+row[1]+' dari '+tabel_master)
                    # elif row[1]:
                        # print('babik '+row[2])
                    else:
                        # print('anjeng')
                        fromRow[i].append(row[2])
                        joinRow[i][row[2]] = {
                            'table_name' : row[1],
                            'column_name' : row[3],
                            'referenced_table_name' : row[2],
                            'referenced_column_name' : row[4]
                        }
                        # print('pindah ke '+fromRow[i][-1]+' dari '+row[1])
                    # fromRow[i].append(row[2])

                    print(row[3]+'-'+row[4])
                    # print(row[1]+' start')
                    findPattern(row[1], fromRow[i], joinRow[i])
                    # print(row[1]+' done')
        # print(fromRow)
            else:
                if row[2] in fromRow[i]:
                    # print('continue :'+row[1]+' - '+row[2])
                    continue
                else:
                    print(row[3]+'-'+row[4])
                    fromRow[i].append(row[2])
                    joinRow[i][row[2]] = {
                            'table_name' : row[1],
                            'column_name' : row[3],
                            'referenced_table_name' : row[2],
                            'referenced_column_name' : row[4]
                        }
                    # print(tabel+'-'+row[2]+" > "+ row[1])
                    # print(row[2]+' start')
                    findPattern(row[2], fromRow[i], joinRow[i])
                    # print(row[2]+' done')

    else:
        print('pucuk '+ tabel)
        print(dari)
        pattern.append(dari)
        # exit()
        joinBoi.append(join)
    # if row.
    # db.close()
    return 1

# dari = []
# if dari is None:
#     print('goblok')

findPattern('kelas', None, None)
# pattern.sort(key=len)
# 
pprint.pprint(pattern)
# pprint.pprint(joinBoi)
#tes
# pprint.pprint(joinBoi)
# # pprint(list(joinBoi.values()))
# print(len(pattern))
# for i, value in enumerate(pattern):
#     q = None
#     # print(value)
#     for j, row in reversed(list(enumerate(value))):
#         # print(row+', ')
#         # print j
#         if j == 0:
#             continue;
#         if j == len(value)-1:
#             # q = 
#             # print("select "+value[j])
#             # print("from "+value[j])
#             # print("inner join "+value[j-1])
#             # print("on "+joinBoi[i][row]['table_name']+'.'+joinBoi[i][row]['column_name']+'='+joinBoi[i][row]['referenced_table_name']+'.'+joinBoi[i][row]['referenced_column_name'])
#             field1 = Field(joinBoi[i][row]['column_name'], alias=None, table=joinBoi[i][row]['table_name'])
#             field2 = Field(joinBoi[i][row]['referenced_column_name'], alias=None, table=joinBoi[i][row]['referenced_table_name'])
#             tabel = Table(value[j])
#             tabel1= Table(value[j-1])
#             q = MySQLQuery.from_(tabel).join(
#                     tabel1
#                 ).on(
#                     getattr(Table(joinBoi[i][row]['table_name']), joinBoi[i][row]['column_name']) == getattr(Table(joinBoi[i][row]['referenced_table_name']), joinBoi[i][row]['referenced_column_name'])
#                 ).select(tabel.star)
#             # print(str(q))

#         else:
#             q = q.join(
#                     Table(value[j-1])
#                 ).on(
#                     getattr(Table(joinBoi[i][row]['table_name']), joinBoi[i][row]['column_name']) == getattr(Table(joinBoi[i][row]['referenced_table_name']), joinBoi[i][row]['referenced_column_name'])
#                 )
#             # print(j-1)
#             # print("inner join "+value[j-1])
#             # print("on "+joinBoi[i][row]['table_name']+'.'+joinBoi[i][row]['column_name']+'='+joinBoi[i][row]['referenced_table_name']+'.'+joinBoi[i][row]['referenced_column_name'])
#     # print(str(q))
#     q = q.select(Table(value[-1]).star).where(
#             getattr(Table(value[0]), "id_kelas") == "IF-101"
#         )
#     print(str(q))         

    # print('\n')
    


db.close()
