import pymysql
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="PARQUEADERO",
        cursorclass=pymysql.cursors.DictCursor
    )
