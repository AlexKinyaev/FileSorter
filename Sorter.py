
import sys
import os
import getopt
import time
import shutil 
import signal

FileFilter = [".png", ".jpg", "bmp", "jpeg", "mpg", "avi", "mov",""]

def signal_handler(sig, frame):
        print('You cancelled process')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def MoveFile(File, DstPath):

    DateList = [time.strftime("%Y", time.gmtime(os.path.getmtime(File))), 
                time.strftime("%B", time.gmtime(os.path.getmtime(File))), 
                    time.strftime("%d", time.gmtime(os.path.getmtime(File)))]

    for Date in DateList:

        DstPath = os.path.join(DstPath, Date)

        if os.path.exists(DstPath):
            pass
        else:
            os.mkdir(DstPath)

    try:
        shutil.copy2(File, DstPath)
        print(File, ' -> ',  DstPath)
    except:
        print(File, ' is exist in: ',  DstPath)

def AnalyzeFile(File):

    global FileFilter

    FileExt = ''

    try:
        FileExt = os.path.splitext(File)[1]
    except:
        return False



    return FileExt.lower() in FileFilter


def ContentEnumerator(SrcPath, DstPath):

    print("Enter in Directory:", SrcPath)

    for item in os.listdir(SrcPath):
        NewPath = os.path.join(SrcPath, item)
        if os.path.isdir(NewPath):
            ContentEnumerator(NewPath, DstPath)
        elif os.path.isfile(NewPath):
            #print("File:" + Path + item)
            if AnalyzeFile(NewPath):
                MoveFile(NewPath, DstPath)
        else:
            print("Special file:", Path + item)

def main():

    ListArgv = sys.argv

    if len(ListArgv) < 3:
        print('Sorter.py <Source Directory Path> <Destination Directory Path>')
        sys.exit(2)

    for Path in ListArgv[1:]:

        if not os.path.exists(os.path.join(Path, '')):
            print('Path:', Path, "doesn't exist.")
            sys.exit(2)

    ContentEnumerator(ListArgv[1], ListArgv[2])


if __name__ == "__main__":
    main()

