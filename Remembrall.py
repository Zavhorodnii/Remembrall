from BlockSettings import *
import importlib

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TELEGRAM_HTTP_API_TOKEN = '942544876:AAE4GMGwrVxMPF6qftwXhn6dEfBiLvicAdY'

CHOOSING, CREATE_DATE, SELECT_DATA, TODAY, SELECT, ENTER, CALENDAR, CREATE_TIME, \
READY, DELETE, MOVE, CREATE_REM = range(12)


class Remembrall:
    def __init__(self):
        self.__user_id = 0
        self.__num_sess = 0
        self.__remember = None
        self.__blockSettings = None
        self.__database = None

    def start(self, update, context):
        print("context ", context.bot.send_message)
        try:
            return self.__blockSettings.start(update, context)
        except Exception as ex:
            print(ex)

    def create_remem(self, update, context):
        return self.__blockSettings.create_remem(update, context)


    def show_remem(self, update, context):
        return self.__blockSettings.show_remem(update, context)


    def delete_rem(self, update, context):
        return self.__blockSettings.delete_rem(update, context)


    def move_date(self, update, context):
        print('+++++++++++++++++++++++++++++++++++')
        return self.__blockSettings.move_date(update, context)


    def enter_date(self, update, context):
        return self.__blockSettings.enter_date(update, context)


    def today_date(self, update, context):
        #try:
        return self.__blockSettings.today_date(update, context)
        #except Exception as ex:
        #    print(ex)

    def create_calendar(self, update, context):
        #try:
        return self.__blockSettings.create_calendar(update, context)
        #except Exception as ex:
        #    print(ex)

    def change_calendar(self, update, context):
        return self.__blockSettings.change_calendar(update, context)


    def create_date(self, update, context):
        return self.__blockSettings.create_date(update, context)


    def set_time(self, update, context):
        return self.__blockSettings.set_time(update, context)


    def enter_time(self, update, context):
        tt = self.__blockSettings.enter_time(update, context)
        print('tt ', tt)
        return tt


    def successful_create_rem(self, update, context):
        return self.__blockSettings.successful_create_rem(update, context)


    def update_date(self, update, context, data):
        return self.__blockSettings.update_date(update, context, data)


    def from_thread(self, index):
        # try:
        return self.__blockSettings.from_thread(index)

    # except Exception as ex:
    #    print(ex)

    def main(self, remember):
        self.__remember = remember
        self.__blockSettings = BlockSettings(remember)
        self.__database = DataBase()

        updater = Updater(TELEGRAM_HTTP_API_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        if len(ThreadCheck.call_time) == 0:
            all_remember = self.__database.select_all_from_remember()
            ThreadCheck.start_create_thread(updater, all_remember)

        control_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start),
                          MessageHandler(Filters.regex('^Просмотр списка напоминаний$'), self.show_remem),
                          MessageHandler(Filters.regex('^Создать напоминание$'), self.create_remem),

                          CallbackQueryHandler(self.delete_rem, pass_user_data=True, pattern='{}$'.format(DELETE)),
                          CallbackQueryHandler(self.move_date, pass_user_data=True, pattern='{}$'.format(MOVE)),
                          ],
            states={
                CHOOSING: [MessageHandler(Filters.regex('^Просмотр списка напоминаний$'), self.show_remem),
                           MessageHandler(Filters.regex('^Создать напоминание$'), self.create_remem),
                           CallbackQueryHandler(self.delete_rem, pass_user_data=True, pattern='{}$'.format(DELETE)),
                           CallbackQueryHandler(self.move_date, pass_user_data=True, pattern='{}$'.format(MOVE)),
                           CallbackQueryHandler(self.today_date, pass_user_data=True, pattern='{}$'.format(TODAY)),
                           CallbackQueryHandler(self.create_calendar, pass_user_data=True,
                                                pattern='{}$'.format(SELECT)),
                           CallbackQueryHandler(self.create_date, pass_user_data=True, pattern='{}$'.format(ENTER)),
                           CallbackQueryHandler(self.successful_create_rem, pass_user_data=True,
                                                pattern='{}$'.format(READY)),
                           ],
                CREATE_REM: [MessageHandler(Filters.text, self.create_remem)],
                CREATE_DATE: [MessageHandler(Filters.text, self.enter_date),
                              ],
                CALENDAR: [CallbackQueryHandler(self.change_calendar),
                           ],
                CREATE_TIME: [MessageHandler(Filters.text, self.enter_time), ]

            },

            fallbacks=[CommandHandler('start', self.start),
                       ]
        )

        dispatcher.add_handler(control_handler)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    remembrall = Remembrall()
    remembrall.main(remembrall)
