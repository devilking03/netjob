from netjob import buffer

HEADER_ALIGN = 256

class SerializableJob:
    SIGNATURE = "JOBCLASS"

    def __init__(self, fn, params = ()):
        self.__fn = fn
        self.__params = params
    def getFn(self):
        return self.__fn
    def getParams(self):
        return self.__params
    def doAction(self):
        return self.__fn(*self.__params)

class Job:
    __jobBin = b''

    def __init__(self, actionFunction, params = (), callback = None, callbackArgs = ()):
        self.__callback = callback
        self.__cbArgs = callbackArgs
        self.__jobBin = buffer.serializeObject(SerializableJob(actionFunction, params))

    def getJobPack(self):
        return self.__jobBin
    
    def fireCallback(self, params):
        if self.__callback:
            self.__callback(buffer.deserializeObject(params), *self.__cbArgs)
