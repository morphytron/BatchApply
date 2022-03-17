import re
#GET A SPECIFIC FILE TXT.
class IOFile:
    def __init__(self):
        pass
    def getFileTxt(self, path):
        final_str = ""
        with open(path, "r") as f:
            for line in f.readlines():
                final_str += line
        return final_str
    def getFileTxtAsArrayForEveryDelimiter(self, path, delimiter = "\n"):
        final_array = []
        with open(path, "r") as f:
            content = f.read()
            array = re.split(re.compile(delimiter), content)
            for s in array:
                final_array.push(s)
        return final_array