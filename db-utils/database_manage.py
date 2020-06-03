import psycopg2 as psy
import config


class DbManage:
    current_connection = psy.connect(dbname=config.DB_NAME, user=config.USER,
                                    password=config.PASSWORD, host=config.HOST)
    
    current_cursor = current_connection.cursor()

    @staticmethod
    def cursor_wrapper(self):
        def wrapper(self, func):
            def func_itself(*args, **kwargs):
                self.current_cursor = self.current_connection.cursor()

                func(*args, **kwargs)

                self.current_cursor.close()
            return func_itself
        return wrapper


class UsersLists(DbManage):
    @staticmethod
    @DbManage.cursor_wrapper

    def get_user_lists(self, id):
        self.current_cursor.execute(
            r"select name from lists where user_id = {id}"
        )

    @staticmethod
    @DbManage.cursor_wrapper

    def get_words_from_list(self, list_id):
        self.currect_cursor.execute(
            r"select words from lists where id = {list_id}"
        )
        return self.current_cursor.fetchone()

    @staticmethod
    @DbManage.cursor_wrapper

    def add_list(self, user_id, list_name):
        next_id_query = '(select max(id) + 1)'

        self.currect_cursor.execute(
            r"insert into lists (id, user_id, name, words) values ({next_id_query}, {user_id}, {list_name}, '{}')"
        )

    @staticmethod
    @DbManage.cursor_wrapper

    def add_words_to_list(self, list_id, words):
        self.current_cursor.execute(
            r"update lists add words = '{words}' where id = {list_id}"
        )
    
    @staticmethod
    @DbManage.cursor_wrapper

    def get_all_users_lists(self, user_id):
        self.current_cursor.execute(
            r"select count(id) from lists where user_id = {user_id}"
        )
        return self.current_cursor.fetchone()

    @staticmethod
    @DbManage.cursor_wrapper

    def get_listID_by_name(self, list_name):
        self.current_cursor.execute(
            r"select id from lists where name = lower({list_name})"
        )
        return self.current_cursor.fetchone()

    @staticmethod
    @DbManage.cursor_wrapper

    def delete_list(self, list_id):
        self.current_cursor.execute(
            r"delete from lists where list_id = id"
        )