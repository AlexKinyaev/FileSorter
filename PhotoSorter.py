
import sys
import os
import time
import shutil 
import signal
from geopy.geocoders import Nominatim
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
#import datetime

FileFilter = [".png", ".jpg", ".bmp", ".jpeg", ".mpg", ".avi", ".mov", ".3gp", ".mkv"]


def signal_handler(sig, frame):
    print('You have cancelled the process.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def getExifInfo(file):
    
    ExifInfo = {}
    FullExif = None

    try:
        image = Image.open(file)
        FullExif = image._getexif()
    except:
        return ExifInfo

    if FullExif:
        for tag, value in FullExif.items():

            Decoded = TAGS.get(tag, tag)
            
            if Decoded == "GPSInfo":
                gps_data = {}
                for gpst in value:
                    sub_decoded = GPSTAGS.get(gpst, gpst)
                    gps_data[sub_decoded] = value[gpst]

                ExifInfo[Decoded] = gps_data
            elif Decoded == "DateTimeOriginal":
                ExifInfo[Decoded] = value

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

    LocationName = None

    try:

        gps_latitude = Coordinates["GPSLatitude"]
        gps_latitude_ref = Coordinates["GPSLatitudeRef"]
        gps_longitude = Coordinates["GPSLongitude"]
        gps_longitude_ref = Coordinates["GPSLongitudeRef"]

    except:
        return LocationName

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:

        lat = ConvertToDegress(gps_latitude)
        if gps_latitude_ref != "N":                     
            lat = 0 - lat

        lng = ConvertToDegress(gps_longitude)
        if gps_longitude_ref != "E":
            lng = 0 - lng

        geolocator = Nominatim()
        lat_lng = str(lat) + ", " + str(lng)
        location = geolocator.reverse(lat_lng)

        address = []

        try:
            address = location.raw["address"]
        except:
            return LocationName

        if "city" in address:
            LocationName = address["city"] + ' '
        elif "state" in address:
            LocationName = address["state"] + ' '

        if "road" in address:
            LocationName += address["road"] + ' '
        elif "county" in address:
            LocationName += address["county"] + ' '

        if "suburb" in address:
            LocationName += address["suburb"]
        elif "country" in address:
            LocationName += address["country"]

        #print(address)
        print(LocationName)

    return LocationName


def PrepareFolder(File, DstPath):

    DateList = None
    FolderName = None

    Info = getExifInfo(File)

    if len(Info):
        if "GPSInfo" in Info:
            FolderName = GetLocationName(Info["GPSInfo"])

    if not FolderName:
        FolderName = time.strftime("%d", time.gmtime(os.path.getmtime(File)))

    DateList = [time.strftime("%Y", time.gmtime(os.path.getmtime(File))), 
                time.strftime("%B", time.gmtime(os.path.getmtime(File))), 
                FolderName]

    for Date in DateList:

        DstPath = os.path.join(DstPath, Date)

        if not os.path.exists(DstPath):
            os.mkdir(DstPath)

    return DstPath


def CopyFile(File, DstPath):

    DesFolder = PrepareFolder(File, DstPath)

    try:
        shutil.copy2(File, DesFolder)
        print(File, ' -> ',  DesFolder)
    except:
        print(File, ' is exist in: ',  DesFolder)

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
                CopyFile(NewPath, DstPath)
        else:
            print("This is a special file:", Path + item)

def main():

    ListArgv = sys.argv

    if len(ListArgv) < 3:
        print('Sorter.py <Source Directory Path> <Destination Directory Path>')
        sys.exit(2)

    for Path in ListArgv[1:]:

        if not os.path.exists(os.path.join(Path, '')):
            print('This Path:', Path, " doesn't exist.")
            sys.exit(2)

    #ListArgv = ["Sorted.py", "D:\PhotoGPS", "D:\Test"]

    ContentEnumerator(ListArgv[1], ListArgv[2])

if __name__ == "__main__":
    main()

