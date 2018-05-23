from pypika import MySQLQuery, Table, Field, Order, functions as fn, JoinType
import MySQLdb
import MySQLdb.cursors as cursors
from pprint import pprint
import time
import os
import datetime
import shlex, subprocess
import copy
import sys
import socket
import json
# while True:
#     # print(waktu)
#     pass
# dir_path = os.path.dirname(os.path.realpath(__file__))
# f = open(dir_path+"/ip.txt", 'r')
# print(dir_path+"/ip.txt")
# ipPusat = f.read()
# ipPusat = ipPusat.rstrip()
ipPusat = '127.0.0.1'
# os.system("wget -O backup"+str(waktu)+".sql http://localhost/sisteminformasi/public/backup/get/structure")
# os.system("wget -O backup"+str(waktu)+".sql http://localhost:8000/backup/get/structure")
# os.system('mysql -u root -pliverpoolfc -e "DROP DATABASE IF EXISTS mmt-its;"')
# os.system('mysql -u root -pliverpoolfc -e "CREATE DATABASE mmt-its;"')
# os.system('mysql -u root -pliverpoolfc -e "SET GLOBAL FOREIGN_KEY_CHECKS=0;"')


# os.system('cat <(echo "SET FOREIGN_KEY_CHECKS=0;") imports.sql | mysql -u root')

# exit()
class DB:
  conn  = None
  host  = None
  user  = None
  password = None
  db    = None
  def __init__(self, host, user, password, db):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
  def __del__(self):
    # print "deleted"
    pass
  def connect(self):
    try:
        if self.password is None:
            self.conn = MySQLdb.connect(
                host = self.host,
                user = self.user,
                db=self.db)
        else:
            self.conn = MySQLdb.connect(
                host = self.host,
                user = self.user,
                db=self.db,
                passwd = self.password)
        
    except Exception as e:
        raise Exception(e)
  def close(self):
    self.conn.close()

  def query(self, sql, cur = None):
    try:
        if cur is None:
            cursor = self.conn.cursor()
        else:
            cursor = self.conn.cursor(cur)
        cursor.execute(sql)        
    except (AttributeError, MySQLdb.OperationalError) as e:
        # print('asoy')
        print(e)
        self.connect()
        return self.query(sql, cur)
    except (MySQLdb.Error, MySQLdb.Warning) as e:

        if e[0] == 0:
            self.connect()
            return self.query(sql, cur)

        print(str(e)+' anja')
        return e
    # except (AttributeError, MySQLdb.OperationalError, MySQLdb.Error, MySQLdb.Warning) as e:
    #     if e[0] == 1062:
    #         print(e)
    #         return cursor
    #         # return self.query(sql)
    #     self.connect()
    #     return self.query(sql)
        # return self.query(sql)
      
      # cursor = self.conn.cursor()
      # cursor.execute(sql)
    # print(cursor.fetchall())
    return cursor
  def commit(self):
    self.conn.commit()
  # def rowcount(self):
  #   return self.conn.rowcount
# os.system('mysql -u root -pliverpoolfc mmt-its < backup'+str(waktu)+'.sql')
db = MySQLdb.connect(host="127.0.0.1",
                         user="root",         # your username
                         passwd="liverpoolfc",  # your password
                         db="information_schema") 
# dbSelect = MySQLdb.connect(host="192.168.0.13",
#                      user="root",         # your username
#                      passwd="liverpoolfc",  # your password
#                      db="mmt-its")
# dbInsert = MySQLdb.connect(host="127.0.0.1",
#                      user="root",         # your username
#                      # passwd="liverpoolfc",  # your password
#                      db="mmt-its")
key_column_usage = Table('key_column_usage')
# print key_column_usage.table_name
# exit()


tabel_master = 'kelas'
key_tabel_master = 'id_kelas'
kelas = socket.gethostname()

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

