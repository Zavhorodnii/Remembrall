from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup)
from telegram import ReplyKeyboardRemove
from calendar import monthrange
from datetime import datetime
import telegramcalendar
import re


CHOOSING, CREATE_DATE, SELECT_DATA, TODAY, SELECT, ENTER, CALENDAR, CREATE_TIME, READY = range(9)
CREATE_REM = 11

class MessageButtons:
    def __init__(self):
        self.__set_rem = list()
        self.__step_create = 0
        self.__change_time = False
        self.__reply_keyboard = [
            ['Создать напоминание', 'Просмотр списка напоминаний'],
        ]
        self.__markup = ReplyKeyboardMarkup(self.__reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    def clear_data(self):
        self.__set_rem.clear()
        self.__step_create = 0

    def change_date(self, change):
        self.__change_time = change

    def check_text_rem(self, text):
        text_2 = re.sub(r'\s+', ' ', text)
        text_2.strip()
        text_2.capitalize()
        self.__set_rem.append(text_2)

    @property
    def get_rem(self):
        return self.__set_rem

    def check_date(self, text):
        try:
            text_2 = re.sub(r'\s+', '', text)
            text_2.strip()
            check = text_2.split('.')
            len_2 = len(check)
            if len_2 < 3 or len_2 > 3:
                raise Exception('Неверный формат ввода даты')
            for date in check:
                if date == '':
                    raise Exception('Неверный формат ввода даты')

            day = int(check[0])
            month = int(check[1])
            year = int(check[2])

            if day < 1 or month < 1 or year < 1:
                raise Exception('Неверный формат ввода даты')

            if month > 12:
                raise Exception('Неверный формат ввода месяца')

            now = datetime.now()
            if day < now.day and month <= now.month and year <= now.year:
                raise Exception('День уже прошел')


            year = int('20{}'.format(year))
            day_end = monthrange(year, month)
            if day > day_end[1]:
                raise Exception('Неверный формат ввода дня')
            day_str = str(day)
            if day < 10:
                day_str = '0{}'.format(day)
            month_str = str(month)
            if month < 10:
                month_str = '0{}'.format(month)

            date = "{}.{}.{}".format(day_str, month_str, check[2])
            self.__set_rem.append(date)
            return 0, "Введена дата {}".format(date)
        except Exception as ex:
            return 1, str(ex)

    def check_time(self, time_2):
        try:
            time = str(time_2)
            text_2 = re.sub(r'\s+', '', time)
            text_2.strip()
            check = text_2.split(':')
            if len(check) < 2 or len(check) > 2:
                raise Exception("Неверный формат ввода времени")
            if not check[0].isdigit() and not check[0].isdigit():
                raise Exception('Неверный формат ввода времени')
            else:
                hour = int(check[0])
            if not check[1].isdigit():
                raise Exception('Неверный формат ввода времени')
            else:
                minute = int(check[1])
            if hour < 0 or hour > 23:
                raise Exception('Неверный формат ввода часов')
            if minute < 0 or minute > 59:
                raise Exception('Неверный формат ввода минут')
            if self.__change_time:
                date = self.__set_rem[0].split('.')
            else:
                date = self.__set_rem[5].split('.')
            now = datetime.now()
            if int(date[0]) == now.day and int(date[1]) == now.month and int('20{}'.format(date[2])) == now.year:
                if hour <= now.hour and minute <= now.minute:
                    raise Exception('Время прошло')

            if len(str(hour)) < 2:
                hour = "0{}".format(hour)
            if len(str(minute)) < 2:
                minute = "0{}".format(minute)
            time = "{}:{}".format(hour, minute)
            self.__set_rem.append(time)
            return 0,
        except Exception as ex:
            return 1, str(ex)


    def start(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text="Чтобы создато напоминание следуйте инструкциям и используйте"
                 " функциональные кнопки под строкой ввода",
            reply_markup=self.__markup
        )
        return CHOOSING

    def create_remem(self, update, context):
        if update.message.text.lower() == "создать напоминание" and self.__step_create == 0:
            context.bot.send_message(
                update.effective_chat.id,
                text="Введите заголовок напоминания",
                reply_markup=ReplyKeyboardRemove()
            )
            self.__step_create += 1
            return CREATE_REM
        elif self.__step_create == 1:


            self.__set_rem.append(update.message.from_user.id)
            self.__set_rem.append(update.message.from_user.first_name)
            self.__set_rem.append(update.message.from_user.last_name)

            self.check_text_rem(update.message.text)
            context.bot.send_message(
                update.effective_chat.id,
                text="Введите текст напоминания"
            )
            self.__step_create += 1
            return CREATE_DATE

    def enter_date(self, update, context, reply_markup):
        if self.__step_create == 3 or self.__change_time:
            text = self.check_date(update.message.text)
            context.bot.send_message(
                update.effective_chat.id,
                text=text[1]
            )
            if text[0] == 0:
                self.__step_create +=1
                self.set_time(update, context)
                return CREATE_TIME
        if self.__step_create == 2:
            self.check_text_rem(update.message.text)
            self.__step_create += 1

        update.message.reply_text(
            "Когда должно быть выведено напоминание?\nВыбрать можно на сегодня или позже.",
            reply_markup=reply_markup
        )
        return CHOOSING

    def today_date(self, update, context):
        query = update.callback_query
        today = datetime.today()
        date = today.strftime("%d.%m.%y")
        self.__set_rem.append(date)
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Выбрана дата:  {}".format(date)
        )
        self.__step_create += 1
        self.set_time(update, context)
        return CREATE_TIME

    def create_calendar(self, update, context):
        query = update.callback_query
        reply_markup = telegramcalendar.create_calendar()
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"Выберите дату",
            reply_markup=reply_markup
        )
        return CALENDAR

    def change_calendar(self, update, context):
        try:
            query = update.callback_query
            selected, date = telegramcalendar.process_calendar_selection(context.bot, update)

            if selected:
                today = date.today()
                if date.year < today.year:
                    selected = False
                if date.year == today.year:
                    if date.month < today.month:
                        selected = False
                if date.year == today.year:
                    if date.month == today.month:
                        if date.day < today.day:
                            selected = False
                if not selected:
                    self.create_calendar(update, context)


            if selected:
                self.__set_rem.append("%s" % (date.strftime("%d.%m.%y")))
                context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="Выбрана дата %s" % (date.strftime("%d.%m.%Y"))
                )
                self.__step_create +=1
                self.set_time(update, context)
                return CREATE_TIME
        except Exception as exe:
            return CALENDAR


    def create_date(self, update, context):
        query = update.callback_query

        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Введите дату в формате \'ДД.ММ.ГГ\'"
        )
        return CREATE_DATE

    def set_time(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text="Ведите время в формате \'ЧЧ:ММ\'"
        )

    def enter_time(self, update, context):
        print('self.__change_time ', self.__change_time)
        if self.__change_time:
            self.__step_create = 4

        if self.__step_create == 4:
            text = self.check_time(update.message.text)
            if text[0] == 0:
                self.successful_create_rem(update, context)
                return 0, CHOOSING
            else:
                context.bot.send_message(
                    update.effective_chat.id,
                    text=text[1]
                )
                self.set_time(update, context)
                return 1, CREATE_TIME


    def successful_create_rem(self, update, context):
        if self.__change_time:
            update.message.reply_text(
                "Напоминание перенесено на {}, {}".format(self.__set_rem[0], self.__set_rem[1]),
                reply_markup=self.__markup
            )
        else:
            update.message.reply_text(
                "Напоминание {}\nПоявится {} в {}".format(self.__set_rem[3], self.__set_rem[5], self.__set_rem[6]),
                reply_markup=self.__markup
            )



