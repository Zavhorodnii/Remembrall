import time
import threading
from queue import Queue

thread_list = list()
call_time = [1,2,3,4,5,6,7,8,9]


class Thread_mess(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            id_mess = self.queue.get()
            print('\n++ ', call_time[id_mess])
            time.sleep(3)
            if len(thread_list) == len(call_time):
                self.queue.task_done()
                break


def main():
    queue = Queue()

    for i in range(len(call_time)):
        thread = Thread_mess(queue)
        thread.setDaemon(True)
        thread.start()
        thread_list.append(thread)

    for i in range(len(call_time)):
        queue.put(i)

    queue.join()

    for i in thread_list:
        print(i)


if __name__ == "__main__":
    main()