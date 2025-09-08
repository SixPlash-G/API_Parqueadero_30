import pymysql
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="PARKING",
        cursorclass=pymysql.cursors.DictCursor
    )
