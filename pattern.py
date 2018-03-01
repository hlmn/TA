from pypika import MySQLQuery, Table, Field, Order
import MySQLdb
import MySQLdb.cursors as cursors
from pprint import pprint
import time
import os
import datetime
import shlex, subprocess
import copy
import sys
import json
waktu = int(time.time())
# while True:
#     # print(waktu)
#     pass

# os.system("wget -O backup"+str(waktu)+".sql http://localhost/sisteminformasi/public/backup/get/structure")
# os.system("wget -O backup"+str(waktu)+".sql http://localhost:8000/backup/get/structure")
# os.system('mysql -u root -pliverpoolfc -e "DROP DATABASE IF EXISTS mmtitsbaru;"')
# os.system('mysql -u root -pliverpoolfc -e "CREATE DATABASE mmtitsbaru;"')
# os.system('mysql -u root -pliverpoolfc -e "SET GLOBAL FOREIGN_KEY_CHECKS=0;"')


# os.system('cat <(echo "SET FOREIGN_KEY_CHECKS=0;") imports.sql | mysql -u root')

# exit()
# os.system('mysql -u root -pliverpoolfc mmtitsbaru < backup'+str(waktu)+'.sql')

db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="information_schema") 
dbSelect = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="mmt-its")
dbInsert = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="mmtitsbaru")
key_column_usage = Table('key_column_usage')
# print key_column_usage.table_name
# exit()


tabel_master = 'kelas'
key_tabel_master = 'id_kelas'
kelas = 'IF-101'
# setFirst = dbSelect.cursor()
# master = Table(tabel_master)
# query = MySQLQuery.from_(master).select(master.star).where(
#     getattr(master, key_tabel_master) == kelas
# )
# setFirst.execute(str(query))
# if setFirst.rowcount < 1:
#     exit()
# query = MySQLQuery.into(tabel_master).insert(setFirst.fetchall()[0])
# setFirst = dbInsert.cursor()
# setFirst.execute(str(query))
# dbInsert.commit()

pattern = []
joinBoi = []


def findPattern(tabel, dari, join):
    if dari is None:
        dari = []
    if join is None:
        join = []
    q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name, Field('table_name'), key_column_usage.referenced_table_name, Field('column_name'),key_column_usage.referenced_column_name).orderby('constraint_name', order=Order.asc).where(
            key_column_usage.table_schema == 'mmt-its'
        ).where(
            (key_column_usage.referenced_table_name == tabel) | (Field('table_name') == tabel)
        )
    cur = db.cursor()
    cur.execute(str(q))
    cur = list(cur)
    count = 0 #parent
    countChild = 0
    index = 0
    primary = 0
    # print(cur)
    for i, row in enumerate(cur):
        if row[2] is None:
            index = index + 1
            # cur.remove(row)
            if row[0] == 'PRIMARY':
                primary = primary + 1
        if row[2] == tabel and row[2] != tabel_master:
            count = count + 1
            # print('a')
        if tabel == row[1] and row[1] != tabel_master:
            countChild = countChild + 1

    # print count
    fromRow = []
    joinRow = []
    # print(tabel)
    # print(cur)
    
    if index > 0:
        length = len(cur)-index
    else: 
        length = len(cur)
    # print(count)
    # exit(
    # if tabel == 'kelasmatkul':
    #     print('absen '+str(length)+' - '+str(count))
    #     exit()
    # print(length)
    if length != count:
        # if len(cur) != countChild:
        if count == 0 and primary > 0 and tabel is not tabel_master:
            # print('pucuk '+ tabel)
            # print(dari)
            pattern.append(dari)
            joinBoi.append(join)
            ujungChild = list(dari)
            del ujungChild[-1]
            pattern.append(ujungChild)
            joinChild = dict(join)
            del joinChild[tabel]
            joinBoi.append(joinChild)
        else:
            for i, row in enumerate(cur):
                # print(row)
                if row[2] is None: 
                    continue
                fromRow.append(list(dari))
                joinRow.append(dict(join))
                # print(dari)
                if row[2] == tabel:
                    if row[2] in fromRow[i]:
                        if row[1] not in fromRow[i]:
                            # print(tabel+'-'+row[2]+" > "+ row[1])
                            # print(row[2]+' start')
                            # print(row[3]+'-'+row[4])
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

                        # print(row[3]+'-'+row[4])
                        # print(row[1]+' start')
                        findPattern(row[1], fromRow[i], joinRow[i])
                        # print(row[1]+' done')
            # print(fromRow)
                else:
                    if row[2] in fromRow[i]:
                        # print('continue :'+row[1]+' - '+row[2])
                        continue
                    else:
                        # print(row[3]+'-'+row[4])
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
        # print('pucuk '+ tabel)
        # print(dari)
        pattern.append(dari)
        # exit()
        joinBoi.append(join)
    # if row.
    # db.close()
    return 1
