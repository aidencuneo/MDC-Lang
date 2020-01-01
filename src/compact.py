'''

definition,

    __init__,

    __magicmethods__,

    appending/adding methods,

    splicing/removing methods,

    getting/retrieving methods,

    boolean returning methods,

'''


class CompactList:

    def __init__(self, *values):
        __slots__ = []
        self._value = ()
        values = values[0] if len(values) == 1 else values
        for a in values:
            self.append(a)
    
    def __repr__(self):
        return str(list(self._value))
    
    def __str__(self):
        return str(list(self._value))
    
    def __eq__(self, value):
        return self._value == value
    
    def __getitem__(self, item):
        return self._value[item]
    
    def __setitem__(self, item, value):
        self.setitem(item, value)
    
    def __delattr__(self, index):
        self.delete_from(index)
    
    def __contains__(self, item):
        return item in self._value
    
    def setitem(self, item, value):
        self._value = list(self._value)
        self._value[item] = value
        self._value = tuple(self._value)

    def append(self, value):
        self._value += tuple([value])

    def extend(self, value):
        self._value += tuple(value)

    def delete_from(self, index):
        self._value = list(self._value)
        del self._value[index]
        self._value = tuple(self._value)
    
    def index(self, item):
        return self._value.index(item)

    def is_empty(self):
        return not bool(self._value)

    def has_data(self):
        return bool(self._value)


class CompactDict:

    def __init__(self, values=None):
        __slots__ = []
        self._value = CompactList()
        values = {} if values is None else values
        for a in values:
            self.setitem(a, values[a])

    def __repr__(self):
        return self.as_dict()

    def __str__(self):
        return str(self.as_dict())
    
    def __delattr__(self, key):
        self.delete_key(key)

    def __getitem__(self, item):
        return self.getitem(item)

    def __setitem__(self, key, value):
        return self.setitem(key, value)
    
    def __contains__(self, key):
        return key in self.as_dict()

    def setitem(self, key, value):
        if key in self.keys():
            self._value[self.keys().index(key)][1] = value
        else:
            self._value.append(CompactList(key, value))

    def getitem(self, name):
        if all([a in '0123456789' for a in str(name)]) and name not in self.keys()._value:
            return self.keys()[name]
        return self.as_dict()[name]

    def as_dict(self):
        return {a[0] : a[1] for a in self._value}
    
    def keys(self):
        return CompactList([a[0] for a in self._value])
    
    def values(self):
        return CompactList([a[1] for a in self._value])
    
    def delete_key(self, key):
        if key in self.keys()._value:
            del self._value[self.keys().index(key)]
        else:
            raise KeyError

    def is_empty(self):
        return not bool(self.as_dict())

    def has_data(self):
        return bool(self.as_dict())
