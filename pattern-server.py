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

db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="information_schema") 
key_column_usage = Table('key_column_usage')
manyToMany = {
    "dosenambilkelas" : {
        "kanan" : [
            'dosen'
        ],
        "kiri" : [
            'kelasmatkul'
        ]
    },
    "ambilkelas" : {
        "kanan" : [
            'mahasiswa'
        ],
        "kiri": [
           'kelasmatkul'
        ] 
    },
    "absen" : {
        "kanan" : [
            'mahasiswa',
            'kartu'
        ],
        "kiri": [
           'jadwal'
        ] 
    }

}

tabel_master = 'kelas'
key_tabel_master = 'id_kelas'
kelas = 'IF-101'
pattern = []
joinBoi = []

def findPattern(tabel, dari, join):
    if dari is None:
        dari = []
    if join is None:
        join = []
    q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name,
        Field('table_name'),
        key_column_usage.referenced_table_name,
        Field('column_name'),
        key_column_usage.referenced_column_name).orderby('constraint_name',
        order=Order.asc).where(
            key_column_usage.table_schema == 'mmt-its'
        ).where(
            (key_column_usage.referenced_table_name == tabel) | (Field('table_name') == tabel)
        )
    cur = db.cursor()
    cur.execute(str(q))
    cur = list(cur)
    count = 0 #parent
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

    fromRow = []
    joinRow = []
    
    if index > 0:
        length = len(cur)-index
    else: 
        length = len(cur)
    if length != count:
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
                            joinRow[i][row[1]] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                                
                            fromRow[i].append(row[1])
                            findPattern(row[1], fromRow[i], joinRow[i])
                        else:
                            if patternVerification(dari):
                                pattern.append(dari)
                                joinBoi.append(join)
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
                        else:
                            fromRow[i].append(row[2])
                            joinRow[i][row[2]] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                        findPattern(row[1], fromRow[i], joinRow[i])
                else:
                    if row[2] in fromRow[i]:
                        if patternVerification(dari):
                            pattern.append(dari)
                            joinBoi.append(join)
                        continue
                    else:
                        fromRow[i].append(row[2])
                        joinRow[i][row[2]] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                        findPattern(row[2], fromRow[i], joinRow[i])

    else:
        if patternVerification(dari):
            pattern.append(dari)
            joinBoi.append(join)
    return 1
def isManyToMany( tabel):
    q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name, Field('table_name'), key_column_usage.referenced_table_name, Field('column_name'),key_column_usage.referenced_column_name).orderby('constraint_name', order=Order.asc).where(
            key_column_usage.table_schema == 'mmt-its'
        ).where(
            (key_column_usage.referenced_table_name == tabel) | (Field('table_name') == tabel)
        )
    
    cur = db.cursor(cursors.DictCursor)
    cur.execute(str(q))
    refCount = 0
    length = 0
    for value in cur:
        # if value['constraint_name'] == 'PRIMARY':
        #     return False
        if value['referenced_table_name'] is not None:
            length += 1
            if value['table_name'] == tabel:
                refCount += 1
    if refCount == length:
        return True
    else:
        return False
def patternVerification( dari):
    for index, element in enumerate(dari):
        try:
            if isManyToMany(element):
                if dari[index-1] in manyToMany[element]['kiri'] and dari[index+1] in manyToMany[element]['kanan']:
                    continue
                else:
                    return False
        except IndexError as e:
            if isManyToMany(element):
                if dari[index-1] in manyToMany[element]['kiri']:
                    continue
                else:
                    return False
    # killDb()
    if dari in pattern:
        return False
    else:
        return True
def closeDB():
    db.close()

def main():   
    findPattern('kelas', None, None)
    oldpattern = []
    oldPattern = copy.deepcopy(pattern)
    counter = 0
    jumlah = len(pattern)
    result = {}

    while (jumlah != counter):
        insertPattern = list(pattern)
        insertJoin = list(joinBoi)
        for i, value in enumerate(insertPattern):
            q = None
            if value:
                tbl = value[-1]
            joinnn = {}
            for j, row in reversed(list(enumerate(value))):
                if j == 0:
                    if value:
                        del pattern[i][-1]
                    if not pattern[i]:
                        counter = counter + 1
                    continue;
                joinnn[row] = copy.deepcopy(insertJoin[i][row])

            if len(value) > 0 :
                if tbl not in result.keys():
                    result[tbl] = {}
                    result[tbl]['pattern'] = []
                    result[tbl]['ref'] = []
                if value in result[tbl]['pattern']:
                    continue
                result[tbl]['pattern'].append(list(value))
                result[tbl]['ref'].append(dict(joinnn))
    r = json.dumps(result)
    print(r)
    # sys.stdout.write(r)
    closeDB()
    # print(len(result))

if __name__ == "__main__":
    main()

