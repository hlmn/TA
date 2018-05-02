import MySQLdb
import MySQLdb.cursors as cursors
from Pattern import Pattern
import datetime
from pprint import pprint
import uuid
from pypika import MySQLQuery, Table, Field, Order, functions as fn, JoinType
import time

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
    print(str( jadwalBaru))
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
def ambilkelas(queryMahasiswa, whereJadwal):
    # print(queryMahasiswa)
    # print(whereJadwal)
    queryTotal = ' UNION '.join(queryMahasiswa)
    print('aaa : '+queryTotal)
    getMahasiswaLain = 'select * from mahasiswa where `mahasiswa`.`nrp` not in (select e.nrp from (' + queryTotal + ') as e)'
    print(getMahasiswaLain)

def main():
    query = 'select distinct jadwal.id_kelas from jadwal'
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute(query)
    while True:
        for row in cursor:
            hasilPattern, where = getQuery(row)
            absen(hasilPattern['kartu'], where['id_jadwal'])
            # ambilkelas(hasilPattern['mahasiswa'], where)
                
            # print()
  
if __name__== "__main__":
    ptrn = Pattern()
    ptrn.findPattern('kelas', None, None)
    ptrn.main()
    main()