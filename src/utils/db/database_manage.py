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
    current_connection = psy.connect(dbname=config.DB_NAME, user=config.USER,
                                    password=config.PASSWORD, host=config.HOST)
    
    current_cursor = current_connection.cursor()

    @staticmethod
    @query_execution(do_commit=False)

    def get_fields_from_table(table, fields, condition):
        if condition != "none":
            DbTools.current_cursor.execute(
                f"select {fields} from {table} where {condition}"
            )
        else: 
            DbTools.current_cursor.execute(
                f"select {fields} from {table}"
            )
        return DbTools.current_cursor.fetchall()



class UserManager(DbTools):

    CACHED_USERS_RESULTS = list(list(user_elements) for user_elements in DbTools.get_fields_from_table("users", "*", "none"))

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

    def interact_with_lists_count(user_id, action):
        if action == "increase":
            UserManager.current_cursor.execute(
                f"update users set lists_count = lists_count + 1 where id = {user_id}"
            )
        elif action == "decrease":
            UserManager.current_cursor.execute(
                f"update users set lists_count = lists_count - 1 where id = {user_id}"
            )

class UserListManager(DbTools):
    
    CACHED_LISTS_RESULTS = list(list(list_elements) for list_elements in DbTools.get_fields_from_table("lists", "*", "none"))

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
    @query_execution(do_commit=True)

    def add_list(user_id, list_name, words, interval, chat_id):

        #Getting of last id
        UserManager.current_cursor.execute(
            "select max(id) from lists"
        )

        fetched_result = UserManager.current_cursor.fetchone()

        next_id = fetched_result[0] + 1 if fetched_result[0]  is not None else 0

        UserManager.current_cursor.execute(
            "insert into lists values (%s, %s, '%s', %s, current_timestamp, '%s', %s)" % 
            (next_id, user_id, list_name, interval, words, chat_id)
        )

    @staticmethod
    @query_execution(do_commit=True)

    def remove_list(user_id, list_name):
        UserManager.current_cursor.execute(
          f"delete from lists where user_id = {user_id} and name = '{list_name}'"
        )   

    @staticmethod
    @query_execution(do_commit=True)

    def update_last_update_datetime(list_id):
        UserManager.current_cursor.execute(
          f"update lists set updated_date = current_timestamp where id = {list_id}"
        )
