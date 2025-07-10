import sqlite3
from typing import Optional, Dict, Any

DB_NAME = 'helpers.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS helpers (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                job TEXT,
                experience TEXT,
                help TEXT,
                contacts TEXT
            )
        ''')
        conn.commit()

def add_helper(user_id: int, name: str, job: str, experience: str, help_text: str, contacts: str):
    with get_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO helpers (user_id, name, job, experience, help, contacts)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, job, experience, help_text, contacts))
        conn.commit()

def get_helper(user_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM helpers WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        if row:
            return {
                'user_id': row[0],
                'name': row[1],
                'job': row[2],
                'experience': row[3],
                'help': row[4],
                'contacts': row[5],
            }
        return None

def update_helper_field(user_id: int, field: str, value: str):
    if field not in {'name', 'job', 'experience', 'help', 'contacts'}:
        raise ValueError('Invalid field')
    with get_connection() as conn:
        conn.execute(f'UPDATE helpers SET {field} = ? WHERE user_id = ?', (value, user_id))
        conn.commit()

def helper_exists(user_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute('SELECT 1 FROM helpers WHERE user_id = ?', (user_id,))
        return cur.fetchone() is not None

def get_all_helpers() -> list:
    """Получить всех помощников"""
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM helpers ORDER BY name')
        rows = cur.fetchall()
        return [
            {
                'user_id': row[0],
                'name': row[1],
                'job': row[2],
                'experience': row[3],
                'help': row[4],
                'contacts': row[5],
            }
            for row in rows
        ]

def search_helpers_by_job(job_keyword: str) -> list:
    """Поиск помощников по профессии"""
    with get_connection() as conn:
        cur = conn.execute(
            'SELECT * FROM helpers WHERE job LIKE ? ORDER BY name',
            (f'%{job_keyword}%',)
        )
        rows = cur.fetchall()
        return [
            {
                'user_id': row[0],
                'name': row[1],
                'job': row[2],
                'experience': row[3],
                'help': row[4],
                'contacts': row[5],
            }
            for row in rows
        ]

def search_helpers_by_help(help_keyword: str) -> list:
    """Поиск помощников по типу помощи"""
    with get_connection() as conn:
        cur = conn.execute(
            'SELECT * FROM helpers WHERE help LIKE ? ORDER BY name',
            (f'%{help_keyword}%',)
        )
        rows = cur.fetchall()
        return [
            {
                'user_id': row[0],
                'name': row[1],
                'job': row[2],
                'experience': row[3],
                'help': row[4],
                'contacts': row[5],
            }
            for row in rows
        ]

def delete_helper(user_id: int):
    """Удалить помощника из базы"""
    with get_connection() as conn:
        conn.execute('DELETE FROM helpers WHERE user_id = ?', (user_id,))
        conn.commit()

def get_helpers_count() -> int:
    """Получить количество помощников в базе"""
    with get_connection() as conn:
        cur = conn.execute('SELECT COUNT(*) FROM helpers')
        return cur.fetchone()[0]

if __name__ == '__main__':
    init_db() 