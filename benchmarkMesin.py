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
import os
import requests
import sys
import re

r = requests.get('http://192.168.0.50:9999/get/ruangan')
# print(r.text)
result = json.loads(r.text)
kelas = {}
job = [10]
for id_kelas in result['ruangan']:
    for socketId in result['ruangan'][id_kelas]:
        ip = result['ip'][socketId]
        address = "http://"+ip+":8888/get/benchmark/"
        test = requests.get(address)
        # print(r)
        filename = 'benchmarkResult'+id_kelas+'.txt'
        open(filename, 'wb').write(test.content)
        ea = open(filename, 'r')
        for line in ea:
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            line = line.split('|')
            if line[0] != '':
                if id_kelas not in kelas:
                    kelas[id_kelas] = {
                        'waktu' : 0,
                        'jumlahLog' : 0,
                        'rowChanged':0
                    }
                kelas[id_kelas]['waktu'] += float(line[1])
                kelas[id_kelas]['jumlahLog'] += 1
                
            # line = line.

        address = "http://"+ip+":8888/get/benchmark/clean"
        test = requests.get(address)
        os.remove(filename)
        # print(r)
        filename = 'benchmarkCleanResult'+id_kelas+'.txt'
        open(filename, 'wb').write(test.content)
        ea = open(filename, 'r')
        for line in ea:
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            line = line.split('|')
            kelas[id_kelas]['waktu'] += float(line[0])
            kelas[id_kelas]['rowChanged'] += float(line[1])
        os.remove(filename)
        # os.system("wget --content-disposition "+address)
# print(kelas['207'])
wb = Workbook()
ws = wb.active
ws.append(['ruangan', 'log/s', 'jumlah log', 'total waktu', 'row changed', 'rata'])
for id_kelas in kelas:
    data = [
        id_kelas,
        kelas[id_kelas]['jumlahLog']/kelas[id_kelas]['waktu'],
        kelas[id_kelas]['jumlahLog'],
        kelas[id_kelas]['waktu'],
        kelas[id_kelas]['rowChanged'],
        kelas[id_kelas]['waktu']/kelas[id_kelas]['jumlahLog']
    ]
    ws.append(data)

wb.save('benchmark/mesinKesimpulan'+sys.argv[1]+'.xlsx')