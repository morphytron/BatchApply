import sys
class Read:
    def __init__(self):
        with open(sys.argv[1], 'r') as f:
            string = ''
            for line in f.readlines():
                string += line
            print(string)
Read()