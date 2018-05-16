import MySQLdb
import MySQLdb.cursors as cursors
from Pattern import Pattern
import datetime
from pprint import pprint
import uuid
from pypika import MySQLQuery, Table, Field, Order, functions as fn, JoinType
import time
import json
import os
import socket
counter = 0   

def getQuery(row):
    
    query = 'SELECT * FROM jadwal where jadwal.id_kelas = \'' + row['id_kelas'] + '\' ORDER BY jadwal.id_jadwal ASC LIMIT 1'
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
    global counter
    counter += 1
    cursor = db.cursor()
    cursor.execute(str(jadwalBaru))
    db.commit()
    return listOfPattern, where

def absen(queryKartu, id_jadwal):
    global counter
    
    queryTotal = ' UNION '.join(queryKartu)
    # print(id_jadwal)
    # print(queryTotal)
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
        # print(str(absen))
        counter += 1
        cursor = db.cursor()
        cursor.execute(str(absen))
        db.commit()
        # exit()
def ambilkelas(queryMahasiswa, whereJadwal):
    global counter
    
    queryTotal = ' UNION '.join(queryMahasiswa)
    queryTotal = queryTotal.replace(socket.gethostname(), whereJadwal['id_kelas'])
    
    getMahasiswaLain = 'select * from mahasiswa where `mahasiswa`.`nrp` not in (select e.nrp from (' + queryTotal + ') as e) ORDER BY mahasiswa.nrp ASC LIMIT 3'
    # print(getMahasiswaLain)
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(str(getMahasiswaLain))
    for row in cursor:
        query = MySQLQuery.into('ambilkelas').insert(whereJadwal['id_kelas_matkul'], row['nrp'])
        print(str(query))
        counter += 1
        cursor = db.cursor()
        cursor.execute(str(query))
        db.commit()
def updateKelasMatkul(queryKelasMatkul, whereJadwal):
    global counter
    
    queryTotal = ' UNION '.join(queryKelasMatkul)
    queryTotal = queryTotal.replace(socket.gethostname(), whereJadwal['id_kelas'])

    getKodeKelas = 'select * from kode_kelas where `kode_kelas`.`id_kode_kelas` not in (select e.id_kode_kelas from (' + queryTotal + ') as e) ORDER BY kode_kelas.id_kode_kelas ASC  LIMIT 1'
    # query = queryTotal
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(str(getKodeKelas))
    hasilKodeKelas = cursor.fetchall()
    for row in hasilKodeKelas:
        getKelasMatkul = queryTotal + ' ORDER BY kelasmatkul.id_kelas_matkul ASC LIMIT 1'
        cursor = db.cursor(cursors.DictCursor)
        cursor.execute(str(getKelasMatkul))
        hasilKelasMatkul = cursor.fetchall()
        for row2 in hasilKelasMatkul:
            update = "update kelasmatkul set id_kode_kelas = '"+row['id_kode_kelas']+"' where id_kelas_matkul = '"+row2['id_kelas_matkul']+"'"
            print(update)
            counter += 1
            cursor = db.cursor()
            cursor.execute(update)
            db.commit()
        
def updateJadwal(whereJadwal):
    global counter
    
    query = "select kelasmatkul.id_kelas_matkul from kelasmatkul where id_kelas_matkul not in (select distinct jadwal.id_kelas_matkul from jadwal where jadwal.id_kelas = '"+whereJadwal['id_kelas']+"') ORDER BY kelasmatkul.id_kelas_matkul ASC LIMIT 1"
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    for row in cursor:
        update = "UPDATE JADWAL SET id_kelas_matkul = '"+row['id_kelas_matkul']+"' WHERE id_jadwal = '"+whereJadwal['id_jadwal']+"'"
        print(update)
        counter += 1
        cursor = db.cursor()
        cursor.execute(update)
        db.commit()

def deleteJadwal(whereJadwal):
    global counter
    
    query = "select jadwal.id_jadwal from jadwal where jadwal.id_kelas ='"+whereJadwal['id_kelas']+"' and id_kelas_matkul != '"+whereJadwal['id_kelas_matkul']+"' ORDER BY jadwal.id_jadwal ASC LIMIT 1"
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    for row in cursor:
        delete = "DELETE FROM jadwal where id_jadwal = '"+row['id_jadwal']+"'"
        counter += 1
        print(delete)
        cursor = db.cursor()
        cursor.execute(delete)
        db.commit()


def main():


    query = 'select distinct jadwal.id_kelas from jadwal ORDER BY jadwal.id_kelas ASC'
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    
    # while True:
    # log = '{"database":"mmt-its","table":"absen","type":"insert","ts":1525257612,"xid":1927081,"commit":true,"position":"master.000006:43124064","data":{"id_absen":"d750c546-dee6-4228-8a91-faef298dfe5b","id_kartu":null,"id_jadwal":"da2a6bd1-b4d0-455d-8a32-362bb41f07b3","waktu_absen":"2018-05-02 17:40:12","nrp":"9211750014008"}}'
    # log = json.loads(log)
    # result, ref = ptrn.getTablePattern(log['table'])
    # listOfPattern = ptrn.buildQuery(result, ref, log['data'], log['table'])
    # pprint(listOfPattern)
    limit = 0;
    
    while limit < 50:
        for row in cursor:
            print(row['id_kelas'])
            hasilPattern, where = getQuery(row)
            # time.sleep(0.5)
            # print(hasilPattern['absen'])
            
            absen(hasilPattern['kartu'], where['id_jadwal'])
            # time.sleep(0.5)
            # # print()
            ambilkelas(ptrn.dictOfPattern['mahasiswa']['query'], where)
            # time.sleep(0.5)
            # exit()
            updateJadwal(where)
            # time.sleep(0.5)
            deleteJadwal(where)
            updateKelasMatkul(ptrn.dictOfPattern['kelasmatkul']['query'], where)
            # time.sleep(0.5)

            print('\n')
            # exit()
        limit += 1
        # exit()
    
if __name__== "__main__":
    awal = time.time()
    # cursor = db.cursor()
    # cursor.execute('select * from jadwal')
    # print(cursor.rowcount)
    # os.system("redis-cli flushall")
    # os.system("mysql -u root -pliverpoolfc -e 'DROP DATABASE IF EXISTS `mmt-its`;'")
    # os.system("mysql -u root -pliverpoolfc -e 'CREATE DATABASE `mmt-its`;'")
    # os.system('mysql -u root -pliverpoolfc -e "SET GLOBAL FOREIGN_KEY_CHECKS=0;"')
    # # db.close()
    # os.system('mysql -u root -pliverpoolfc mmt-its < baru.sql')
    # os.system('mysql -u root -pliverpoolfc -e "SET GLOBAL FOREIGN_KEY_CHECKS=1;"')
    # os.system('python replicateInServer.py')
    # os.system("redis-cli flushall")
    # # exit()
    
    db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="liverpoolfc",  # your password
                     db="mmt-its")
       
    ptrn = Pattern()
    ptrn.findPattern('kelas', None, None)
    ptrn.main()
    main()
    print counter
    print ((time.time()-awal)/60)