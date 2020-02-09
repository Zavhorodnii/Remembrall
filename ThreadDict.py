
__id_main_class = None
__thread_dict = dict()



def dict_get(index):
    return __thread_dict[index]


def dict_set(index, value):
    __thread_dict[index] = value


def dict_del(index):
    __thread_dict[index] = 0
