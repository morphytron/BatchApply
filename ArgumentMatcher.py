import re, sys, IOFile
class ArgumentMatcher:
    args = sys.argv
    newArgs = []
    charkeys = {}
    def makeCompiledPattern(self, stri):
        return re.compile(stri)
    def setCharKeys(self, dic = {}):
        self.charkeys = dic
    '''
    The key is the unique character that identifies the beginning of the argument, 
    The value is string or number or other data.
    '''
    def sortArgumentParameters(self):
        args = self.args[1:]
        print(str(args))
        initialSizeOfArgs = len(args)
        count = 0
        t = IOFile.IOFile()
        print("Initial size of arguments, exluding first: " + str(initialSizeOfArgs))
        while len(self.newArgs) * 2 < initialSizeOfArgs:
            #print("Count#:" + str(count) + ".  Parameter argument#: " + str(len(self.newArgs)))
            for arg in args[count:]:
                for key in self.charkeys.keys():
                    result = re.search(key, arg)
                    if result:
                        value = self.charkeys[key]
                        if type(value) is tuple:
                            print("Tuple found...")
                            if value[0] == 0:
                                print(value[1])
                                count += 1
                            elif value[0] == 1:
                                print(str(t.getFileTxtAsArrayForEveryDelimiter(value[1])))
                                count += 1
                            break
                        else:
                            self.newArgs.append((key, args[count+1]))
                            count += 2
                            break
            else:
                if count % 2 == 1:
                    break;
        #print(str(self.newArgs))
    def getSortedArguments(self):
        return self.newArgs
#argument = ArgumentMatcher()
#test = {"\-f" : "flag", "\-s" : "cag", "\-b" : "bologne"}
#test = dict(zip(map(argument.makeCompiledPattern, test.keys()), test.values()))
#print(str(test))
#argument.setCharKeys(test)
#argument.sortArgumentParameters()
#print(str(argument.getSortedArguments()))