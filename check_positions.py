import sqlite3

conn = sqlite3.connect('db/db.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT id, name, type, position FROM web_mng WHERE is_delete = 0 ORDER BY type, position')
rows = cursor.fetchall()

print('ID | Name | Type | Position')
print('-' * 60)
for r in rows:
    print(f'{r[0]:3d} | {r[1]:20s} | {r[2]:4s} | {r[3]}')

conn.close()
