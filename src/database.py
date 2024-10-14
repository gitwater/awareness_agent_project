# src/database.py
import json
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file='agent.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                birthdate TEXT,
                gender TEXT,
                culture TEXT,
                language TEXT,
                dimensions TEXT,
                UNIQUE(username)
            )
        ''')

        # Create agent_state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                last_updated TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TIMESTAMP,
                message TEXT,
                sender TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

        # Create Dimension Analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dimension_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                analysis TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    # Save user information to the database
    # Insert if it is new, otherwise update
    def save_user_info(self, user_info):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, birthdate, gender, culture, language, dimensions)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                birthdate = excluded.birthdate,
                gender = excluded.gender,
                culture = excluded.culture,
                language = excluded.language,
                dimensions = excluded.dimensions
        ''', (
            user_info.get('username'),
            user_info.get('birthdate'),
            user_info.get('gender'),
            user_info.get('culture'),
            user_info.get('language'),
            user_info.get('dimensions')
        ))
        self.conn.commit()
        # Check if a new row was inserted and add the 'id' to the user_info dictionary
        if cursor.lastrowid:
            user_info['id'] = cursor.lastrowid

        return user_info

    def get_user_info(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, birthdate, gender, culture, language, dimensions FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': username,
                'birthdate': row[1],
                'gender': row[2],
                'culture': row[3],
                'language': row[4],
                'dimensions': row[5 ]
            }
        else:
            return {'id': None, 'username': None, 'birthdate': None, 'gender': None, 'culture': None, 'language': None, 'dimensions': None}

    def save_user_info_field(self, user_id, field_name, field_value):
        cursor = self.conn.cursor()
        cursor.execute(f'''
            UPDATE users
            SET {field_name} = ?
            WHERE id = ?
        ''', (field_value, user_id))
        self.conn.commit()

    def save_profile(self, user_id, profile_data):
        cursor = self.conn.cursor()
        # Delete existing profile data for the user
        cursor.execute('DELETE FROM profiles WHERE user_id = ?', (user_id,))
        # Insert new profile data
        for dimension, score in profile_data.items():
            cursor.execute('''
                INSERT INTO profiles (user_id, dimension, score)
                VALUES (?, ?, ?)
            ''', (user_id, dimension, score))
        self.conn.commit()

    def get_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT dimension, score FROM profiles WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        profile = {}
        for dimension, score in rows:
            profile[dimension] = score
        return profile

    def save_agent_state(self, user_id, state):
        cursor = self.conn.cursor()
        timestamp = datetime.now()
        cursor.execute('''
            INSERT OR REPLACE INTO agent_state (user_id, state, last_updated)
            VALUES (?, ?, ?)
        ''', (user_id, state, timestamp))
        self.conn.commit()

    def get_agent_state(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT state FROM agent_state WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_dimension_analysis(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT analysis FROM dimension_analysis WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def save_dimension_analysis(self, user_id, analysis):
        # convert analysis to a json string if it is a dict
        if isinstance(analysis, dict):
            analysis = json.dumps(analysis)
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO dimension_analysis (user_id, analysis)
            VALUES (?, ?)
        ''', (user_id, analysis))
        self.conn.commit()

    def save_conversation(self, user_id, message, sender='user'):
        cursor = self.conn.cursor()
        timestamp = datetime.now()
        cursor.execute('''
            INSERT INTO conversations (user_id, timestamp, message, sender)
            VALUES (?, ?, ?, ?)
        ''', (user_id, timestamp, message, sender))
        self.conn.commit()

    def get_conversation_history(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, message, sender FROM conversations
            WHERE user_id = ? ORDER BY timestamp
        ''', (user_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
