import BatchApply, ArgumentMatcher, sys, IOFile
t = IOFile.IOFile()
helpFText = t.getFileTxt(sys.path[0] + "\\" + "help.txt")
batchapply = {"-dirX" : "Root directory X, or the starting directory.  This param. is required.",
              "-dirY" : "Root directory Y, or the starting directory.  This param. is NOT required.",
              "-Xex" : "Root directory X filename-extension requirement.",
              "-Yex" :  "Root directory Y filename-extension requirement.",
              "-flags" : "Used for sorting the templates before acting on files: useful for when the files that are created or modifed are dependent on the other.",
              "-Tc" : "The number of threads that can be running at the same time.  A minimum of two should be this value.",
              "-Xcons" : "Regex constraint for the name of the generated files from root directory X.",
              "-Ycons" : "Regex constraint for the name of the generated files from root directory Y.",
              "-h" : (0, helpFText),
              "-H" : (0, helpFText),
              "-templ" : "The template that can accept ZZZ, JJJ, NNN, or RRR tokens.",
              "-m" : "Sets the mode.",
              "-e" : "Filename matching reg expr. for finding corresponding strings for comparing filenames from root directory X with files from root directory Y."}
a = ArgumentMatcher.ArgumentMatcher()
#b = dict(zip(map(a.makeCompiledPattern, batchapply.keys()), batchapply.values()))
a.setCharKeys(batchapply)
a.sortArgumentParameters()
args = a.getSortedArguments()
#print(str(argumentStart.getSortedArguments()))
ba = BatchApply.BatchApply(args)