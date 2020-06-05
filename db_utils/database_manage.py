import psycopg2 as psy
import config
from functools import wraps


def query_execution(do_commit=True, close_cursor=True):
    """ A decorator that saves changes in a db and at the same time frees resources of cursor """
    def decorator(func):
        @wraps(func)
        def func_itself(*args, **kwargs):
            DbTools.current_cursor = DbTools.current_connection.cursor()

            res = func(*args, **kwargs)

            if do_commit:
                DbTools.current_connection.commit()

            if close_cursor:
                DbTools.current_cursor.close()

            if res is not None:
                return res

        return func_itself
    return decorator



class DbTools:
    """Implements a function, returning fields from a table, and two fields to work with connection and cursor"""
    current_connection = psy.connect(dbname=config.DB_NAME, user=config.USER,
                                    password=config.PASSWORD, host=config.HOST)
    
    current_cursor = current_connection.cursor()

    @staticmethod
    @query_execution(do_commit=False)

    def get_fields_from_table(table, fields, condition):
        UserManager.current_cursor.execute(
            f"select {fields} from {table} where {condition}"
        )
        return UserManager.current_cursor.fetchone()



class UserManager(DbTools):

    @staticmethod
    @query_execution(do_commit=True)

    def add_user(user_id, list_count, active=True):
        UserManager.current_cursor.execute(
            f"insert into users values ({user_id}, {active}, {list_count})"
        )
    
    @staticmethod
    @query_execution(do_commit=True)

    def set_user_active(user_id, active):
        UserManager.current_cursor.execute(
            f"update users set active = {active} where user_id = {user_id}"
        )
    
    @staticmethod
    @query_execution(do_commit=True)

    def increase_users_lists_count(user_id):
        UserManager.current_cursor.execute(
            f"update users set lists_count = lists_count + 1 where id = {user_id}"
        )

class UserListManager(DbTools):
    
    @staticmethod
    @query_execution(do_commit=False)

    def is_there_same_list(list_name, user_id):
        UserManager.current_cursor.execute(
           f"select id from lists where name = '{list_name}' and user_id = {user_id}"
        )
        return UserManager.current_cursor.fetchone()


    @staticmethod
    @query_execution(do_commit=True)

    def add_words_to_list(list_id, words):
        UserManager.current_cursor.execute(
            f"update lists add words = '{words}' where id = {list_id}"
        )

    @staticmethod
    @query_execution(do_commit=False, close_cursor=False)

    def get_last_id():
        UserManager.current_cursor.execute(
            "select max(id) from lists"
        )

        fetched_result = UserManager.current_cursor.fetchone()

        return fetched_result[0] if fetched_result[0] is not None else 0

    @staticmethod
    @query_execution(do_commit=True)

    def add_list(user_id, list_name, words, interval=60):
        next_id_query = UserListManager.get_last_id() + 1

        UserManager.current_cursor.execute(
            "insert into lists values (%s, %s, '%s', %s, current_timestamp, '%s')" % 
            (next_id_query, user_id, list_name, interval, words)
        )