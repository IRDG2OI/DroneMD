import exifread
import re
# import glob
import os
import pandas as pd
import base64
import xmltodict as x2d

# Return image list
def getImagelist(folder):
    """
    Number of images
    
    Parameters
    ----------
    folder: str
                Folder where some images are available
    """ 
    images_list = []
    ###########################################
    ## Old method to parse only DCIM folder
    ###########################################
    # types = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG")
    # for t in types:
    #     images_list.extend(glob.glob(os.path.join(folder, t)))
    ###########################################
    ## New method to parse DCIM subfolder
    ###########################################
    types = (".jpg", ".jpeg", ".JPG", ".JPEG")
    images_list = [os.path.join(root, name)
                 for root, dirs, files in os.walk(folder)
                 for name in files
                 if name.endswith(types)]
    
    return images_list

def nbImages(il):
    """
    Number of images
    
    Parameters
    ----------
    il: list
                Images list
    """ 
    # print(len(getImagelist(folder)), "images found")
    return len(il)

# From https://github.com/OpenDroneMap/ODM/blob/master/opendm/photo.py
def get_xmp(file):
    """
    Extract xmp values
    
    Parameters
    ----------
    file: str
                image name
    """ 
    img_bytes = file.read()
    xmp_start = img_bytes.find(b'<x:xmpmeta')
    xmp_end = img_bytes.find(b'</x:xmpmeta')

    if xmp_start < xmp_end:
        xmp_str = img_bytes[xmp_start:xmp_end + 12].decode('utf8')
        try:
            xdict = x2d.parse(xmp_str)
        except ExpatError as e:
            from bs4 import BeautifulSoup
            xmp_str = str(BeautifulSoup(xmp_str, 'xml'))
            xdict = x2d.parse(xmp_str)
        xdict = xdict.get('x:xmpmeta', {})
        xdict = xdict.get('rdf:RDF', {})
        xdict = xdict.get('rdf:Description', {})
        if isinstance(xdict, list):
            return xdict
        else:
            return [xdict]
    else:
        return []

