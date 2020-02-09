from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup)
from telegram import ReplyKeyboardRemove
from calendar import monthrange
from datetime import datetime
from telegram.ext import *
from DataBase import *
import telegramcalendar
import logging
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TELEGRAM_HTTP_API_TOKEN = '942544876:AAE4GMGwrVxMPF6qftwXhn6dEfBiLvicAdY'

CHOOSING, CREATE_DATE, SELECT_DATA, TODAY, SELECT, ENTER, CALENDAR, CREATE_TIME, READY = range(9)


class Remembrall:
    def __init__(self):
        self.__set_rem = list()
        self.__step_create = 0
        self.__database = DataBase()
        self.__reply_keyboard = [
            ['Создать напоминание', 'Просмотр списка напоминаний'],
        ]
        self.__markup = ReplyKeyboardMarkup(self.__reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    def clear_data(self):
        self.__set_rem.clear()
        self.__step_create = 0

    def check_text_rem(self, text):
        text_2 = re.sub(r'\s+', ' ', text)
        text_2.strip()
        text_2.capitalize()
        self.__set_rem.append(text_2)

    def check_date(self, text):
        try:
            print(text)
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

            print('{} _ {} _ {}'.format(day, month, year))

            if day < 1 or month < 1 or year < 1:
                raise Exception('Неверный формат ввода даты')


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

    def check_time(self, time):
        print(time)
        try:
            text_2 = re.sub(r'\s+', '', time)
            text_2.strip()
            check = text_2.split(':')
            if not check[0].isdigit():
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

            date = self.__set_rem[2].split('.')
            now = datetime.now()
            if int(date[0]) == now.day and int(date[1]) == now.month and int(date[2]) == now.year:
                if hour <= now.hour and minute <= now.minute:
                    raise Exception('Время вышло')

            if len(str(hour)) < 2:
                hour = "0{}".format(hour)
            if len(str(minute)) < 2:
                minute = "0{}".format(minute)
            time = "{}:{}".format(hour, minute)
            self.__set_rem.append(time)
            return 0, "Напоминание появится {} в {}".format(self.__set_rem[2], time)
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
            reply_markup = ReplyKeyboardRemove()
            context.bot.send_message(
                update.effective_chat.id,
                text="Введите заголовок напоминания",
                reply_markup=reply_markup
            )
            self.__step_create += 1
            return CHOOSING
        elif self.__step_create == 1:
            self.check_text_rem(update.message.text)
            context.bot.send_message(
                update.effective_chat.id,
                text="Введите текст напоминания"
            )
            self.__step_create += 1
            return CREATE_DATE


    def show_remem(self, update, context):
        context.bot.send_message(
            update.effective_chat.id,
            text="Показать напоминания"
        )

    def center_date(self, update, context):
        if self.__step_create == 3:
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

        keyboard = [
            [InlineKeyboardButton("Сегодня", callback_data=str(TODAY)),
             InlineKeyboardButton("Выбрать", callback_data=str(SELECT)),
             InlineKeyboardButton("Ввести", callback_data=str(ENTER))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Когда должно быть выведено напоминание?\nВыбрать можно на сегодня или позже.",
            reply_markup=reply_markup
        )
        return SELECT_DATA

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
            print("111")
            self.__set_rem.append("%s" % (date.strftime("%d.%m.%Y")))
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="Выбрана дата %s" % (date.strftime("%d.%m.%Y"))
            )
            self.__step_create +=1
            self.set_time(update, context)
            return CREATE_TIME


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
        print(self.__step_create)
        if self.__step_create == 4:
            text = self.check_time(update.message.text)
            context.bot.send_message(
                update.effective_chat.id,
                text=text[1]
            )
            if text[0] == 0:
                print(text[1])
                return self.successful_create_rem(update, context)
            else:
                self.set_time(update, context)
                return CREATE_TIME


    def successful_create_rem(self, update, context):
        update.message.reply_text(
            "Напоминание {}\nПоявится {} в {}".format(self.__set_rem[0], self.__set_rem[2], self.__set_rem[3]),
            reply_markup=self.__markup
        )
        print(self.__set_rem)

        self.clear_data()
        return CHOOSING




    def main(self):
        updater = Updater(TELEGRAM_HTTP_API_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],

            states={
                CHOOSING: [MessageHandler(Filters.regex('^Просмотр списка напоминаний$'), self.show_remem),
                           MessageHandler(Filters.text, self.create_remem),
                           ],
                CREATE_DATE: [MessageHandler(Filters.text, self.center_date),
                              ],
                SELECT_DATA: [CallbackQueryHandler(self.today_date, pass_user_data=True, pattern='{}$'.format(TODAY)),
                              CallbackQueryHandler(self.create_calendar, pass_user_data=True, pattern='{}$'.format(SELECT)),
                              CallbackQueryHandler(self.create_date, pass_user_data=True, pattern='{}$'.format(ENTER)),
                              CallbackQueryHandler(self.successful_create_rem, pass_user_data=True, pattern='{}$'.format(READY)),
                              ],
                CALENDAR: [CallbackQueryHandler(self.change_calendar),
                           ],
                CREATE_TIME: [MessageHandler(Filters.text,self.enter_time),]
            },

            fallbacks=[CommandHandler('start', self.start)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    remembrall = Remembrall()
    remembrall.main()
