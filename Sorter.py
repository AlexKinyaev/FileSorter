
import sys
import os
import getopt
import time
import shutil 
import signal
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import googlemaps
import datetime

FileFilter = [".png", ".jpg", ".bmp", ".jpeg", ".mpg", ".avi", ".mov", ".3gp", ".mkv"]

def signal_handler(sig, frame):
        print('You have cancelled the process.')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def getExifInfo(file):
    
    ExifInfo = {}
    image = Image.open(file)

    FullExif = None

    try:
        FullExif = image._getexif()
    except:
        return ExifInfo

    if FullExif:
        for tag, value in FullExif.items():

            decoded = TAGS.get(tag, tag)
            
            if decoded == "GPSInfo":
                gps_data = {}
                for gpst in value:
                    sub_decoded = GPSTAGS.get(gpst, gpst)
                    gps_data[sub_decoded] = value[gpst]

                ExifInfo[decoded] = gps_data
            elif decoded == "DateTimeOriginal":
                ExifInfo[decoded] = value

    return ExifInfo

def ConvertToDegress(value):

    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def GetLocationName(Coordinates):

    gps_latitude = Coordinates["GPSLatitude"]
    gps_latitude_ref = Coordinates["GPSLatitudeRef"]

    gps_longitude = Coordinates["GPSLongitude"]
    gps_longitude_ref = Coordinates["GPSLongitudeRef"]

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:

        lat = ConvertToDegress(gps_latitude)
        if gps_latitude_ref != "N":                     
            lat = 0 - lat

        lng = ConvertToDegress(gps_longitude)
        if gps_longitude_ref != "E":
            lng = 0 - lng

    #return lat, lng

    gmaps = googlemaps(api_key="AIzaSyC-Q-Pk0bCBfaCofSS9cPZAFRHNXLD6EZg")

    local = gmaps.latlng_to_address(38.887563, -77.019929)

    #my_location = GoogleMaps.search(lat=lat, lng=lng)

    return


def GetFolderName(File):

    DateList = None
    FolderName = None

    Info = getExifInfo(File)

    if len(Info):
        if "GPSInfo" in Info:
            GetLocationName(Info["GPSInfo"])
            pass

    if not FolderName:
        FolderName = time.strftime("%d", time.gmtime(os.path.getmtime(File)))

    DateList = [time.strftime("%Y", time.gmtime(os.path.getmtime(File))), 
                time.strftime("%B", time.gmtime(os.path.getmtime(File))), 
                FolderName]

    for Date in DateList:

        DstPath = os.path.join(DstPath, Date)

        if os.path.exists(DstPath):
            pass
        else:
            os.mkdir(DstPath)


def MoveFile(File, DstPath):

    GetFolderName(File)

    return

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
            if AnalyzeFile(NewPath):
                MoveFile(NewPath, DstPath)
        else:
            print("This is a special file:", Path + item)

def main():

    ListArgv = sys.argv

    #if len(ListArgv) < 3:
    #    print('Sorter.py <Source Directory Path> <Destination Directory Path>')
    #    sys.exit(2)

    #for Path in ListArgv[1:]:

    #    if not os.path.exists(os.path.join(Path, '')):
    #        print('This Path:', Path, " doesn't exist.")
    #        sys.exit(2)

    ListArgv = ["Sorted.py", "D:\GPS", "D:\Test"]

    ContentEnumerator(ListArgv[1], ListArgv[2])

if __name__ == "__main__":
    main()

