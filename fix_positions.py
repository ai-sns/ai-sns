"""
修复数据库中的position值
确保LLM的position在0-999范围内，Tool的position在1000-1999范围内
"""
import sqlite3

def fix_positions():
    conn = sqlite3.connect('db/db.sqlite')
    cursor = conn.cursor()
    
    print('=== 修复前的数据 ===')
    cursor.execute('SELECT id, name, type, position FROM web_mng WHERE is_delete = 0 ORDER BY type, position')
    rows = cursor.fetchall()
    for r in rows:
        print(f'ID: {r[0]:3d} | Name: {r[1]:20s} | Type: {r[2]:4s} | Position: {r[3]}')
    
    # 修复LLM的position
    print('\n=== 修复LLM的position ===')
    cursor.execute('SELECT id, name, position FROM web_mng WHERE type = "LLM" AND is_delete = 0 ORDER BY position')
    llm_items = cursor.fetchall()
    
    for index, (item_id, name, old_position) in enumerate(llm_items):
        new_position = index
        if old_position != new_position:
            print(f'更新 {name}: {old_position} -> {new_position}')
            cursor.execute('UPDATE web_mng SET position = ? WHERE id = ?', (new_position, item_id))
    
    # 修复Tool的position
    print('\n=== 修复Tool的position ===')
    cursor.execute('SELECT id, name, position FROM web_mng WHERE type = "Tool" AND is_delete = 0 ORDER BY position')
    tool_items = cursor.fetchall()
    
    for index, (item_id, name, old_position) in enumerate(tool_items):
        new_position = 1000 + index
        if old_position != new_position:
            print(f'更新 {name}: {old_position} -> {new_position}')
            cursor.execute('UPDATE web_mng SET position = ? WHERE id = ?', (new_position, item_id))
    
    conn.commit()
    
    print('\n=== 修复后的数据 ===')
    cursor.execute('SELECT id, name, type, position FROM web_mng WHERE is_delete = 0 ORDER BY type, position')
    rows = cursor.fetchall()
    for r in rows:
        print(f'ID: {r[0]:3d} | Name: {r[1]:20s} | Type: {r[2]:4s} | Position: {r[3]}')
    
    conn.close()
    print('\n✅ Position修复完成！')

if __name__ == '__main__':
    fix_positions()
