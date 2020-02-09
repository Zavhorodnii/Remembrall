from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup)
from DataBase import *
import datetime

DELETE = 9
MOVE = 10
SELECT_DATA = 2


class ShowRemember:
    def __init__(self):
        self.__user_id = 0
        self.__num_sess = 0
        self.__step_mess = 0
        self.__change_back = list()
        self.__database = DataBase()
        self.__remember_with_db = list()
        self.__keyboard = [
            [InlineKeyboardButton("Удалить", callback_data=str(DELETE)),
             InlineKeyboardButton("Перенести", callback_data=str(MOVE))]
        ]
        self.__reply_markup = InlineKeyboardMarkup(self.__keyboard)

    def update_remember(self):
        self.__remember_with_db = self.__database.show_all_remem(self.__user_id)


    def show_remember(self, update, context, markup):
        self.__change_back.clear()
        self.__user_id = update.message.chat_id
        self.__num_sess = update.message.message_id
        self.update_remember()
        # print('len(self.__remember_with_db ', len(self.__remember_with_db))
        if len(self.__remember_with_db) == 0:
            context.bot.send_message(
                update.effective_chat.id,
                text='У вас нет напомианий',
                reply_markup = markup
            )
        for i in self.__remember_with_db:
            print('Cообщение ', self.__num_sess)
            print('self.__num_sess ', self.__num_sess)
            self.__database.set_call_mes(self.__num_sess, i[0])
            self.__num_sess += 1
            data = str(i[3]).split(' ')
            new_data = data[0].split('-')
            context.bot.send_message(
                update.effective_chat.id,
                text='{}\n{}\nДата {}.{}.{}, время {}'.format(str(i[1]), str(i[2]), new_data[2], new_data[1],
                                                              new_data[0], data[1]),
                reply_markup=self.__reply_markup
            )

        return

    def send_mess(self, update, context, index):
        self.__user_id = update.message.chat_id
        #self.__num_sess = update.message.message_id
        text = self.__database.thread_rem(index)
        print('text[2] ', text[2])

        if text[2] <= datetime.datetime.today():
            data = str(text[2]).split(' ')
            new_data = data[0].split('-')
            __step_mess = context.bot.send_message(
                update.effective_chat.id,
                text='{}\n{}\nДата {}.{}.{}, время {}'.format(text[0], text[1], new_data[2], new_data[1],
                                                              new_data[0], data[1]),
                reply_markup=self.__reply_markup
            )
            self.__database.set_call_mes(__step_mess.message_id-1, index)


    def delete_remember(self, update, context):
        print('delete')
        self.__user_id = update.callback_query.message.chat_id
        from_db = self.__database.get_call_mes(self.__user_id, update.callback_query.message.message_id - 1)
        delete_date_time = self.__database.get_date_time(update.callback_query.message.message_id - 1)
        self.__database.dell_mess(from_db[0][1])

        for i in from_db:
            context.bot.edit_message_text(
                chat_id=update.callback_query.message.chat_id,
                message_id=i[0] + 1,
                text="Напоминание удалено"
            )
        return delete_date_time

    def move_date(self, update, context, reply_markup, is_clear=False):
        if is_clear:
            self.__change_back.clear()
        print('+++++++++++++++++++++++++++++')
        self.__user_id = update.callback_query.message.chat_id
        self.update_remember()
        from_db = self.__database.get_call_mes(self.__user_id, update.callback_query.message.message_id - 1)
        #print('from_db ', from_db)
        print('self.__remember_with_db ', self.__remember_with_db)
        #print('self.__change_back ', self.__change_back)
        this_mess = list()
        for i in self.__remember_with_db:
            if i[0] == from_db[0][1]:
                this_mess = i
        print('this_mess[3] ', this_mess[3])
        data = str(this_mess[3]).split(' ')
        new_data = data[0].split('-')
        if len(self.__change_back) != 0:
            self.change(update, context)
        self.__change_back.append(this_mess[1])
        self.__change_back.append(this_mess[2])

        self.__step_mess = context.bot.send_message(
            update.effective_chat.id,
            text='{}\n{}\nДата {}.{}.{}, время {}'.format(this_mess[1], this_mess[2], new_data[2], new_data[1],
                                                               new_data[0], data[1]),
            reply_markup=reply_markup
        )
        self.__step_mess = self.__step_mess.message_id
        if self.__step_mess - self.__num_sess > 1:
            self.__num_sess = self.__step_mess - 1
            self.__database.set_call_mes(self.__step_mess - 1, from_db[0][1])
        else:
            self.__database.set_call_mes(self.__num_sess, from_db[0][1])
        self.__num_sess += 1


    def change(self, update, context):
        # print('self.__num_sess ', self.__num_sess)
        # print(self.__change_back[0])

        from_db = self.__database.get_call_mes(self.__user_id, self.__num_sess - 1)
        # print('from_db_2 ', from_db)

        if len(from_db) != 0:
            this_mess = list()
            for i in self.__remember_with_db:
                if i[0] == from_db[0][1]:
                    this_mess = i
            #print('this_mess[3] ', this_mess[3])
            data = str(this_mess[3]).split(' ')
            new_data = data[0].split('-')
            context.bot.edit_message_text(
                chat_id=self.__user_id,
                message_id=self.__num_sess,
                text='{}\n{}\nДата {}.{}.{}, время {}'.format(self.__change_back[0], self.__change_back[1],
                                                                      new_data[2], new_data[1],
                                                                      new_data[0], data[1]),
                reply_markup=self.__reply_markup
            )
        self.__change_back.clear()

    def update_date(self, update, context, new_date):
        date = new_date[0].split('.')
        date_time = '20{}-{}-{} {}:00'.format(date[2], date[1], date[0], new_date[1])
        odl_date_time = self.__database.get_date_time(self.__num_sess - 1)

        self.__database.update_date(date_time, self.__num_sess - 1)
        from_db = self.__database.get_call_mes(self.__user_id, self.__num_sess - 1)
        mess = self.__database.get_one_mes(self.__num_sess - 1)

        data = str(mess[0][2]).split(' ')
        new_data = data[0].split('-')
        for i in from_db:
            context.bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=i[0] + 1,
                text='{}\n{}\nДата {}.{}.{}, время {}'.format(mess[0][0], mess[0][1], new_data[2], new_data[1],
                                                              new_data[0], data[1]),
                reply_markup=self.__reply_markup
            )

        self.__change_back.clear()
        return odl_date_time, mess[0][2]
