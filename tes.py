from pypika import MySQLQuery, Table, Field
import MySQLdb
import MySQLdb.cursors as cursors
db = MySQLdb.connect(host="db.muhammadhilman.com",    # your host, usually localhost
                     user="hlmn",         # your username
                     passwd="liverpoolfc",  # your password
                     db="information_schema") 
key_column_usage = Table('key_column_usage')
# print key_column_usage.table_name
# exit()
tabel_master = 'kelas'

def findPattern(tabel, dari):
    if dari is None:
        dari = []
    else:
        print(dari)
    q = MySQLQuery.from_('key_column_usage').select(key_column_usage.constraint_name, Field('table_name'), key_column_usage.referenced_table_name).where(
            key_column_usage.table_schema == 'mmt-its'
        ).where(
            key_column_usage.referenced_table_name.notnull()
        ).where(
            (key_column_usage.referenced_table_name == tabel) | (Field('table_name') == tabel)
        )
    cur = db.cursor()
    cur.execute(str(q))
    cur = list(cur)
    count = 0
    
    for row in cur:
        if row[2] == tabel and row[2] != tabel_master:
            count = count + 1

    # print count
    fromRow = [];
    if len(cur) != count:
        for i, row in enumerate(cur):
            # print row
            fromRow.append(dari)
            if row[2] == tabel:
                if row[2] in fromRow[i]:
                    print('continue')
                    continue
                else:
                    if row[2] == tabel_master:
                        fromRow[i].append(row[1])
                        print('pindah ke '+row[1]+' dari '+tabel_master)
                    # elif row[1]:
                    else:
                        fromRow[i].append(row[2])
                        print('pindah ke '+fromRow[i][-1]+' dari '+row[1])
                    # fromRow[i].append(row[2])

                    print(row[1]+' start')
                    findPattern(row[1], fromRow[i])
                    print(row[1]+' done')
        # print(fromRow)
            else:
                if row[1] in fromRow[i]: 
                    continue
                else:
                    # fromRow[i].append(row[2])
                    print(row[2]+" > "+ row[1])
                    print(row[2]+' start')
                    findPattern(row[2], fromRow[i])
                    print(row[2]+' done')

    else:
        print('pucuk '+ tabel)
        print(dari)

    # if row.
    # db.close()

# dari = []
# if dari is None:
#     print('goblok')

findPattern('kelas', None)
