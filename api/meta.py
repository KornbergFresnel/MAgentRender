import collections


State = collections.namedtuple('State', ['id', 'alive', 'position'])


class StateList(object):
    def __init__(self, list_data=None):
        self._data = []
        self._len = 0

        if list_data is not None and type(list_data) == list:
            self._len = len(list_data)
            for i in range(self._len):
                self._data.append(State(*list_data[i]))
    
    def __getitem__(self, key):
        if 0 > key or key >= self._len:
            raise IndexError
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __len__(self):
        return self._len
            