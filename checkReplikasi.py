import MySQLdb
import MySQLdb.cursors as cursors
from Pattern import Pattern
import datetime
from pprint import pprint
import uuid
from pypika import MySQLQuery, Table, Field, Order, functions as fn, JoinType
import time
import json
import socket
from openpyxl import Workbook
import copy
import requests

db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="mmt-its")
mesin = MySQLdb.connect(host="192.168.0.33",
                     user="root",         # your username
                     passwd="mmtitsmmtits",  # your password
                     db="mmtitsbaru")

ptrn = Pattern()
ptrn.findPattern('kelas', None, None)
ptrn.main()

blacklist = [
    'kelas',
    'mesin_log'
]


listTable = {}

def check(query, tableName, ip, id_kelas):
    mesin = MySQLdb.connect(host=str(ip),
                     user="root",         # your username
                     passwd="mmtitsmmtits",  # your password
                     db="mmtitsbaru")
    cursor = db.cursor()
    cursor.execute(query)
    hasil = list(cursor.fetchall())

    query = 'select * from '+tableName
    cursor = mesin.cursor()
    cursor.execute(query)
    cursor = list(cursor.fetchall())
    jumlahDiServer = len(hasil)
    jumlahDiMesin = len(cursor)
    print('Jumlah di Server : '+ str(jumlahDiServer))
    print('Jumlah di Mesin : '+ str(jumlahDiMesin))    
    # for row in cursor:
    #     if row not in hasil:
    #         print(row)
    for row in hasil:
        if row not in cursor:
            # print(row)
            pass
    # if jumlahDiMesin != jumlahDiServer:
    print('Perbedaan Data : ' + str(+(jumlahDiMesin-jumlahDiServer)))
    
    if id_kelas not in listTable:
        listTable[id_kelas] = {}
    listTable[id_kelas][tableName] =  +(jumlahDiMesin-jumlahDiServer)





tables = "SELECT table_name FROM information_schema.tables where table_schema='mmt-its'"

cursor = db.cursor(cursors.DictCursor)
cursor.execute(tables)

r = requests.get('http://localhost:9999/get/ruangan')
# print(r.text)
result = json.loads(r.text)
# pprint(result)


for id_kelas in result['ruangan']:
    print(id_kelas)
    for socketId in result['ruangan'][id_kelas]:
        # print(socket)
        print(result['ip'][socketId])
        for row in cursor:
            if row['table_name'] in blacklist:
                continue
            print(row['table_name'])
            query = copy.deepcopy(ptrn.dictOfPattern[row['table_name']]['query'])
            query =  ' UNION '.join(query)
            query = query.replace(socket.gethostname(), str(id_kelas))
            # print(query + '\n')
            check(query, row['table_name'], result['ip'][socketId], id_kelas)
            print('')
    print('')
# exit()
print(listTable)
    # exit()

wb = Workbook()
ws = wb.active
header = ['Nama Tabel']
for key in listTable:
    header.append(key)
ws.append(header)

for row in cursor:
    if row['table_name'] in blacklist:
        continue
    baris = [row['table_name']]
    for key in listTable:
        baris.append(listTable[key][row['table_name']])
    ws.append(baris)


wb.save("checkData.xlsx")