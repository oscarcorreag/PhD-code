class CandidatesList(list):
    def __init__(self, maxlen):
        super(CandidatesList, self).__init__()
        self.__maxlen = maxlen

    def append(self, p_object):
        super(CandidatesList, self).append(p_object)
        self.sort()
        if self.__len__() > self.__maxlen:
            self.pop()
