import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'electrohub.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            input_data TEXT,
            result TEXT,
            warnings TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor TEXT,
            value REAL,
            unit TEXT,
            alert INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energy_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            total_energy REAL,
            peak_load REAL,
            efficiency REAL,
            cost REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment TEXT,
            result TEXT,
            conclusion TEXT,
            pdf_path TEXT,
            timestamp DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def save_calculation(module, input_data, result, warnings=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO calculations (module, input_data, result, warnings)
        VALUES (?, ?, ?, ?)
    ''', (module, str(input_data), str(result), warnings))
    conn.commit()
    conn.close()

def get_calculations(module=None, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    if module:
        cursor.execute('''
            SELECT * FROM calculations WHERE module = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (module, limit))
    else:
        cursor.execute('''
            SELECT * FROM calculations ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def save_iot_reading(sensor, value, unit, alert=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO iot_readings (sensor, value, unit, alert)
        VALUES (?, ?, ?, ?)
    ''', (sensor, value, unit, alert))
    conn.commit()
    conn.close()

def get_iot_readings(sensor=None, limit=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    if sensor:
        cursor.execute('''
            SELECT * FROM iot_readings WHERE sensor = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (sensor, limit))
    else:
        cursor.execute('''
            SELECT * FROM iot_readings ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def save_energy_data(filename, total_energy, peak_load, efficiency, cost):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO energy_data (filename, total_energy, peak_load, efficiency, cost)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, total_energy, peak_load, efficiency, cost))
    conn.commit()
    conn.close()

def get_energy_data(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM energy_data ORDER BY id DESC LIMIT ?', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def save_lab_report(experiment, result, conclusion, pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lab_reports (experiment, result, conclusion, pdf_path, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (experiment, result, conclusion, pdf_path, datetime.now()))
    conn.commit()
    conn.close()

def get_lab_reports(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lab_reports ORDER BY timestamp DESC LIMIT ?', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
