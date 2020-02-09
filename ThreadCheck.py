import threading
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
import datetime
import time
from queue import Queue
from DataBase import *

DELETE = 9
MOVE = 10
call_time = dict()
thread_list = list()
queue = Queue()

__keyboard = [
    [InlineKeyboardButton("Удалить", callback_data=str(DELETE)),
     InlineKeyboardButton("Перенести", callback_data=str(MOVE))]
]
reply_markup = InlineKeyboardMarkup(__keyboard)


class ThreadCheck(threading.Thread):
    def __init__(self, queue, send_mess, is_start):
        threading.Thread.__init__(self)
        self.__queue = queue
        self.__send_mess = send_mess
        self.__is_start = is_start
        self.__database = DataBase()


    def update(self, send_mess, is_start):
        print('update ', send_mess, is_start)
        self.__send_mess = send_mess
        self.__is_start = is_start


    def run(self):
        index = self.__queue.get()
        print('index ', call_time[index])

        data = str(call_time[index][3]).split(' ')
        new_data = data[0].split('-')


        i = 0
        while True:
            #print("i ", i)
            #print('call_time ', call_time)

            #print('update2 ', self.__send_mess, self.__is_start)
            if call_time[index][3] == 0:
                del call_time[index]
                print('delete message')
                self.__queue.task_done()
                break
            elif call_time[index][3] <= datetime.datetime.today():

                if self.__is_start:
                    #print('print in thread')
                    __step_mess = self.__send_mess.bot.send_message(
                        call_time[index][4], '{}\n{}\nДата {}.{}.{}, '
                                             'время {}'.format(call_time[index][1], call_time[index][2], new_data[2],
                                                               new_data[1], new_data[0], data[1]),
                        reply_markup=reply_markup
                    )
                    self.__database.set_call_mes(__step_mess.message_id - 1, index)
                else:
                    print('from_thread')
                    self.__send_mess.from_thread(index)
                time.sleep(300)
            else:
                i += 1
                #print('no_datatime')
                time.sleep(20)


def set_call_time(*time):
    print('time ', time)
    if not time[0] in call_time:
        #print("-----------------")
        index = time[0]
        thread = ThreadCheck(queue, time[2], False)
        call_time[time[0]] = (thread, 0, 0, time[1])
        thread.setDaemon(True)
        thread.start()
        thread_list.append(thread)
        queue.put(index)
    else:
        call_time[time[0]][3] = time[1]


def update_thread(id_main_class, id_user):
    #print('+++++++\nupdate_thread\n+++++ ')
    for i in call_time:
        #print('id_user ', id_user)
        #print('call_time[i][3] ', call_time[i][4])

        if id_user == call_time[i][4]:
            call_time[i][0].update(id_main_class, False)


def start_create_thread(updater, all_remember):
    for i in all_remember:
        if not i[0] in call_time:
            index = i[0]
            thread = ThreadCheck(queue, updater, True)
            call_time[i[0]] = (thread, i[1], i[2], i[3], i[4])
            thread.setDaemon(True)
            thread.start()
            thread_list.append(thread)
            queue.put(index)


def update_call_time(mes):
    tt = call_time[mes[0][0]]
    if len(tt) == 5:
        call_time[mes[0][0]] = (tt[0], tt[1], tt[2], mes[1], tt[4])
    else:
        call_time[mes[0][0]] = (tt[0], tt[1], tt[2], mes[1])


def delete_call_time(index):
    tt = call_time[index[0]]
    if len(tt) == 5:
        call_time[index[0]] = (tt[0], tt[1], tt[2], 0, tt[4])
    else:
        call_time[index[0]] = (tt[0], tt[1], tt[2], 0)
    print('call_time ', call_time)
