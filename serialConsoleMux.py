#!/usr/bin/python

import os, subprocess, sys, time


EXIT_CODE_INVALID_NUM_ARGS = 1
EXIT_CODE_UNKNOWN_COMMAND = 2
EXIT_CODE_INTERNAL_ERROR = 3

ARG_EMB = "emb"

EXECUTABLE = os.path.basename(sys.argv[0])


class TimeDiff:
    def __init__(self):
        __startTime_s = None
        self.setStartTime_now()
        
        
    def setStartTime_now(self):
        __startTime_s = time.time()
        
        
    def getElapsedTime_s(self):
        return time.time() - self.__startTime_s
        return 0
    
    
    def isElapsed_s(self, secsIn):
        return (self.getElapsedTime_s() > secsIn)
    

def __main():
    # see if the user is asking for help
    if( (len(sys.argv) == 1) or (sys.argv[1] == "-h") or (sys.argv[1] == "--help") or (sys.argv[1] == "help") ):
        # parse our command-line arguments
        printUsage()
        sys.exit()

    # we've got at least at least enough for a command
    commandIn = sys.argv[1]

    try:
        if( commandIn == "push" ):
            __checkNumArgs(5)
            __push(sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif( commandIn == "pull" ):
            __checkNumArgs(5)
        
        elif( commandIn == ARG_EMB ):
            print "emb"
                
        else:
            printError("Unknown command: '%s'" % commandIn)
            sys.exit(EXIT_CODE_UNKNOWN_COMMAND)
                
    except ValueError as e:
        printError(e.message)
        sys.exit(EXIT_CODE_INTERNAL_ERROR)


def printUsage():
    print "Serial Console Multiplexer"
    print "Send and receive files and directories via a serial TTY"
    print "Note: Assumes serial port baud rate has already been configured by your serial console program"
    print("")
    print "Usage:"
    print "   Push a file/directory to the embedded system:"
    print "   ./%s push <tty> <localPath> <targetPath>" % EXECUTABLE
    print "      <tty>                   path to serial port (eg. /dev/ttyUSB0)"
    print "      <localPath>             path of local file or directory to send to embedded system"
    print "      <targetPath>            target path for received files on embedded system"
    print("")
    print "   Pull a file/directory from the embedded system:"
    print "   ./%s pull <tty> <targetPath> <localPath>" % EXECUTABLE
    print "      <tty>                   path to serial port (eg. /dev/ttyUSB0)"
    print "      <targetPath>            target file or directory to pull from embedded system"
    print "      <localPath>             local path to store file or directory pulled from embedded system"
    print("")
    

def printError(errorMsgIn):
    print "\nError:"
    print errorMsgIn
        

def __push(ttyIn, localPathIn, targetPathIn):    
    # make sure the target path is sane
    if( not(targetPathIn.startswith(os.sep)) ): raise ValueError("targetPath is relative...cowardly refusing")
    
    if( os.path.isdir(localPathIn) ): __pushDir(ttyIn, os.path.abspath(localPathIn), targetPathIn)
    elif( os.path.isfile(localPathIn) ): __pushFile(ttyIn, os.path.abspath(localPathIn), targetPathIn)
    else: raise ValueError("not sure if localPath is file or directory")


def __pushFile(ttyIn, localFileIn, targetPathIn):
    print "Writing file to target..."
    
    print "Opening serial port '%s'..." % ttyIn
    serPort = __prepSerialPort(ttyIn)
    
    # figure out where our target is
    targetFile = None
    targetFile_parentDir = None
    if( targetPathIn.endswith(os.sep) ):
        targetFile = os.path.join(targetPathIn, os.path.basename(localFileIn))
        targetFile_parentDir = targetPathIn
    else:
        targetFile = targetPathIn
        targetFile_parentDir = os.path.dirname(targetPathIn)
    
    print("")    
    print "localFile: '%s'" % localFileIn
    print "targetFile: '%s'" % targetFile
    print "targetFileParentdir: '%s'" % targetFile_parentDir
    print("")
    
    # don't delete the file since we'll just overwrite it
    
    # make sure the required directory structure to the target file exists
    print "ensuring directory structure is in place..."
    serPort.write("\nmkdir -p %s\n" % targetFile_parentDir)
    
    # get the remote system ready to receive
    print "prepping target for reception..."
    serPort.write("\n echo -e \"\\nPress ctrl-d when transfer is complete...\\n\"")
    serPort.write("\nbase64 -d | gunzip > %s\n" % targetFile)
    time.sleep(1)
    
    # send our data
    print "sending file..."
    command = "gzip --stdout %s | base64" % localFileIn
    print command
    subprocess.call(command, stdout=serPort, shell=True)
    
    print("")
    print "transfer complete...press ctrl-d on target"
    

def __pushDir(ttyIn, localDirIn, targetPathIn):
    print "Writing directory to target..."
    
    print "Opening serial port '%s'..." % ttyIn
    serPort = __prepSerialPort(ttyIn)
    
    # can't use os.path.isdir on target (since it's remote)
    # so make our decision based upon the presence of a separator
    if( targetPathIn.endswith(os.sep) ):
        # eg. targetPathIn = /root/tmp/
        # targetDir --> /root/tmp/<last dir of local path>
        targetDir = os.path.join(targetPathIn, os.path.basename(localDirIn))
    else:
        # eg. targetPathIn = /root/tmp
        # targetDir_parentDir --> /root
        # targetDir --> /root/tmp
        targetDir = targetPathIn 
    
    print("")    
    print "localDir: '%s'" % localDirIn
    print "targetDir: '%s'" % targetDir
    print("")
    
    # make sure we're not messing with the root directory
    if( __isRootDir(targetDir) ): raise ValueError("targetDir is root ('/')...cowardly refusing")
    
    # delete the target file if it exists
    print "deleting '%s'..." % targetDir
    serPort.write("\nrm -f %s\n" % targetDir)
    
    # make sure the required directory structure to the target file exists
    print "ensuring directory structure is in place..."
    serPort.write("\nmkdir -p %s\n" % targetDir)
    
    # get the remote system ready to receive
    print "prepping target for reception..."
    serPort.write("\n echo -e \"\\nPress ctrl-d when transfer is complete...\\n\"")
    serPort.write("\nbase64 --decode | tar -C %s -zxv\n" % targetDir)
    time.sleep(1)
    
    # send our data
    print "sending file..."
    command = "tar -C %s -cz . | base64" % localDirIn
    print command
    subprocess.call(command, stdout=serPort, shell=True)

    print("")
    print "transfer complete...press ctrl-d on target"
    

def __prepSerialPort(ttyIn):
    # make sure our serial port exists
    if( not(os.path.exists(ttyIn)) ): raise ValueError("invalid TTY specified")
    
    serPort = open(ttyIn, "r+")
    
    # make sure we aren't currently running any processes
    # and that we don't have any stray characters on the terminal...
    # (send ctrl-c and wait for it to settle)
    serPort.write('\x03')
    time.sleep(1)
    return serPort


def __isRootDir(pathIn):
    head, tail = os.path.split(pathIn)
    return (head == os.sep) and (len(tail) == 0)


def __checkNumArgs(expectedNumArgsIn):
    if( len(sys.argv) != expectedNumArgsIn ):
        printError("Invalid number of arguments")
        sys.exit(EXIT_CODE_INVALID_NUM_ARGS)
        

if __name__ == "__main__":
    __main()