import psycopg2 as psy
import config
from functools import wraps


def query_execution(func):
    """ A decorator that saves changes in a db and at the same time frees resources of cursor """
    @wraps(func)
    def func_itself(*args, **kwargs):
        DbManage.current_cursor = DbManage.current_connection.cursor()

        res = func(*args, **kwargs)

        DbManage.current_connection.commit()

        DbManage.current_cursor.close()

        if res is not None:
            return res

    return func_itself



class DbManage:
    current_connection = psy.connect(dbname=config.DB_NAME, user=config.USER,
                                    password=config.PASSWORD, host=config.HOST)
    
    current_cursor = current_connection.cursor()



class UsersLists(DbManage):

    @staticmethod
    @query_execution
    def get_user_lists(self, id):
        self.current_cursor.execute(
            r"select name from lists where user_id = {id}"
        )

    @staticmethod
    @query_execution

    def get_words_from_list(self, list_id):
        self.currect_cursor.execute(
            r"select words from lists where id = {list_id}"
        )
        return self.current_cursor.fetchone()

    @staticmethod
    @query_execution

    def add_list(user_id, list_name, last_update, interval=60):
        next_id_query = '(select max(id) + 1 from lists)'

        UsersLists.current_cursor.execute(
            "insert into lists values (%s, '{}', %s, '%s %s %s')" %
            (next_id_query, user_id, list_name, interval, last_update)
        )

    @staticmethod
    @query_execution

    def add_words_to_list(self, list_id, words):
        self.current_cursor.execute(
            r"update lists add words = '{words}' where id = {list_id}"
        )
        UsersLists.current_cursor.fetchone()
    
    @staticmethod
    @query_execution

    def get_all_users_lists(self, user_id):
        self.current_cursor.execute(
            r"select count(id) from lists where user_id = {user_id}"
        )
        return self.current_cursor.fetchone()

    @staticmethod
    @query_execution

    def get_listID_by_name(self, list_name):
        self.current_cursor.execute(
            r"select id from lists where name = lower({list_name})"
        )
        return self.current_cursor.fetchone()