class Pattern:
    primaryKey = {}
    pattern = []
    joinBoi = []
    dictOfPattern = {}
    dbInsert = None
    dbSelect = None
    def __init__(self):

        self.dbInsert = DB(
                    '127.0.0.1',
                    'root',
                    'liverpoolfc',
                    'mmt-its'
                )
        self.dbSelect = DB(
                    ipPusat,
                    'root',
                    'liverpoolfc',
                    'liverpoolfc'
                    'mmt-its'
                )

        # print(self.dbSelect)
    def findPattern(self, tabel, dari, join, restrict = None):
        if restrict is None:
            restrict = []
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
        # print(str(q))
        cur = list(cur)
        count = 0 #parent
        countChild = 0
        index = 0
        fromRow = []
        joinRow = []
        restrictRow = []
        primary = 0
        # print(cur)
        for i, row in enumerate(cur):
            if row[2] is None:
                index = index + 1
                # cur.remove(row)
                if row[0] == 'PRIMARY':
                    primary = primary + 1
                    self.primaryKey[row[1]] = row[3]
            # else:
            #     if row[1] == tabel:
            #         fromRow.append()
            if row[2] == tabel and row[2] != tabel_master:
                count = count + 1
                # print('a')
            if tabel == row[1] and row[1] != tabel_master:
                countChild = countChild + 1

        # print count
        
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
            # if count == 0 and primary > 0 and tabel is not tabel_master:
            #     # print(dari)
            #     if self.patternVerification(dari):
            #         self.pattern.append(dari)
            #         self.joinBoi.append(join)
            #         ujungChild = list(dari)
            #         del ujungChild[-1]
            #         self.pattern.append(ujungChild)
            #         joinChild = dict(join)
            #         del joinChild[tabel]
            #         self.joinBoi.append(joinChild)
            # else:
            for i, row in enumerate(cur):
                # print(row)
                if row[2] is None: 
                    continue
                fromRow.append(list(dari))
                joinRow.append(dict(join))
                restrictRow.append(list(restrict))

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
                            for idx, test in enumerate(cur):
                                if test[2] is not None:
                                    if test[1] == tabel:
                                        restrictRow[i].append(test[2])
                                    else:
                                        restrictRow[i].append(test[1])
                            fromRow[i].append(row[1])
                            self.findPattern(row[1], fromRow[i], joinRow[i], restrictRow[i])
                            # print('continue :'+row[1]+' - '+row[2])
                        else:
                            if self.patternVerification(dari):
                                self.pattern.append(dari)
                                self.joinBoi.append(join)
                            continue 
                    else:
                        if row[2] == tabel_master:
                            if len(dari) == 0:
                                for idx, test in enumerate(cur):
                                    if test[2] is not None:
                                        if test[1] == tabel:
                                            restrictRow[i].append(test[2])
                                        else:
                                            restrictRow[i].append(test[1])
                                fromRow[i].append(tabel_master)
                                joinRow[i][tabel_master] = {
                                    'table_name' : row[1],
                                    'column_name' : row[3],
                                    'referenced_table_name' : row[2],
                                    'referenced_column_name' : row[4]
                                }
                            for idx, test in enumerate(cur):
                                if test[2] is not None:
                                    if test[1] == tabel:
                                        restrictRow[i].append(test[2])
                                    else:
                                        restrictRow[i].append(test[1])
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
                            for idx, test in enumerate(cur):
                                if test[2] is not None:
                                    if test[1] == tabel:
                                        restrictRow[i].append(test[2])
                                    else:
                                        restrictRow[i].append(test[1])
                            fromRow[i].append(row[2])
                            joinRow[i][row[2]] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                            # print('pindah ke '+fromRow[i][-1]+' dari '+row[1])

                        # print(row[3]+'-'+row[4])
                        # print(row[1]+' start')
                        self.findPattern(row[1], fromRow[i], joinRow[i], restrictRow[i])
                        # print(row[1]+' done')
            # print(fromRow)
                else:
                    if row[2] in fromRow[i]:
                        # print('continue :'+row[1]+' - '+row[2])
                        if self.patternVerification(dari):
                            self.pattern.append(dari)
                            self.joinBoi.append(join)
                        continue
                    else:
                        # print(row[3]+'-'+row[4])
                        for idx, test in enumerate(cur):
                            if test[2] is not None:
                                if test[1] == tabel:
                                    restrictRow[i].append(test[2])
                                else:
                                    restrictRow[i].append(test[1])
                        fromRow[i].append(row[2])
                        joinRow[i][row[2]] = {
                                'table_name' : row[1],
                                'column_name' : row[3],
                                'referenced_table_name' : row[2],
                                'referenced_column_name' : row[4]
                            }
                        # print(tabel+'-'+row[2]+" > "+ row[1])
                        # print(row[2]+' start')
                        self.findPattern(row[2], fromRow[i], joinRow[i], restrictRow[i])
                        # print(row[2]+' done')

        else:
            # print('pucuk '+ tabel)
            # print(dari)
            if self.patternVerification(dari):
                self.pattern.append(dari)
                # exit()
                self.joinBoi.append(join)
        # if row.
        # db.close()
        return 1
    def isManyToMany(self, tabel):
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
    def patternVerification(self, dari):
        for index, element in enumerate(dari):
            try:
                if self.isManyToMany(element):
                    if dari[index-1] in manyToMany[element]['kiri'] and dari[index+1] in manyToMany[element]['kanan']:
                        continue
                    else:
                        return False
            except IndexError as e:
                if self.isManyToMany(element):
                    if dari[index-1] in manyToMany[element]['kiri']:
                        continue
                    else:
                        return False
        # self.killDb()
        if dari in self.pattern:
            return False
        else:
            return True
    def getRef(self, table):
        q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name, Field('table_name'), key_column_usage.referenced_table_name, Field('column_name'),key_column_usage.referenced_column_name).orderby('constraint_name', order=Order.asc).where(
                key_column_usage.table_schema == 'mmt-its'
            ).where(
                (key_column_usage.referenced_table_name == table) | (Field('table_name') == table)
            )
        
        cur = db.cursor(cursors.DictCursor)
        cur.execute(str(q))
        result = []
        refCount = 0
        length = 0
        for value in cur:
            if value['referenced_table_name'] is not None:
                length += 1
                result.append(value)
                # if value['table_name'] == element:
                #     refCount += 1
        return result
    


    def closeDB(self):
        # dbInsert.close()
        # dbSelect.close()
        try:
            db.close()
        except:
            return 1
    def getTablePattern(self, tableTarget):
        # self.pattern
        tablePattern = list(self.pattern)
        joinBoiPattern = list(self.joinBoi)
        # exit()
        result = []
        joinResult = []
        for idx1, i in enumerate(tablePattern):
            if tableTarget in i:
                index = i.index(tableTarget)
                if tableTarget in self.primaryKey:
                    if i[index:] not in result:
                        result.append(i[index:])
                        joinResult.append(joinBoiPattern[idx1])
                else:
                    if i[index:] not in result:
                        result.append(i[index:])
                        joinResult.append(joinBoiPattern[idx1])
                        # if i[:index] not in result:
                        #     result.append(i[:index])
                        #     joinResult.append(joinBoiPattern[idx1])
                        
            # else

            # for idx, j in enumerate(i):
            #     if j == tableTarget:
            #         break
            #     tablePattern[idx1].pop(0)
        # exit()
        return result, joinResult

    def raw(self, text):
        """Returns a raw string representation of text"""
        escape_dict={
            '\'':r'\'',
            '\"':r'\"',
        }
        new_string=''
        for char in text:
            try: new_string+=escape_dict[char]
            except KeyError: new_string+=char
        return new_string

    def killDb(self):
        try:
            self.dbInsert.close()
            self.dbInsert.close()
        except:
            pass
        self.closeDB()
    def insertToDb(self, result):
        # newlist = []
        # for i in result:
        #     if i not in newlist:
        #         newlist.append(i)
        # result = newlist
        listTabel = []
        tables = []
        self.dbInsert.query('SET foreign_key_checks = 0')
        for i, j in enumerate(result):
            for key in j.keys():
                # print 
                if key not in listTabel:
                    listTabel.append(key)
                # cur = dbSelect.cursor()
                cur = self.dbSelect.query(j[key]['selectQuery'])
                for row in cur:
                    data = []
                    for item in row:
                        if isinstance(item, int):
                            data.append(item)
                        else:
                            if item is None:
                                data.append(None)
                            else:
                                temp = str(item)
                                data.append(self.raw(temp))
                    tables.append(key)
                    query = MySQLQuery.into(key).insert(data)
                    print(str(query))
                    # try:
                        # insertCursor = dbInsert.cursor()s
                        # insertCursor.execute('SET foreign_key_checks = 0')
                    self.dbInsert.query(str(query))
                    self.dbInsert.commit()
                    # except (MySQLdb.Error, MySQLdb.Warning) as e:
                    #     print(e)
                # exit()
                # if key =='jadwal':
                #     exit()
        self.dbInsert.query('SET foreign_key_checks = 1')
        # pprint.pprint(listTabel)
        # exit()
        self.dbInsert.close()
        # self.dbInsert = None
        self.dbSelect.close()
        # self.dbSelect = None
        self.closeDB()
        f = open("statement.sql","w+")
        f.write('SET foreign_key_checks = 0;')
        for table in listTabel:
            f.write('CREATE TABLE tbl_new AS SELECT DISTINCT * FROM '+table+';LOCK TABLES '+table+' WRITE, tbl_new WRITE;truncate '+table+';insert '+table+' select * from tbl_new;drop table tbl_new;UNLOCK TABLES;')
        f.write('SET foreign_key_checks = 0;')
        f.close()
        cmd = 'mysql -u root mmt-its < statement.sql';
        args = shlex.split(cmd)
        p = os.system(cmd)
        self.dbInsert.query('SET foreign_key_checks = 1')
        self.dbInsert.close()



    def buildQuery(self, pattern, joinBoi, where, tabel):
        # oldPattern = copy.deepcopy(pattern)
        # print(len(oldPattern))

        # pprint(tabel)
        # exit()
        tableTarget = Table(tabel)
        counter = 0
        jumlah = len(pattern)
        result = []
        while (jumlah != counter):

            # print(pattern)
            # print(counter)
            insertPattern = list(pattern)
            insertJoin = list(joinBoi)
            for i, value in enumerate(insertPattern):

                q = None
                if value:
                    tbl = value[-1]
                for j, row in reversed(list(enumerate(value))):
                    if j == 0:
                        if len(value)>1 :
                            q = q.select(Table(value[-1]).star).distinct()
                            for element in where.keys():
                                if where[element] is None:
                                    q = q.where(getattr(tableTarget, element).isnull())
                                else:
                                    q = q.where(
                                        getattr(tableTarget, element) == where[element]
                                    )
                        else: 
                            q = MySQLQuery.from_(tableTarget).select(getattr(tableTarget, 'star')).distinct()
                            for element in where.keys():
                                # if element == 'jam_mulai' or element == 'jam_selesai' or element == 'tanggal':
                                #     continue
                                if where[element] is None:
                                    q = q.where(getattr(tableTarget, element).isnull())
                                else:
                                    q = q.where(
                                        getattr(tableTarget, element) == where[element]
                                    )
                                # q = q.where(
                                #         getattr(tableTarget, element) == where[element]
                                #     )
                        if value:
                            del pattern[i][-1]
                        if not pattern[i]:
                            counter = counter + 1
                        continue;
                    if j == len(value)-1:

                        tabel = Table(value[j])
                        tabel1= Table(value[j-1])
                        q = MySQLQuery.from_(tabel).join(
                                tabel1
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            ).select(tabel.star).distinct()
                        
                        # print(str(q))

                    else:
                        q = q.join(
                                Table(value[j-1])
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            )
                        # print('anajay')
                if q is not None:
                    result.append({
                        tbl: {
                            'selectQuery' : str(q)
                        }
                    })
                    del q
                # del q

        # insertToDb(result)
        # pprint(oldPattern)
        # pprint(result)
        seen = set()
        new_l = []
        queryList = {}
        for d in result:
            # print d.items()
            if d not in new_l:
                new_l.append(d)
                if d.keys()[0] not in queryList:
                    queryList[d.keys()[0]] = []
                    queryList[d.keys()[0]].append(d[d.keys()[0]]['selectQuery'])
                else:
                    queryList[d.keys()[0]].append(d[d.keys()[0]]['selectQuery'])
        # pprint(queryList)
        
        # exit()
        # print(new_l)
        return queryList
    def updateSlave(self, where, tabel, newData, result, ref, old):
        self.closeDB()
        new = dict(newData)
        test = self.dbInsert.query('SET FOREIGN_KEY_CHECKS=1')
        pikaTable = Table(tabel)
        q = MySQLQuery.update(pikaTable)
        qCheck = MySQLQuery.from_(pikaTable).select(fn.Count(pikaTable.star).as_('jumlah'))
        for i in newData.keys():
            q = q.set(i, newData[i])
        if tabel not in self.primaryKey:
            for key in where:
                if where[key] is None:
                    # if tabel in primaryKey:
                    #     if key == primaryKey[tabel]:
                            
                    qCheck = qCheck.where(getattr(pikaTable, key).isnull())
                    q = q.where(getattr(pikaTable, key).isnull())
                else:
                    # if tabel in primaryKey:
                    #     if key == primaryKey[tabel]:
                    #         qCheck = qCheck.where(
                    #             getattr(pikaTable, key) == where[key]
                    #         )
                    qCheck = qCheck.where(
                        getattr(pikaTable, key) == where[key]
                    )
                    q = q.where(
                        getattr(pikaTable, key) == where[key]
                    )
        else:
            qCheck = qCheck.where(
                getattr(pikaTable, self.primaryKey[tabel]) == where[self.primaryKey[tabel]]
            )
            q = q.where(
                getattr(pikaTable, self.primaryKey[tabel]) == where[self.primaryKey[tabel]]
            )


        # print(str(q))SET FOREIGN_KEY_CHECKS=1; 
        print(str(qCheck))
        test = self.dbInsert.query(str(qCheck))
        count = (test.fetchone()[0])
        print(count)
        if count == 0:
            self.insertToDb(self.buildQuery(result, ref, newData, tabel))
        else:
            isDirty = False
            cleanJob = []
            test = self.dbInsert.query(str(q))
            isDirty, cleanJob = self.checkDirty(tabel, old, result) 
            try:
                # print('a')
                if test[0] == 1452:
                    isDirty = True
                    for key in old:
                        cek = self.dbInsert.query(str("select referenced_table_name, referenced_column_name from information_schema.key_column_usage where table_schema = 'mmt-its' and (column_name = '"+key+"') and table_name = '"+tabel+"'"))
                        print("select referenced_table_name, referenced_column_name from information_schema.key_column_usage where table_schema = 'mmt-its' and (column_name = '"+key+"') and table_name = '"+tabel+"'")

                        for element in cek:
                            print(element[0])
                            print('cek')
                            # print(tabel)len()
                            # len(result[0][0])
                            if len(result) == 1 and len(result[0]) == 1 and result[0][0] == tabel: #ujung ex:absen
                                print('kaaa')
                                result = None
                                ref = None
                                # print(element[0])
                                result, ref = self.getTablePattern(element[0])
                                print(element[0])
                                print(result)
                                newData = {
                                   element[1] : new[key]
                                }        
                                tabel = element[0]
                                # exit()   
                            # else:   
                            tmpResult = []
                            tmpRef = []
                            print(result)
                            # isOld = True
                            for index, j in enumerate(result):
                                # print j
                                if element[0] in j:
                                    tmpResult.append(result[index])
                                    tmpRef.append(ref[index])


                            pprint(newData)
                            if not tmpResult:
                                cleanTmp = copy.deepcopy(result)
                                cleanJob.append(cleanTmp)
                                self.dbInsert.query('SET foreign_key_checks = 0')
                                self.dbInsert.query(str(q))
                                self.dbInsert.query('SET foreign_key_checks = 1')
                            else:
                                cleanTmp = copy.deepcopy(tmpResult)
                                cleanJob.append(cleanTmp)
                                pprint(tmpResult)
                                # exit()
                                self.insertToDb(self.buildQuery(tmpResult, tmpRef, newData, tabel))
                                print('a')
            except Exception as e:
                print(e)
                # test = self.dbInsert.query(str(q))
                self.dbInsert.commit()
                print(isDirty, cleanJob)
                if isDirty:
                    for value in cleanJob:
                        self.cleanData(value)
                self.killDb()
                return 1
            
            test = self.dbInsert.query(str(q))
            self.dbInsert.commit()
            if isDirty:
                for value in cleanJob:
                    self.cleanData(value)
            # self.dbInsert.commit()
            self.killDb()
        return 1
        # print(test)
        # fo
        #     print(i)
    def checkDirty(self, tabel, old, result):
        cleanJob = []
        isDirty = False
        for key in old:
            cek = self.dbInsert.query(str("select referenced_table_name, referenced_column_name from information_schema.key_column_usage where table_schema = 'mmt-its' and (column_name = '"+key+"') and table_name = '"+tabel+"'"))
            print("select referenced_table_name, referenced_column_name from information_schema.key_column_usage where table_schema = 'mmt-its' and (column_name = '"+key+"') and table_name = '"+tabel+"'")

            for element in cek:
                isDirty = True
                print(element[0])
                print('cek')
                # print(tabel)len()
                # len(result[0][0])
                if len(result) == 1 and len(result[0]) == 1 and result[0][0] == tabel: #ujung ex:absen
                    print('kaaa')
                    result = None
                    # print(element[0])
                    result, ref = self.getTablePattern(element[0])
                    print(result)

                tmpResult = []
                print(result)
                # isOld = True
                for index, j in enumerate(result):
                    # print j
                    if element[0] in j:
                        tmpResult.append(result[index])
                
                if not tmpResult:
                    cleanTmp = copy.deepcopy(result)
                    cleanJob.append(cleanTmp)
                else:
                    cleanTmp = copy.deepcopy(tmpResult)
                    cleanJob.append(cleanTmp)

        return isDirty, cleanJob

    def cleanData(self, result):
        print result
        tableToClean = []
        for i in result:
            for j in i:
                if j not in tableToClean:
                    dataPenting = []
                    for query in self.dictOfPattern[j]['query']:
                        dataPentingPerQuery = self.dbInsert.query(str(query), cursors.DictCursor)
                        for data in dataPentingPerQuery:
                            if data not in dataPenting:
                                dataPenting.append(data)
                    dirtyData = self.dbInsert.query('SELECT `'+j+'`.* FROM `' + j+'`', cursors.DictCursor)
                    for data in dirtyData:
                        if data not in dataPenting:
                            self.deleteData(data, j)
                    # exit()
                    tableToClean.append(j)
        # print tableToClean
    def deleteData(self, data, table):
        table = Table(table)
        query = MySQLQuery.from_(table).delete()
        for element in data.keys():
            if data[element] is None:
                query = query.where( getattr(table, element).isnull())
            else:
                query = query.where( getattr(table, element) == str(data[element]))

        print(str(query))
        self.dbInsert.query(str(query))
        self.dbInsert.commit()
        self.killDb()
    def deleteSlave(self, result, ref, log):
        data = log['data']
        table = Table(log['table'])
        query = MySQLQuery.from_(table).delete() 
        for element in data.keys():
            if data[element] is None:
                query = query.where( getattr(table, element).isnull())
            else:
                query = query.where( getattr(table, element) == str(data[element]))
        cur = self.dbInsert.query(str(query))
        if cur.rowcount > 0:
            self.dbInsert.commit()
            self.cleanData(result)
        self.killDb()
        # print cur.rowcount


    def buildMainQuery(self):   
        oldpattern = []
        oldPattern = copy.deepcopy(self.pattern)
        # print(oldPattern)
        # exit()
        counter = 0
        jumlah = len(self.pattern)
        result = []

        while (jumlah != counter):

            # print(pattern)
            # print(counter)
            insertPattern = list(self.pattern)
            insertJoin = list(self.joinBoi)
            for i, value in enumerate(insertPattern):

                q = None
                if value:
                    tbl = value[-1]
                for j, row in reversed(list(enumerate(value))):
                    if j == 0:
                        if len(value)>1 :
                            q = q.select(Table(value[-1]).star).where(
                                getattr(Table(value[0]), key_tabel_master) == kelas
                        ).distinct()
                        if value:
                            del self.pattern[i][-1]
                        if not self.pattern[i]:
                            counter = counter + 1
                        continue;
                    if j == len(value)-1:

                        tabel = Table(value[j])
                        tabel1= Table(value[j-1])
                        q = MySQLQuery.from_(tabel).join(
                                tabel1
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            ).select(tabel.star).distinct()
                        
                        # print(str(q))

                    else:
                        q = q.join(
                                Table(value[j-1])
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            )
                if q is not None:
                    result.append({
                        tbl: {
                            'selectQuery' : str(q)
                        }
                    })
        # insertToDb(result)
        r = json.dumps(result)
        print(r)
        return r

    def main(self):   
        # pprint(self.pattern)
        # exit()
        oldPattern = copy.deepcopy(self.pattern)
        oldJoin = list(self.joinBoi)
        # print(oldPattern)
        # exit()
        counter = 0
        jumlah = len(oldPattern)
        result = {}

        while (jumlah != counter):

            # print(oldPattern)
            # print(counter)
            insertPattern = list(oldPattern)
            insertJoin = list(oldJoin)
            for i, value in enumerate(insertPattern):
                # pprint(value)
                q = None
                if value:
                    tbl = value[-1]
                joinnn = {}
                for j, row in reversed(list(enumerate(value))):
                    if j == 0:
                        if len(value)>1 :
                            q = q.select(Table(value[-1]).star).where(
                                getattr(Table(value[0]), key_tabel_master) == kelas
                            ).distinct()
                            # q = q.select(Table(value[-1]).star).where(
                            #     getattr(Table(value[0]), key_tabel_master).isnull()
                            # )
                        if value:
                            del oldPattern[i][-1]
                        if not oldPattern[i]:
                            counter = counter + 1
                        continue;
                    if j == len(value)-1:

                        tabel = Table(value[j])
                        tabel1= Table(value[j-1])
                        q = MySQLQuery.from_(tabel).join(
                                tabel1
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            ).select(tabel.star).distinct()
                        # joinnn[row] = copy.deepcopy(insertJoin[i][row])
                        # print(str(q))

                    else:
                        q = q.join(
                                Table(value[j-1])
                            ).on(
                                getattr(Table(insertJoin[i][row]['table_name']), insertJoin[i][row]['column_name']) == getattr(Table(insertJoin[i][row]['referenced_table_name']), insertJoin[i][row]['referenced_column_name'])
                            )
                        # joinnn[row] = copy.deepcopy(insertJoin[i][row])
                    joinnn[row] = copy.deepcopy(insertJoin[i][row])

                if len(value) > 0 :
                    if tbl not in result.keys():
                        # print(tbl)
                        result[tbl] = {}
                        result[tbl]['pattern'] = []
                        result[tbl]['ref'] = []
                        result[tbl]['query'] = []
                    # pprint(value)
                    if value in result[tbl]['pattern']:
                        continue
                    result[tbl]['pattern'].append(list(value))
                    result[tbl]['query'].append(str(q))
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
        # for query in result['kelasmatkul']['query']:
        #     print query
        # exit()
        # pprint(result)
        # exit()
        # r = json.dumps(result)
        # print(r)
        self.dictOfPattern = copy.deepcopy(result)


        # sys.stdout.write(r)
        # closeDB()
        # print(len(result))

# if __name__ == "__main__":
#     main()

