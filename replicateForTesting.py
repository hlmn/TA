import MySQLdb
import MySQLdb.cursors as cursors
import time
import os
import requests
import json
db = MySQLdb.connect(host="127.0.0.1",
                     user="root",         # your username
                     passwd="semarmesem")

waktu = int(time.time())
os.system("redis-cli flushall")
os.system("mysql -u root -psemarmesem -e 'DROP DATABASE IF EXISTS `mmt-its`;'")
os.system("mysql -u root -psemarmesem -e 'CREATE DATABASE `mmt-its`;'")
os.system('mysql -u root -psemarmesem -e "SET GLOBAL FOREIGN_KEY_CHECKS=0;"')
# db.close()
os.system('mysql -u root -psemarmesem mmt-its < baru.sql')
os.system('mysql -u root -psemarmesem -e "SET GLOBAL FOREIGN_KEY_CHECKS=1;"')
cursor = db.cursor()
cursor.execute('flush tables with read lock')
db.commit()
os.system("wget -O backup"+str(waktu)+".sql http://127.0.0.1:8000/backup/get")
os.system("redis-cli flushall")
cursor = db.cursor()
cursor.execute('unlock tables')
db.commit()

os.system('mysql -u root -psemarmesem -e "DROP DATABASE IF EXISTS `mmtslave`;"')
os.system('mysql -u root -psemarmesem -e "CREATE DATABASE `mmtslave`;"')
os.system('mysql -u root -psemarmesem -e "SET GLOBAL FOREIGN_KEY_CHECKS=0;"')
# db.close()
os.system('mysql -u root -psemarmesem `mmtslave` < backup'+str(waktu)+'.sql')
os.system('mysql -u root -psemarmesem -e "SET GLOBAL FOREIGN_KEY_CHECKS=1;"')
os.system("redis-cli flushall")

r = requests.get('http://localhost:9999/get/ruangan')
result = json.loads(r.text)

for ruangan in result['ruangan']:
    for socketId in result['ruangan'][ruangan]:
        ip = result['ip'][socketId]
        address = "http://"+ip+":8888/start/replikasi/"
        print('replicating '+ruangan+'...')
        test = requests.get(address)
        print(test.text)