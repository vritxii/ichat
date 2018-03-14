from backup import genesis
import inspect
import json
class A:
    __x = 0.0
    def __init__(self, args={}):
        defaults = {}
        genesis.Init(self, args, defaults)
        pass

    def add(self):
        print('a')
        pass

def __init(self, args={'b':0}):
    self.b = args['b']

def newb(self, b):
    self.b = b
    print(self.b)
    print('Hello')
    pass

def HHH(a:int, b:str):
    pass

def AAA(args={'a':0,'b':0}):
    print(args)
    pass

def a(self,x):
    self.x = x
    print(self.x)

def run_server(x):
    if x.n:
        x = genesis.EnhanceObject(x, {'a':a})
    return x

class X:
    def __init__(self, args={'n':False}):
        self.n = args['n']
        

if __name__ == '__main__':
    genesis.InitBothHaveFuncs()
    genesis.InitPacketDealFuncs()
    genesis.InitServerFuncs()
    genesis.InitClientFuncs()
    genesis.SetVersionsFuncSet()
    genesis.DefineVersion()
    print(genesis.Version)
    ITest = genesis.CreateClass('ITest', ['Test'], 'C')
    it = ITest()
    it.Test(20)
    
    it = genesis.EnhanceObject(it, {'newb':newb, '__init__':__init})
    print(hasattr(it, 'newb'))
    print(it.__dir__())
    it.newb(10)
    print(type(it))
    #print(genesis.ClientPool.keys())
    x = X({'n':True})
    x = run_server(x)
    x.a(100)



    