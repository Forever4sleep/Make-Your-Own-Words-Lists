import psycopg2 as psy
import config
from functools import wraps


def query_execution(do_commit=True):
    """ A decorator that saves changes in a db and at the same time frees resources of cursor """
    def decorator(func):
        def func_itself(*args, **kwargs):
            DbManage.current_cursor = DbManage.current_connection.cursor()

            res = func(*args, **kwargs)

            if do_commit:
                DbManage.current_connection.commit()

            DbManage.current_cursor.close()

            if res is not None:
                return res

        return func_itself
    return decorator



class DbManage:
    current_connection = psy.connect(dbname=config.DB_NAME, user=config.USER,
                                    password=config.PASSWORD, host=config.HOST)
    
    current_cursor = current_connection.cursor()



class UsersLists(DbManage):

    @staticmethod
    @query_execution(do_commit=False)

    def get_fields_from_lists(fields, condition):
        UsersLists.current_cursor.execute(
            f"select {fields} from lists where {condition}"
        )


    @staticmethod
    @query_execution(do_commit=True)

    def add_list(user_id, list_name, last_update, interval=60): 
        next_id_query = '(select max(id) + 1 from lists)'

        UsersLists.current_cursor.execute(
            "insert into lists values (%s, '{}', %s, '%s %s %s')" %
            (next_id_query, user_id, list_name, interval, last_update)
        )


    @staticmethod
    @query_execution(do_commit=True)

    def add_words_to_list(list_id, words):
        UsersLists.current_cursor.execute(
            f"update lists add words = '{words}' where id = {list_id}"
        )
        UsersLists.current_cursor.fetchone()
    

    @staticmethod
    @query_execution(do_commit=False)

    def is_there_same_list(list_name, user_id):
        UsersLists.current_cursor.execute(
           f"select id from lists where name = '{list_name}' and user_id = {user_id}"
        )
        return UsersLists.current_cursor.fetchone()
