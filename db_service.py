import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def db_connection():
    return mysql.connector.connect(host=DB_HOST,user=DB_USERNAME,passwd=DB_PASSWORD)

def db_engine():
    return create_engine(f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

def create_database():
    db = db_connection()
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS redbus")
    cursor.close()
    db.close()

def create_table():
    db = db_connection()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS redbus.bus_route 
                   (id int primary key auto_increment,
                   state_transport_name text,
                   route_name text,
                   route_link text,
                   bus_name text,
                   bus_type text,
                   departing_time time,
                   duration text,
                   arrival_time time,
                   star_rating float,
                   fare_price decimal(10,2),
                   seats_available int,
                   seat_type text,
                   created_on datetime default current_timestamp)''')
    cursor.close()
    db.close()

def insert_data(df_data):
    data = tuple(df_data.to_numpy().tolist())
    try:
        db = db_connection()
        cursor = db.cursor()
        cursor.executemany('''INSERT INTO redbus.bus_route
                       (state_transport_name, route_name, route_link, bus_name, bus_type, departing_time, duration, arrival_time, star_rating, fare_price, seats_available, seat_type) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', data)
        db.commit()        
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        db.close()   

def check_data(state_transport_name):
    try:
        db = db_connection()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}'")
        records_to_delete = cursor.fetchall()
        if records_to_delete:
            cursor.execute(f"DELETE FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}'")
            db.commit()
            return records_to_delete
        else:
            return []  
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()

# To get state transports from MySQL
def get_state_transports():
    list_state_transport=['All']
    try:
        db = db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT state_transport_name FROM redbus.bus_route GROUP BY state_transport_name")
        state_transports = cursor.fetchall()
        for state_transport in state_transports:
            list_state_transport.append(state_transport[0])
        return list_state_transport
    except Exception as e:
        print(e)
        return list_state_transport
    finally:
        cursor.close()
        db.close()

# To get bus routes from MySQL
def get_bus_routes(state_transport_name):
    list_bus_routes=['All']
    try:
        db = db_connection()
        cursor = db.cursor()
        if state_transport_name == 'All':
            cursor.execute("SELECT DISTINCT route_name FROM redbus.bus_route")
        else:
            cursor.execute(f"SELECT DISTINCT route_name FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}'")
        bus_routes = cursor.fetchall()
        for bus_route in bus_routes:
            list_bus_routes.append(bus_route[0])
        return list_bus_routes
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()

# To get bus type from MySQL
def get_bus_type(state_transport_name, route_name):
    list_bus_type=['All']
    try:
        db = db_connection()
        cursor = db.cursor()
        if state_transport_name == 'All':
            if route_name == 'All':
                cursor.execute("SELECT DISTINCT bus_type FROM redbus.bus_route")
            else:
                cursor.execute(f"SELECT DISTINCT bus_type FROM redbus.bus_route WHERE route_name = '{route_name}'")                
        else:
            if route_name == 'All':
                cursor.execute(f"SELECT DISTINCT bus_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}'")
            else:
                cursor.execute(f"SELECT DISTINCT bus_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}' AND route_name = '{route_name}'")
        bus_types = cursor.fetchall()
        for bus_type in bus_types:
            list_bus_type.append(bus_type[0])
        return list_bus_type
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()

# To get bus details from MySQL
def get_bus_data(state_transport_name, route_name, bus_type, start_price, end_price, start_rating, end_rating, start_seat, end_seat):
    try:
        db = db_connection()
        cursor = db.cursor()
        if state_transport_name == 'All':
            if route_name == 'All':
                if bus_type == 'All':
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
                else:
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE bus_type = '{bus_type}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
            else:
                if bus_type == 'All':
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE route_name = '{route_name}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
                else:
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE route_name = '{route_name}' AND bus_type = '{bus_type}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
        else:
            if route_name == 'All':
                if bus_type == 'All':
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
                else:
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}' AND bus_type = '{bus_type}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
            else:
                if bus_type == 'All':
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}' AND route_name = '{route_name}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
                else:
                    cursor.execute(f"SELECT state_transport_name, route_name, bus_type, fare_price, star_rating, seats_available, seat_type FROM redbus.bus_route WHERE state_transport_name = '{state_transport_name}' AND route_name = '{route_name}' AND bus_type = '{bus_type}' AND fare_price BETWEEN {start_price} AND {end_price} AND star_rating BETWEEN {start_rating} AND {end_rating} AND seats_available BETWEEN {start_seat} AND {end_seat}")
        
        bus_data = cursor.fetchall()
        i = [i for i in range(1, len(bus_data) + 1)]
        #pd.set_option('display.max_columns', None)
        #pd.set_option('display.max_rows', None)
        data = pd.DataFrame(bus_data, columns=['State Transport Name', 'Route Name', 'Bus Type', 'Fare Price', 'Star Rating', 'Seats Available', 'Seat Type'], index=i)
        data = data.rename_axis('S.No')
        data.index = data.index.map(lambda x: '{:^{}}'.format(x, 10))
        return data
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()

# To get bus details for Data Visualization from MySQL
def dv_get_data_from_mysql(state_transport_name):
    try:
        db = db_engine()
        bus_data = pd.read_sql('SELECT * FROM redbus.bus_route WHERE state_transport_name = "'+state_transport_name+'"', db)     
        return bus_data
    except Exception as e:
        print(e)
        return None
    
# To get state transports for Data Visualization from MySQL
def dv_get_state_transports():
    list_state_transport=[]
    try:
        db = db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT state_transport_name FROM redbus.bus_route GROUP BY state_transport_name")
        state_transports = cursor.fetchall()
        for state_transport in state_transports:
            list_state_transport.append(state_transport[0])
        return list_state_transport
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()

# To get buses based on state transport for Data Visualization from MySQL
def dv_get_state_buses():    
    try:
        db = db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT state_transport_name, COUNT(*) AS number_of_buses FROM redbus.bus_route GROUP BY state_transport_name;")
        state_buses = cursor.fetchall()
        data = pd.DataFrame(state_buses)
        data = data.rename(columns={0: 'State Transport', 1: 'Number of Buses'})        
        return data
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()
