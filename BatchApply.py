import sys, os, os.path, re, threading as t, subprocess as p, random as r, traceback as tb

'''
Author: <Daniel Alexander Apatiga (daniel.apatiga@pickupfit.com)>
This class will allow you to do batch options on multiple files.
To get filename : re.match("(?<=\\\\)[\w\- %&#@!()
'''
class BatchApply:
    #obj variables
    #example: batchapply "d:/atomhid" "ffmpeg -i XXX -fh stabilize i
    #args = sys.argv
    starting_path = "" #args[1]
    starting_path_Y = ""
    template = "" #args[2]
    extension = "" #args[3]
    extension_Y = ""
    extractionPattern = ""
    fConstraintCompiled = ""#re.compile(args[4])
    fConstraintCompiled_Y = ""
    maxThreads = 2 #default 2 #args[5]
    flags = "" #args[6]
    templateReplacements = "" #args[7:]
    pathToThisFolder = ""
    filePaths = []
    filePaths_Y = []
    fileNames = []
    fileNames_Y = []
    totalFiles = 0
    totalFiles_Y = 0
    onFile = 0
    skipAllPrompts = False
    currentThread = 1
    newTemplates = []
    #re.match("(?<=\\\\)[\w\- %&#@!()_=+`~]?(?=\.)")
    def doFilenameMatching(self):
        self.starting_path = re.sub("[/\\\]", "/", self.starting_path)
        self.starting_path_Y = re.sub("[/\\\]", "/", self.starting_path_Y)
        print("Starting path of root directory X: " + self.starting_path)
        print("Starting path of root directory Y: " + self.starting_path_Y)
        print("Template: " + self.template)
        print("Generating filename and filepath list @ root directory X...")
        self.filePaths, self.fileNames = self.recurseGetFiles(self.starting_path, self.filePaths, self.fileNames,
                                                              self.extension)
        self.filePaths, self.fileNames = self.maybeSort(self.filePaths, self.fileNames)
        print("Filtering filepaths and filenames generated @ root directory X...")
        self.filePaths, self.fileNames, self.totalFiles = self.filterFiles(self.filePaths, self.fileNames,self.fConstraintCompiled, self.totalFiles)
        print("Generating new templates (round one...)")
        self.replaceTokensWithStrings()
        print("Generating filename and filepath list @ root directory Y...")
        self.totalFiles_Y = 0
        self.filePaths_Y, self.fileNames_Y = self.recurseGetFiles(self.starting_path_Y, self.filePaths_Y,
                                                                  self.fileNames_Y, self.extension_Y)
        print("Filtering filepaths and filenames generated @ root directory Y...")
        self.filePaths_Y, self.fileNames_Y, self.totalFiles_Y = self.filterFiles(self.filePaths_Y, self.fileNames_Y,
                                                                                 self.fConstraintCompiled_Y,
                                                                                 self.totalFiles_Y)
        if self.totalFiles_Y != len(self.filePaths):
            print("Total files @ root X: " + str(len(self.filePaths)) + ".  Total files @ root Y: " + str(
                self.totalFiles_Y))
            if not self.skipAllPrompts:
                while True:
                    res = input(
                        "Total files for root directory tree Y are unequal to those of root directory tree X.  Some files may be acted upon that shouldn't be, be warned!  Continue? (Y/N:) ")
                    if res == "y" or res == "Y":
                        break
                    elif res == "n" or res == "N":
                        print("Exited.")
                        sys.exit()
                    else:
                        print("Invalid response.  Please try again.")
                flag = 0
                while True:
                    res = input(
                        "More than one file in root directory Y may match generated string from root directory X.  Do you want to 1) prevent this? or, 2) let it happen? (Enter 1 or 2:)")
                    if res == "1":
                        flag = 0
                        break
                    elif res == "2":
                        flag = 1
                        break
                    else:
                        print("Invalid response.  Please try again.")
        print("Matching filenames of root directory Y with extracted-by-regex strings to filenames-of-root-directory-X list...")
        self.replaceTokensWithStringsFileMatching(self.extractionPattern, self.fileNames_Y, self.filePaths_Y, self.flags)
        print("Finished with generating new templates after round two.  Starting concurrent operations...")
        self.startThreads()
    def interactivePrompts(self):
        x = input("Match part of a discovered file with files in another directory? (Y/N):")
        if x == "y" or x == "Y":
            self.starting_path = input("Please type the starting path to the root directory X of the files where the file names' strings are to be extracted from the results (using regex):")
            self.starting_path = re.sub("[/\\\]", "/", self.starting_path)
            self.starting_path_Y = input("Please type the starting path to the root directory Y of the files to be eventually filtered out and matched with the files from root directory X:")
            self.starting_path_Y = re.sub("[/\\\]", "/", self.starting_path_Y)
            self.extension_Y = input("Please type the extension of the files @ root directory Y that are to be kept:")
            i = input("Please enter the regex for filtering out those files:")
            self.extractionPattern = re.compile(input("Please enter the regex for extracting the string from filenames @ domain X to match against filenames @ domain Y:"))
            self.fConstraintCompiled_Y = re.compile(i)
            print("Starting path of root directory X: " + self.starting_path)
            print("Starting path of root directory Y: " + self.starting_path_Y)
            print("Template: " + self.template)
            print("Generating filename and filepath list @ root directory X...")
            self.filePaths, self.fileNames = self.recurseGetFiles(self.starting_path, self.filePaths, self.fileNames, self.extension)
            self.filePaths, self.fileNames = self.maybeSort(self.filePaths, self.fileNames)
            print("Filtering filepaths and filenames generated @ root directory X...")
            self.filePaths, self.fileNames, self.totalFiles = self.filterFiles(self.filePaths,self.fileNames, self.fConstraintCompiled, self.totalFiles)
            print("Generating new templates (round one...)")
            self.replaceTokensWithStrings()
            print("Generating filename and filepath list @ root directory Y...")
            self.totalFiles_Y = 0
            self.filePaths_Y, self.fileNames_Y = self.recurseGetFiles(self.starting_path_Y, self.filePaths_Y, self.fileNames_Y, self.extension_Y)
            self.filePaths_Y, self.fileNames_Y = self.maybeSort(self.filePaths_Y, self.fileNames_Y)
            print("Filtering filepaths and filenames generated @ root directory Y...")
            self.filePaths_Y, self.fileNames_Y, self.totalFiles_Y = self.filterFiles(self.filePaths_Y,self.fileNames_Y, self.fConstraintCompiled_Y, self.totalFiles_Y)
            if self.totalFiles_Y != len(self.filePaths):
                print("Total files @ root X: " + str(len(self.filePaths)) + ".  Total files @ root Y: " + str(self.totalFiles_Y))
                while True:
                    res = input("Total files for root directory tree Y are unequal to those of root directory tree X.  Some files may be acted upon that shouldn't be, be warned!  Continue? (Y/N:) ")
                    if res == "y" or res == "Y":
                        break
                    elif res == "n" or res == "N":
                        print("Exited.")
                        sys.exit()
                    else:
                        print("Invalid response.  Please try again.")
            flag = 0
            while True:
                res = input("More than one file in root directory Y may match generated string from root directory X.  Do you want to 1) prevent this? or, 2) let it happen? (Enter 1 or 2:)")
                if res == "1":
                    flag = 0
                    break
                elif res == "2":
                    flag = 1
                    break
                else:
                    print("Invalid response.  Please try again.")
            print("Matching filenames of root directory Y with extracted-by-regex strings to filenames-of-root-directory-X list...")
            self.replaceTokensWithStringsFileMatching(self.extractionPattern, self.fileNames_Y, self.filePaths_Y, self.flags)
            print("Finished with generating new templates after round two.  Starting concurrent operations...")
            self.startThreads()
    def maybeSort(self, filePaths, fileNames):
        for c in self.flags:
            if re.search(re.compile("[k]"), c):
                self.skipAllPrompts = True
            elif re.search(re.compile("[c]"), c):
                print("Sorting filepaths in ascending order by creation date...")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 'c')
            elif re.search(re.compile("[C]"), c):
                print("Sorting filepaths in descending order by creation date...")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 'C')
            elif re.search(re.compile("[m]"), c):
                print("Sorting filepaths in ascedning order by modification date...")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 'm')
            elif re.search(re.compile("[M]"), c):
                print("Sorting filepaths in descending order by modification date...")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 'M')
            elif re.search(re.compile("[s]"), c):
                print("Sorting filepaths in ascending order by string (name...)")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 's')
            elif re.search(re.compile("[S]"), c):
                print("Sorting filepaths in descending order by string (name...)")
                filePaths, fileNames = self.sortFilePathsOnMakeTimes(filePaths, fileNames, 'S')
        return filePaths, fileNames
    def sortFilePathsOnMakeTimes(self, filepathsCopies, filenamesCopies, flag):
        if flag == 'c': #sort in ascending order with what happened first last.
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    tempPathY = filepathsCopies[y]
                    fileNY = filenamesCopies[y]
                    if os.path.getctime(tempPathX) > os.path.getctime(tempPathY):
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
                        #templates[y] = templateX
                        #templates[x] = templateY
        elif flag == 'C':
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    tempPathY = filepathsCopies[y]
                    fileNY = filenamesCopies[y]
                    if os.path.getctime(tempPathX) < os.path.getctime(tempPathY):
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
        elif flag == 'm': #sort in ascending order with what happened first last.
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    tempPathY = filepathsCopies[y]
                    fileNY = filenamesCopies[y]
                    if os.path.getmtime(tempPathX) > os.path.getmtime(tempPathY):
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
                        #break
                        #templates[y] = templateX
                        #templates[x] = templateY
        elif flag == 'M':
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    tempPathY = filepathsCopies[y]
                    fileNY = filenamesCopies[y]
                    if os.path.getmtime(tempPathX) < os.path.getmtime(tempPathY):
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
        elif flag == 's': #sort in ascending order with what happened first last.
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    fileNY = filenamesCopies[y]
                    tempPathY = filepathsCopies[y]
                    if fileNX > fileNY:
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
                        #templates[y] = templateX
                        #templates[x] = templateY
        elif flag == 'S':
            for x in range(0, len(filepathsCopies)):
                tempPathX = filepathsCopies[x]
                fileNX = filenamesCopies[x]
                for y in range(x + 1, len(filepathsCopies)):
                    tempPathY = filepathsCopies[y]
                    fileNY = filenamesCopies[y]
                    if fileNX < fileNY:
                        filepathsCopies[x] = tempPathY
                        filepathsCopies[y] = tempPathX
                        filenamesCopies[x] = fileNY
                        filenamesCopies[y] = fileNX
                        break
        return filepathsCopies, filenamesCopies
    def setArguments(self, args = []):
        rootX = False
        rootY = False
        hasTemplate = False
        extractionP  = False
        extX = False
        extY = False
        xcons = False
        ycons = False
        for item in args:
            if item[0] == "-dirX":
                self.starting_path = item[1]
                rootX = True
            elif item[0] == "-tR":
                self.templateReplacements.append(item[1])
            elif item[0] == "-dirY":
                rootY = True
                self.starting_path_Y = item[1]
            elif item[0] == "-Xex":
                extX = True
                self.extension = item[1]
            elif item[0] == "-Yex":
                extY = True
                self.extension_Y = item[1]
            elif item[0] == "-flags":
                self.flags = item[1]
            elif item[0] == "-Tc":
                self.maxThreads = int(item[1])
            elif item[0] == "-templ":
                hasTemplate = True
                self.template = item[1]
            elif item[0] == "-e":
                extractionP = True
                self.extractionPattern = re.compile(item[1])
            elif item[0] == "-Xcons":
                xcons = True
                self.fConstraintCompiled = re.compile(item[1])
            elif item[0] == "-Ycons":
                ycons = True
                self.fConstraintCompiled_Y = re.compile(item[1])
            elif item[0] == "-m":
                if item[1] == 'interactive':
                    self.interactivePrompts()
                    return
                else:
                    print("Not a valid mode.  Exiting...")
                    sys.exit()
        l = [hasTemplate, rootX, extX, xcons, not rootY]
        p = [hasTemplate, rootX, extX, xcons, rootY, extY, ycons, extractionP]
        if all(l):
            self.doSingleRootMethod()
        elif all(p):
            self.doFilenameMatching()
    def __init__(self, args = []):
        self.setArguments(args)
    def doSingleRootMethod(self):
        print("Starting path: " + self.starting_path)
        print("Template: " + self.template)
        self.pathToThisFolder = os.getcwd()
        print("Note: results may end up in this folder depending on the software: " + self.pathToThisFolder)
        self.filePaths, self.fileNames = self.recurseGetFiles(self.starting_path, self.filePaths, self.fileNames, self.extension)
        self.filePaths, self.fileNames = self.maybeSort(self.filePaths, self.fileNames)
        print("Filtering files...")
        self.filePaths, self.fileNames, self.totalFiles = self.filterFiles(self.filePaths, self.fileNames, self.fConstraintCompiled, self.totalFiles)
        print("Generating new templates...")
        self.replaceTokensWithStrings()
        print("Starting concurrent operations...")
        self.startThreads()
    def generateRandomNumberString(self):
        number = r.randint(0,10000) ^ r.randint(0,10000)
        return str(number)
    def recurseGetFiles(self, starting_path, filePaths, fileNames, extension):
        print("Searching matching files in " + starting_path + "...")
        if extension != ".*":
            for (dirpath, dirnames, filenames) in os.walk(starting_path):
                dirpath = re.sub("\\\\", "/", dirpath)
                for filename in [f for f in filenames if f.endswith(extension)]:
                    stri = dirpath + "/" + filename
                    filePaths.append(stri)
                    fileNames.append(filename)
                    print("Found file: " + stri)
            return filePaths, fileNames
        else:
            for (dirpath, dirnames, filenames) in os.walk(starting_path):
                dirpath = re.sub("\\\\", "/", dirpath)
                for filename in [f for f in filenames]:
                    stri = dirpath + "/" + filename
                    filePaths.append(stri)
                    fileNames.append(filename)
                    print("Found file: " + stri)
            return filePaths, fileNames
    def startThreads(self):
        while len(self.newTemplates) > 0:
            if t.active_count() >= int(self.maxThreads):
                continue
            else:
                self.startThread(self.newTemplates.pop(0))
    def filterFiles(self, filePaths, fileNames, fConstraintCompiled, totalFiles):
        filePathCopies = filePaths[:]
        fileNamesCopies = fileNames[:]
        fileNames = []
        filePaths = []
        while len(filePathCopies) > 0:
            path = filePathCopies[0]
            fN = fileNamesCopies[0]
            filePathCopies.pop(0)
            fileNamesCopies.pop(0)
            result = re.search(fConstraintCompiled, str(fN))
            if result is None:
                continue
            else:
                totalFiles += 1
                filePaths.append(path)
                fileNames.append(fN)
        return filePaths, fileNames, totalFiles
    def replaceTokensWithStringsFileMatching(self, pattern, fileNames, filePaths, flag=1):
        fileN = re.compile("NNN")
        countX = 0
        newTemplateCopies = self.newTemplates[:]
        self.newTemplates = []
        while countX < len(newTemplateCopies):
            nameOfFileDomainX = self.fileNames[countX]
            template = newTemplateCopies[countX]
            #print("Template: " + template + ". Name of file from domain X: " + nameOfFileDomainX)
            test = re.search(pattern, nameOfFileDomainX)
            if test == None:
                print("Could not extract the string to be matched from domain X to domain Y.  Exiting because of fundamental error...")
                print("Pattern was: " + pattern.__str__() + ".  Name of file from domain X: " + nameOfFileDomainX)
                i = input("Skip? (y/n")
                if i == "y" or i == "Y":
                    countX += 1
                    continue
                elif i == "n" or i =="N":
                    sys.exit()
                else:
                    countX += 1
                    print("Continuing because of invalid response...")
            else:
                stringToBeMatched = test.group(0)
                #print("String to be matched against files from root directory Y: " + stringToBeMatched)
                countY = 0
                while countY < len(fileNames):
                    nameOfFileDomainY = fileNames[countY]
                    #print("Filename @ root directory Y: " + nameOfFileDomainY)
                    res = re.search(stringToBeMatched, nameOfFileDomainY)
                    if res != None:
                        if flag == 0:
                            template = re.sub(fileN, filePaths[countY], template)
                            fileNames.pop(countY)
                            filePaths.pop(countY)
                            print("New template: " + template)
                            self.newTemplates.append(template)
                            break #comment this
                        else:
                            template = re.sub(fileN, filePaths[countY], template)
                            print("New template: " + template)
                            self.newTemplates.append(template)
                            break
                    elif countY > len(fileNames):
                        print("No matches from domain Y found for file, " + nameOfFileDomainX + ", @ domain X. Skipping the file...")
                        break
                    countY += 1
            countX += 1
    def replaceTokensWithStrings(self):
        name = re.compile("JJJ")
        rand = re.compile("RRR")
        pat = re.compile("XXX")
        fileR =  re.compile("ZZZ")
        matches = re.findall(pat, self.template)
        #print(len(matches))
        #print(self.templateReplacements)
        if len(self.filePaths) == 0:
            print("Files to be batched should have a size of at least one.")
            sys.exit()
        if not len(matches) == len(self.templateReplacements):
            print("You have a different amount of template replacements when compared to what you specified in the template argument.  Please correct this and try again!")
            sys.exit()
        filePaths = self.filePaths[:]
        fileNames = self.fileNames[:]
        for x in range(0, len(self.filePaths)):
            templateCopy = self.template[:]
            templateReplacementsCopy = self.templateReplacements[:]
            while len(re.findall(rand, templateCopy)) > 0:
                templateCopy = re.sub(rand, self.generateRandomNumberString(), templateCopy)
            fpath = filePaths.pop(0)
            while len(re.findall(fileR, templateCopy)) > 0:
                templateCopy = re.sub(fileR, fpath, templateCopy)
            fname = fileNames.pop(0)
            while len(re.findall(name, templateCopy)) > 0:
                templateCopy = re.sub(name, fname, templateCopy)
            while len(re.findall(pat, templateCopy)) > 0:
                templateCopy = self.reSubOnce(pattern=pat, replacement=self.templateReplacements.pop(0), string=templateCopy)
            print("New template: " + templateCopy)
            self.newTemplates.append(templateCopy)
    def reSubOnce(self, pattern, replacement, string):
        result = re.search(pattern, string)
        if result:
            start, end = result.span() #gets first occurrance
            string = string[0:start] + replacement + string[end:]
        return string
    def subP(self, templateNew, targ):
        self.currentThread += 1
        copyOf = str(self.currentThread)
        print("[STARTED thread#" + copyOf + ".] Argument=" + templateNew + ". Target=" + targ + ".")
        try:
            result = p.Popen(args=targ + " " + templateNew, shell=True, stdout = p.PIPE, stderr = p.PIPE)
            s = result.communicate()
            self.onFile += 1
        except:
            b = tb.print_exc()
            print(b)
            print("[FAILURE thread#" + copyOf + "]\n" + s)
        else:
            print("[THREAD#" + copyOf + "]")
            print(s)
        finally:
            print(str(self.onFile / self.totalFiles * 100) + "% complete...")
            print("[FINISHED thread#" + copyOf + ".] There are " + str(t.active_count()) + " active threads.")
    def startThread(self, templateNew):
        match = re.search(" ", templateNew)
        if match is not None:
            st = match.start()
            targ = templateNew[0:st]
            templateNew = templateNew[st + 1:]
            thread = t.Thread(target=self.subP, args=[templateNew, targ], daemon=False)
            thread.start()
        else:
            print("Could not match the first part of the template that is supposed to be the target executable.  Make sure you have a space between it and the rest of the parameters.")
#x = re.search('(?<=123).+(?=\.trf)', '123asdfsdfsdf.trf')
#print(x.group(0))
#clas = BatchApply()
#time = ti.ctime(clas.getCMakeMetaData("setup.py"))
#print(time)
#start = BatchApply()