def closeDB():
    dbInsert.close()
    dbSelect.close()
    db.close()

def insertToDb(result):
    listTabel = []
    setCursor = dbInsert.cursor()
    setCursor.execute('SET foreign_key_checks = 0')
    for i, j in enumerate(result):
        for key in j.keys():
            # print 
            if key not in listTabel:
                listTabel.append(key)
            cur = dbSelect.cursor()
            cur.execute(j[key]['selectQuery'])
            for row in cur:
                data = []
                for item in row:
                    if isinstance(item, int):
                        data.append(item)
                    else:
                        if item is None:
                            data.append(None)
                        else:
                            data.append(str(item))
                query = MySQLQuery.into(key).insert(data)
                print(str(query))
                try:
                    insertCursor = dbInsert.cursor()
                    # insertCursor.execute('SET foreign_key_checks = 0')
                    insertCursor.execute(str(query))
                    dbInsert.commit()
                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    print(e)
            # exit()
            # if key =='jadwal':
            #     exit()
    
    # pprint.pprint(listTabel)
    # exit()
    closeDB()
    f = open("statement.sql","w+")
    f.write('SET foreign_key_checks = 0;')
    for table in listTabel:
        f.write('CREATE TABLE tbl_new AS SELECT DISTINCT * FROM '+table+';LOCK TABLES '+table+' WRITE, tbl_new WRITE;truncate '+table+';insert '+table+' select * from tbl_new;drop table tbl_new;UNLOCK TABLES;')
    f.write('SET foreign_key_checks = 0;')
    f.close()
    cmd = 'mysql -u root -pliverpoolfc mmtitsbaru < statement.sql';
    args = shlex.split(cmd)
    p = os.system(cmd)

def main():   
    findPattern('kelas', None, None)
    oldpattern = []
    oldPattern = copy.deepcopy(pattern)
    # print(oldPattern)
    # exit()
    counter = 0
    jumlah = len(pattern)
    result = {}

    while (jumlah != counter):

        # print(pattern)
        # print(counter)
        insertPattern = list(pattern)
        insertJoin = list(joinBoi)
        for i, value in enumerate(insertPattern):
            # pprint(value)
            q = None
            if value:
                tbl = value[-1]
            joinnn = {}
            for j, row in reversed(list(enumerate(value))):
                if j == 0:
                    # if len(value)>1 :
                    #     q = q.select(Table(value[-1]).star).where(
                    #         getattr(Table(value[0]), key_tabel_master) == kelas
                    # )
                    if value:
                        del pattern[i][-1]
                    if not pattern[i]:
                        counter = counter + 1
                    continue;
                # if j == len(value)-1:

                #     tabel = Table(value[j])
                #     tabel1= Table(value[j-1])
                #     q = MySQLQuery.from_(tabel).join(
                #             tabel1
                #         ).on(
                #             getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                #         ).select(tabel.star)
                #     joinnn[row] = copy.deepcopy(insertJoin[i][row])
                #     # print(str(q))

                # else:
                #     q = q.join(
                #             Table(value[j-1])
                #         ).on(
                #             getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                #         )
                #     joinnn[row] = copy.deepcopy(insertJoin[i][row])
                joinnn[row] = copy.deepcopy(insertJoin[i][row])

            if len(value) > 0 :
                if tbl not in result.keys():
                    # print(tbl)
                    result[tbl] = {}
                    result[tbl]['pattern'] = []
                    result[tbl]['ref'] = []
                # pprint(value)
                if value in result[tbl]['pattern']:
                    continue
                result[tbl]['pattern'].append(list(value))
                result[tbl]['ref'].append(dict(joinnn))
                # pprint(result[tbl])p



                # result.append({
                #     tbl: {
                #         'selectQuery' : str(q)
                #     }
                # })
                # result()

    # insertToDb(result)
    # pprint(pattern)
    # pprint(result)
    # for j in result:
    #     result[j].sort(key=len)
    # print(result)
    
    pprint(result)
    exit()
    r = json.dumps(result)
    print(r)
    # sys.stdout.write(r)
    closeDB()
    # print(len(result))

if __name__ == "__main__":
    main()

