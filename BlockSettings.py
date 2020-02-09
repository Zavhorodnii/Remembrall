from telegram.ext import *
import logging
from MessageButtons import *
from ShowRemember import *
import ThreadCheck

CHOOSING, CREATE_DATE, SELECT_DATA, TODAY, SELECT, ENTER, CALENDAR, CREATE_TIME, \
READY, DELETE, MOVE, CREATE_REM = range(12)


class BlockSettings:
    def __init__(self, remember):
        self.__remember = remember
        self.__LIFO_rem = list()
        self.__block_rem = False
        self.__update = None
        self.__context = None
        self.__database = DataBase()
        self.__change_time = True
        self.__is_move = False
        self.__is_create = False
        self.__update_thread = True
        self.__mess_but = MessageButtons()
        self.__show_remember = ShowRemember()
        self.__keyboard = [
            [InlineKeyboardButton("Сегодня", callback_data=str(TODAY)),
             InlineKeyboardButton("Выбрать", callback_data=str(SELECT)),
             InlineKeyboardButton("Ввести", callback_data=str(ENTER))]
        ]
        self.__reply_markup = InlineKeyboardMarkup(self.__keyboard)
        self.__reply_keyboard = [
            ['Создать напоминание', 'Просмотр списка напоминаний'],
        ]
        self.__markup = ReplyKeyboardMarkup(self.__reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    def start(self, update, context):
        print('1111self.__remember ', self.__remember)
        self.__context = context
        self.__update = update
        user = self.__database.check_user(update.message.chat_id)
        self.__mess_but.start(update, context)
        if int(user) != 0:
            all_remem = self.__database.get_rememm_thread(update.message.chat_id)

            for i in all_remem:
                ThreadCheck.set_call_time(i[0], i[1], self.__remember)
        return CHOOSING

    def create_remem(self, update, context):

        self.__context = context
        self.__update = update
        #self.__block_rem = True
        print('create ', self.__is_move)
        self.__is_create = True
        if self.__is_move:
            self.__show_remember.change(update, context)
        self.__is_move = False
        self.__mess_but.change_date(False)
        self.__change_time = False
        if self.__update_thread:
            ThreadCheck.update_thread(self.__remember, update.message.chat_id)
            self.__update_thread = False
        return self.__mess_but.create_remem(update, context)

    def show_remem(self, update, context):

        print('show')

        self.__context = context
        self.__update = update
        self.__is_create = False
        self.__change_time = True
        self.__show_remember.show_remember(update, context, self.__markup)
        if self.__update_thread:
            ThreadCheck.update_thread(self.__remember, update.message.chat_id)
            self.__update_thread = False
        self.__mess_but.change_date(True)
        return CHOOSING

    def delete_rem(self, update, context):
        if self.__change_time:
            delete_date = self.__show_remember.delete_remember(update, context)
            ThreadCheck.delete_call_time(delete_date)
            return

    def move_date(self, update, context):
        #self.__block_rem = True
        if not self.__is_create:
            self.__is_move = True
            self.__mess_but.change_date(True)
            self.__show_remember.move_date(update, context, self.__reply_markup)
            return CHOOSING

    def enter_date(self, update, context, ):
        return self.__mess_but.enter_date(update, context, self.__reply_markup)

    def today_date(self, update, context):
        return self.__mess_but.today_date(update, context)

    def create_calendar(self, update, context):
        return self.__mess_but.create_calendar(update, context)

    def change_calendar(self, update, context):
        return self.__mess_but.change_calendar(update, context)

    def create_date(self, update, context):
        return self.__mess_but.create_date(update, context)

    def set_time(self, update, context):
        return self.__mess_but.set_time(update, context)

    def enter_time(self, update, context):

        ret = self.__mess_but.enter_time(update, context)
        print("ret ", ret)
        if ret[0] == 0:
            self.successful_create_rem(update, context)
            return CHOOSING
        else:
            return ret[1]

    def successful_create_rem(self, update, context):
        data = self.__mess_but.get_rem
        if self.__change_time:
            self.update_date(update, context, data)

        else:
            if self.__database.check_user(data[0]) == 0:
                self.__database.add_user(data[0], data[1], data[2])
            date_str = data[5].split('.')
            date_time = '20{}-{}-{} {}:00'.format(date_str[2], date_str[1], date_str[0], data[6])
            self.__database.send_rem_to_db(data[3], data[4], date_time, data[0])

            from_db = self.__database.get_start_data(update.message.chat_id)
            #print('2222self.__remember ', self.__remember)
            ThreadCheck.set_call_time(from_db[0][0], from_db[0][1], self.__remember)

        self.__mess_but.clear_data()
        self.__is_create = False
        if len(self.__LIFO_rem) > 0:
            self.from_thread(self.__LIFO_rem[0])

    def update_date(self, update, context, data):
        new = self.__show_remember.update_date(update, context, data)
        #print('new ', new)
        ThreadCheck.update_call_time(new)

    def from_thread(self, id):
        self.__block_rem = True
        print('from_thread ', id)
        print('self.__LIFO_rem ', self.__LIFO_rem)
        if self.__LIFO_rem.count(id) == 0:
            self.__LIFO_rem.append(id)
        if not self.__block_rem:
            for i in range(len(self.__LIFO_rem)):
                self.__is_create = False
                self.__change_time = True
                self.__show_remember.send_mess(self.__update, self.__context, self.__LIFO_rem.pop(0))
                self.__mess_but.change_date(True)

                print('delete_self.__LIFO_rem ', self.__LIFO_rem)
            return CHOOSING
