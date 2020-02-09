import pymysql


class DataBase:
    def __init__(self):
        self.__con = pymysql.connect('localhost',
                                     'root',
                                     'Ambrasador83',
                                     'usersdb')
        self.__add_user_to_db = "INSERT users (IdUser, FirstName, LastName)" \
                                "VALUES (%s, %s, %s)"
        self.__add_rem_to_db = "INSERT remember (HeadRemember, TextRemember, DateRemember,IdUser)" \
                               "VALUES (%s, %s, %s, %s)"
        self.__user_in_db = "SELECT COUNT(*) as count FROM users WHERE IdUser=%s"
        self.__all_remem = "select IdRemember, HeadRemember, TextRemember, DateRemember from " \
                           "remember, users where remember.IdUser=users.IdUser " \
                           "and users.IdUser = %s"
        self.__call_remem = "INSERT message (IdMessage, IdRemember)" \
                            "VALUES (%s, %s)"
        self.__vall_dell_mess = "select IdMessage, IdRemember from message where message.IdRemember = " \
                                "(select IdRemember from remember, users " \
                                "WHERE remember.IdUser=users.IdUser and " \
                                "users.IdUser = %s and " \
                                "remember.IdRemember = (select IdRemember from message " \
                                "where message.IdMessage = %s));"
        self.__delete_rem_1 = "DELETE FROM message WHERE IdRemember = %s;"
        self.__delete_rem_2 = "DELETE FROM remember WHERE IdRemember = %s;"
        self.__update_date = "UPDATE remember " \
                             "SET DateRemember = %s " \
                             "WHERE remember.IdRemember = (select IdRemember from message " \
                             "where message.IdMessage = %s);"
        self.__get_one_mess = "select HeadRemember, TextRemember, DateRemember from remember " \
                              "where remember.IdRemember = (select IdRemember " \
                              "from message where message.IdMessage = %s);"
        self.__get_date = "select IdRemember from remember where remember.IdRemember = " \
                          "(select IdRemember from message where message.IdMessage = %s);"
        self.__get_start = "select IdRemember, DateRemember FROM remember " \
                           "WHERE IdRemember=(SELECT MAX(IdRemember) FROM remember where IdUser = %s);"
        self.__thread_rem = "select HeadRemember, TextRemember, DateRemember FROM remember WHERE IdRemember = %s;"
        self.__thread_remem = "select IdRemember, DateRemember FROM remember WHERE IdUser = %s"
        self.__select_all_from_remember = "SELECT * FROM usersdb.remember;"

    def add_user(self, *data):
        args = (data[0], data[1], data[2])
        with self.__con:
            __cur = self.__con.cursor()
            __cur.execute(self.__add_user_to_db, args)
            __cur.close()

    def send_rem_to_db(self, *set_rem):
        args = (set_rem[0], set_rem[1], set_rem[2], set_rem[3])
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__add_rem_to_db, args)
            __con.close()

    def check_user(self, id_user):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__user_in_db, id_user)
            in_db = __con.fetchone()
            __con.close()
        return in_db[0]

    def show_all_remem(self, id_user):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__all_remem, id_user)
            in_db = __con.fetchall()
            __con.close()
        return in_db

    def set_call_mes(self, *add_mess):
        args = (add_mess[0], add_mess[1])
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__call_remem, args)
            __con.close()

    def get_call_mes(self, *id_mess):
        args = (id_mess[0], id_mess[1])
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__vall_dell_mess, args)
            in_db = __con.fetchall()
            __con.close()
        return in_db

    def dell_mess(self, id_mess):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__delete_rem_1, id_mess)
            __con.execute(self.__delete_rem_2, id_mess)
            __con.close()

    def update_date(self, *new_date):
        args = (str(new_date[0]), str(new_date[1]))
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__update_date, args)
            __con.close()

    def get_one_mes(self, id_mess):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__get_one_mess, str(id_mess))
            in_db = __con.fetchall()
            __con.close()
        return in_db

    def get_date_time(self, id_mess):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__get_date, str(id_mess))
            in_db = __con.fetchone()
            __con.close()
        return in_db

    def get_start_data(self, id_user):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__get_start, id_user)
            in_db = __con.fetchall()
            __con.close()
        return in_db

    def thread_rem(self, id_mess):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__thread_rem, id_mess)
            in_db = __con.fetchone()
            __con.close()
        return in_db

    def get_rememm_thread(self, id_user):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__thread_remem, id_user)
            in_db = __con.fetchall()
            __con.close()
        return in_db

    def select_all_from_remember(self):
        with self.__con:
            __con = self.__con.cursor()
            __con.execute(self.__select_all_from_remember)
            in_db = __con.fetchall()
            __con.close()
        return in_db
