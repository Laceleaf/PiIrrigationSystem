import sqlite3
from sqlite3 import Error

def create_connection(plant_db_1):
    """create a database connection to a SQLIte database """
    conn=None

    try:
        conn=sqlite3.connect("plant_db_1")
        print(sqlite3.version)
        print("Database created")

        conn.execute('''
        CREATE TABLE IF NOT EXISTS sensordata
        ([plant_id] INTEGER PRIMARY KEY, 
        [soil_capactive] INTEGER,
        [temperature] REAL,
        [humidity] REAL,
        [light] INTEGER,
        [taken_at] TEXT)
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS plant
        ([plant_id] INTEGER PRIMARY KEY,
        [name] TEXT,
        [plant_type] TEXT,
        [created_at] TEXT,
        FOREIGN KEY (plant_id)
            REFERENCES sensordata (plant_id))
        ''')
        
        conn.execute('''
        INSERT INTO sensordata(plant_id, soil_capactive, taken_at) VALUES ('1',300, CURRENT_TIMESTAMP) 
        ''')
        
        #Dont forget to commit or data is not inserted
        conn.commit()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    create_connection(r"/home/molly/Desktop")