def images_coords(il):
    """
    Extract images coordinates and complete exifs of images
    
    Parameters
    ----------
    il: list
                Images list
    """ 
    df = {}
    df = pd.DataFrame(columns=('FileName', 'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'FlightRollDegree', 'FlightPitchDegree', 'FlightYawDegree', 'GimbalRollDegree', 'GimbalPitchDegree', 'GimbalYawDegree', 'ImageWidth', 'ImageLength', 'BitsPerSample', 'ImageDescription', 'Make', 'Model', 'Orientation', 'SamplesPerPixel', 'XResolution', 'YResolution', 'ResolutionUnit', 'Software', 'DateTime', 'YCbCrPositioning', 'ExifOffset', 'GPSVersionID',  'ThumbnailImageWidth', 'ThumbnailImageLength', 'ThumbnailCompression', 'ThumbnailXResolution', 'ThumbnailYResolution', 'ThumbnailResolutionUnit', 'ThumbnailJPEGInterchangeFormat', 'ThumbnailJPEGInterchangeFormatLength', 'ExposureTime', 'FNumber', 'ExposureProgram', 'ISOSpeedRatings', 'ExifVersion', 'DateTimeOriginal', 'DateTimeDigitized', 'ComponentsConfiguration', 'ExposureBiasValue', 'MaxApertureValue', 'MeteringMode', 'LightSource', 'Flash', 'FocalLength', 'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ExifImageLength', 'FileSource', 'SceneType', 'ExposureMode', 'WhiteBalance', 'DigitalZoomRatio', 'FocalLengthIn35mmFilm', 'SceneCaptureType', 'GainControl', 'Contrast', 'Saturation', 'Sharpness', 'DeviceSettingDescription', 'BodySerialNumber', 'ThumbnailImage'))
    for i in il:
        f = open(i, 'rb')
        tags = exifread.process_file(f, details=True)
        f.seek(0)
        xmp = {}
        xmp = get_xmp(f)
        if 'GPS GPSLatitude' in tags:
            # print("Extract GPS tags for: " + i)
            if 'DJI' in xmp[0].values():
                gpslatdd = xmp[0]['@drone-dji:GpsLatitude']
                gpslondd = xmp[0]['@drone-dji:GpsLongitude']
                # gpsalt = xmp[0]['@drone-dji:AbsoluteAltitude']
                gpsalt = xmp[0]['@drone-dji:RelativeAltitude']
                flightroll = xmp[0]['@drone-dji:FlightRollDegree']
                flightpitch = xmp[0]['@drone-dji:FlightPitchDegree']
                flightyaw = xmp[0]['@drone-dji:FlightYawDegree']
                cameraroll = xmp[0]['@drone-dji:GimbalRollDegree']
                camerapitch = xmp[0]['@drone-dji:GimbalPitchDegree']
                camerayaw = xmp[0]['@drone-dji:GimbalYawDegree']
                
            else:
                gpslatdd = convertMetaIncoord(gpslatdms, tags["GPS GPSLatitudeRef"])
                gpslondd = convertMetaIncoord(gpslondms, tags["GPS GPSLongitudeRef"])
                gpslatdms = tags['GPS GPSLatitude'].printable
                gpslondms = tags['GPS GPSLongitude'].printable
                gpsalt = tags['GPS GPSAltitude'].printable

        else:
            print('WARN: No GPS tags in:' +i)
            pass
        
        if "Image ImageWidth" and "Image ImageLength" in tags:
            ImageWidth = tags['Image ImageWidth'].printable
            ImageLength = tags['Image ImageLength'].printable
            BitsPerSample = tags['Image BitsPerSample'].printable
            ImageDescription = tags['Image ImageDescription'].printable
            Make = tags['Image Make'].printable
            Model = tags['Image Model'].printable
            Orientation = tags['Image Orientation'].printable
            SamplesPerPixel = tags['Image SamplesPerPixel'].printable
            XResolution = tags['Image XResolution'].printable
            YResolution = tags['Image YResolution'].printable
            ResolutionUnit = tags['Image ResolutionUnit'].printable
            Software = tags['Image Software'].printable
            DateTime = tags['Image DateTime'].printable
            YCbCrPositioning = tags['Image YCbCrPositioning'].printable
            ExifOffset = tags['Image ExifOffset'].printable
            GPSVersionID = tags['GPS GPSVersionID'].printable
            ThumbnailImageWidth = tags['Thumbnail ImageWidth'].printable
            ThumbnailImageLength = tags['Thumbnail ImageLength'].printable
            ThumbnailCompression = tags['Thumbnail Compression'].printable
            ThumbnailXResolution = tags['Thumbnail XResolution'].printable
            ThumbnailYResolution = tags['Thumbnail YResolution'].printable
            ThumbnailResolutionUnit = tags['Thumbnail ResolutionUnit'].printable
            ThumbnailJPEGInterchangeFormat = tags['Thumbnail JPEGInterchangeFormat'].printable
            ThumbnailJPEGInterchangeFormatLength = tags['Thumbnail JPEGInterchangeFormatLength'].printable
            ExposureTime = tags['EXIF ExposureTime'].printable
            FNumber = tags['EXIF FNumber'].values[0]
            ExposureProgram = tags['EXIF ExposureProgram'].printable
            ISOSpeedRatings = tags['EXIF ISOSpeedRatings'].printable
            ExifVersion = tags['EXIF ExifVersion'].printable
            DateTimeOriginal = tags['EXIF DateTimeOriginal'].printable
            DateTimeDigitized = tags['EXIF DateTimeDigitized'].printable
            ComponentsConfiguration = tags['EXIF ComponentsConfiguration'].printable
            ExposureBiasValue = tags['EXIF ExposureBiasValue'].values[0]
            MaxApertureValue = tags['EXIF MaxApertureValue'].values[0]
            MeteringMode = tags['EXIF MeteringMode'].printable
            LightSource = tags['EXIF LightSource'].printable
            Flash = tags['EXIF Flash'].printable
            FocalLength = tags['EXIF FocalLength'].values[0]
            FlashPixVersion = tags['EXIF FlashPixVersion'].printable
            ColorSpace = tags['EXIF ColorSpace'].printable
            ExifImageWidth = tags['EXIF ExifImageWidth'].printable
            ExifImageLength = tags['EXIF ExifImageLength'].printable
            FileSource = tags['EXIF FileSource'].printable
            SceneType = tags['EXIF SceneType'].printable
            ExposureMode = tags['EXIF ExposureMode'].printable
            WhiteBalance = tags['EXIF WhiteBalance'].printable
            DigitalZoomRatio = tags['EXIF DigitalZoomRatio'].printable
            FocalLengthIn35mmFilm = tags['EXIF FocalLengthIn35mmFilm'].printable
            SceneCaptureType = tags['EXIF SceneCaptureType'].printable
            GainControl = tags['EXIF GainControl'].printable
            Contrast = tags['EXIF Contrast'].printable
            Saturation = tags['EXIF Saturation'].printable
            Sharpness = tags['EXIF Sharpness'].printable
            DeviceSettingDescription = tags['EXIF DeviceSettingDescription'].printable
            BodySerialNumber = tags['EXIF BodySerialNumber'].printable

            tb = "base64:" + base64.b64encode(tags['JPEGThumbnail']).decode()
        
        filename = os.path.split(i)[-1]        
        
        df.loc[i]=[filename, float(gpslatdd), float(gpslondd), float(gpsalt), float(flightroll), float(flightpitch), float(flightyaw), float(cameraroll), float(camerapitch), float(camerayaw), ImageWidth, ImageLength, BitsPerSample, ImageDescription, Make, Model, Orientation, SamplesPerPixel, XResolution, YResolution, ResolutionUnit, Software, DateTime, YCbCrPositioning, ExifOffset, GPSVersionID, ThumbnailImageWidth, ThumbnailImageLength, ThumbnailCompression, ThumbnailXResolution, ThumbnailYResolution, ThumbnailResolutionUnit, ThumbnailJPEGInterchangeFormat, ThumbnailJPEGInterchangeFormatLength, ExposureTime, float(FNumber), ExposureProgram, ISOSpeedRatings, ExifVersion, DateTimeOriginal, DateTimeDigitized, ComponentsConfiguration, float(ExposureBiasValue), float(MaxApertureValue), MeteringMode, LightSource, Flash, float(FocalLength), FlashPixVersion, ColorSpace, ExifImageWidth, ExifImageLength, FileSource, SceneType, ExposureMode, WhiteBalance, DigitalZoomRatio, float(FocalLengthIn35mmFilm), SceneCaptureType, GainControl, Contrast, Saturation, Sharpness, DeviceSettingDescription, BodySerialNumber, tb]

    return df


def bbox(df):
    """
    Return bounding box
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Images list dataframe
    """ 
    min_x = df.min()['GPSLongitude']
    min_y = df.min()['GPSLatitude']
    max_x = df.max()['GPSLongitude']
    max_y = df.max()['GPSLatitude']
    return min_x, min_y, max_x, max_y

def center_bbox(coords):
    """
    Compute center of bounding box
    
    Parameters
    ----------
    coords: list
                Four coordinates generated from bbox function
    """ 
    x = (coords[0]+coords[2])/2
    y = (coords[1]+coords[3])/2
    return x, y

def altimg(df):
    """
    Extract flight height
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Images list dataframe
    """ 
    return df.median(numeric_only=True)['GPSAltitude']

def datebe(df):
    """
    Date begin - end
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Images list dataframe
    """ 
    return df.min()['DateTime'], df.max()['DateTime']

def common_tags(il):
    """
    Extract common tags of a dataset to fill survey info
    
    Parameters
    ----------
    il: list
                Images list
    """ 
    file = il[round(len(il)/2)]
    print(file)
    f = open(file, 'rb') 
    tags = exifread.process_file(f, details=False)
    common_elements = {}
    xmp = {}
    common_elements.update({
    "Make": tags['Image Make'].printable,
    "Model": tags['Image Model'].printable,
    "Width": tags['Image ImageWidth'].printable,
    "Height": tags['Image ImageLength'].printable,
    "Focal": tags['EXIF FocalLengthIn35mmFilm'].printable,
    "WhiteBalance": tags['EXIF WhiteBalance'].printable,
    "ExposureMode": tags['EXIF ExposureMode'].printable,
    "ColoSpace": tags['EXIF ColorSpace'].printable,
    "EV": float(tags['EXIF ExposureBiasValue'].values[0]),
    "MeteringMode": tags['EXIF MeteringMode'].printable}
                            )
    f.seek(0)
    xmp = get_xmp(f)
    common_elements["Camera Pitch"] = xmp[0]['@drone-dji:GimbalPitchDegree']
    return common_elements

def convertMetaIncoord(gps_lat_or_lon, quadrant):
    """
    Convert Degrees Minutes seconds to Decimal degrees
    
    Parameters
    ----------
    gps_lat_or_lon: str
                Degrees Minutes Seconds from exif
    quadrant: str
                Claudius Ptolemy. N, S, W or E
    """ 
    coord = {} 
    regexHour = re.compile(r"\[(\d+)\,")
    regexMinute = re.compile(r"\, (\d+)\,")
    regexSecond = re.compile(r"\,\ (\d+)\/")
    regexSecondDivisor = re.compile(r"\/(\d+)\]")
    coord["hour"] = re.findall(regexHour, str(gps_lat_or_lon))[0] 
    coord["minute"] = re.findall(regexMinute, str(gps_lat_or_lon))[0] 
    if "/" in str(gps_lat_or_lon):
        coord["second"] = re.findall(regexSecond, str(gps_lat_or_lon))[0]
        coord["secondDivisor"] = re.findall(regexSecondDivisor, str(gps_lat_or_lon))[0] 
    else:
        coord["second"] = gps_lat_or_lon.split(",")[2].strip("]")
        coord["secondDivisor"] = "1"
    coord["total"] = float(int(coord["hour"]) + ( (int(coord["minute"]) * 60) + (int(coord["second"])) / int(coord["secondDivisor"])) / 3600) 
    if str(quadrant) == "S" or str(quadrant) == "W": 
        coord["total"] = coord["total"] * -1 
        return coord["total"]
    else:
        return coord["total"]

# Define a function to display the image
def display_image(df):
    """
    Generate html code to wath base64 image
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Dataframe with base64 image
    """    
    img_src = f"data:image/jpeg;base64, {df}"
    # return HTML(
    img_html = f'<img src="{img_src}" class="blog-image"/>' + " "
    return img_html


