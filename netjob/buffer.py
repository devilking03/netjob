import numpy as np
import pickle

def makeNPArray(*kwargs):
    return np.asarray(kwargs)

def makeNPBuffer(*kwargs):
    return np.asarray(kwargs).tobytes()

def serializeObject(pyObj):
    return pickle.dumps(pyObj)

def deserializeObject(buffer):
    #try:
    return pickle.loads(buffer)
    #except pickle.UnpicklingError:
    #    raise RuntimeError("Unpickle Error")
