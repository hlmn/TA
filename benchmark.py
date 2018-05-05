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
db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="mmt-its")

def getQuery(row):
    query = 'SELECT * FROM jadwal where jadwal.id_kelas = \'' + row['id_kelas'] + '\' ORDER BY RAND() LIMIT 1'
    where = {}
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    row = cursor.fetchone()
    for key in row.keys():
        if isinstance(row[key], datetime.date):
            where[key] = str(row[key])
        elif isinstance(row[key], datetime.timedelta):
            where[key] = str(row[key])
        else:
            where[key] = row[key]
    result, ref = ptrn.getTablePattern('jadwal')
    listOfPattern = ptrn.buildQuery(result, ref, where, 'jadwal')
    # print(where.values())
    print(where['id_jadwal'])
    where['id_jadwal'] = str(uuid.uuid4())
    print(where['id_jadwal'])
    jadwalBaru = MySQLQuery.into('jadwal').insert(where.values())
    for i in where.keys():
        jadwalBaru = jadwalBaru.columns(i)
    print(str(jadwalBaru))
    cursor = db.cursor()
    cursor.execute(str(jadwalBaru))
    db.commit()
    return listOfPattern, where

def absen(queryKartu, id_jadwal):
    queryTotal = ' UNION '.join(queryKartu)
    # print(id_jadwal)
    print(queryTotal+'\n')
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(queryTotal)
    # print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    for row in cursor:
        absen = MySQLQuery.into('absen').insert([
            str(uuid.uuid4()),
            None,
            id_jadwal,
            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            row['nrp']
        ])
        print(str(absen))
        cursor = db.cursor()
        cursor.execute(str(absen))
        db.commit()
        exit()
def ambilkelas(queryMahasiswa, whereJadwal):
    queryTotal = ' UNION '.join(queryMahasiswa)
    queryTotal = queryTotal.replace(socket.gethostname(), whereJadwal['id_kelas'])
    
    getMahasiswaLain = 'select * from mahasiswa where `mahasiswa`.`nrp` not in (select e.nrp from (' + queryTotal + ') as e)  ORDER BY RAND() LIMIT 3'
    print(getMahasiswaLain)
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(str(getMahasiswaLain))
    for row in cursor:
        query = MySQLQuery.into('ambilkelas').insert(whereJadwal['id_kelas_matkul'], row['nrp'])
        print(str(query))
        cursor = db.cursor()
        cursor.execute(str(query))
        db.commit()



def main():
    query = 'select distinct jadwal.id_kelas from jadwal'
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    # while True:
    # log = '{"database":"mmt-its","table":"absen","type":"insert","ts":1525257612,"xid":1927081,"commit":true,"position":"master.000006:43124064","data":{"id_absen":"d750c546-dee6-4228-8a91-faef298dfe5b","id_kartu":null,"id_jadwal":"da2a6bd1-b4d0-455d-8a32-362bb41f07b3","waktu_absen":"2018-05-02 17:40:12","nrp":"9211750014008"}}'
    # log = json.loads(log)
    # result, ref = ptrn.getTablePattern(log['table'])
    # listOfPattern = ptrn.buildQuery(result, ref, log['data'], log['table'])
    # pprint(listOfPattern)
    for row in cursor:
        hasilPattern, where = getQuery(row)
        # print(hasilPattern['absen'])
        absen(hasilPattern['kartu'], where['id_jadwal'])
        # # print()
        ambilkelas(ptrn.dictOfPattern['mahasiswa']['query'], where)
  
if __name__== "__main__":
    ptrn = Pattern()
    ptrn.findPattern('kelas', None, None)
    ptrn.main()
    main()