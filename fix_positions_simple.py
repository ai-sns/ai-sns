import sqlite3

conn = sqlite3.connect('db/db.sqlite')
cursor = conn.cursor()

print('=== Fixing LLM positions ===')
cursor.execute('SELECT id, name, position FROM web_mng WHERE type = "LLM" AND is_delete = 0 ORDER BY position, id')
llm_items = cursor.fetchall()

for index, (item_id, name, old_pos) in enumerate(llm_items):
    new_pos = index
    print(f'LLM: {name[:20]:20s} | {old_pos:4d} -> {new_pos:4d}')
    cursor.execute('UPDATE web_mng SET position = ? WHERE id = ?', (new_pos, item_id))

print('\n=== Fixing Tool positions ===')
cursor.execute('SELECT id, name, position FROM web_mng WHERE type = "Tool" AND is_delete = 0 ORDER BY position, id')
tool_items = cursor.fetchall()

for index, (item_id, name, old_pos) in enumerate(tool_items):
    new_pos = 1000 + index
    print(f'Tool: {name[:20]:20s} | {old_pos:4d} -> {new_pos:4d}')
    cursor.execute('UPDATE web_mng SET position = ? WHERE id = ?', (new_pos, item_id))

conn.commit()
conn.close()
print('\n✅ Done!')
