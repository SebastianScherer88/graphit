class ParseMe(object):

    def __init__(self):
        pass

    def function_1(self):

        print('function_1')

    def function_2(self,n:int):
        for i in range(n):
            self.function_1()
            print('function_2')