class ConstList:
    def __init__(self, length):
        self.l = range(length)
        self.count = 0
        self.length = length

    def add(self, obj):
        if self.count == self.length - 1:
            self.count = 0
        else:
            self.count += 1

        self.l[self.count] = obj

    def extend(self, objs):
        for o in objs:
            self.add(o)

    def get(self):
        return self.l[self.count + 1: self.length] + self.l[:self.count + 1]

    def __str__(self):
        string = ""
        for a in self.get():
            string += str(a) + ' '
        return string.rstrip()

    def __iter__(self):
        for a in self.get():
            yield a
