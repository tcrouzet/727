#Met à jour images.yml, use once ou if change
import os
import yaml
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = {}
    
    if hasattr(image, '_getexif'):
        exif_info = image._getexif()
        if exif_info is not None:
            for tag, value in exif_info.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value

    return exif_data

def get_geotagging(exif_data):
    if 'GPSInfo' in exif_data:
        gps_info = exif_data['GPSInfo']
        geotagging = {}
        for tag in gps_info.keys():
            decoded = GPSTAGS.get(tag, tag)
            geotagging[decoded] = gps_info[tag]

        return geotagging
    return None

def convert_to_degrees(value):
    """ Convertit une valeur DMS EXIF en degrés décimaux """
    # Convertit chaque valeur IFDRational en un nombre décimal
    d, m, s = value
    return round(float(d) + float(m) / 60 + float(s) / 3600,5)

def get_decimal_coords(geotags):
    lat = convert_to_degrees(geotags['GPSLatitude'])
    lon = convert_to_degrees(geotags['GPSLongitude'])

    if geotags['GPSLatitudeRef'] != 'N':
        lat = -lat
    if geotags['GPSLongitudeRef'] != 'E':
        lon = -lon

    return (lat, lon)

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file)

yml_file = "~/Documents/GitHub/727/_data/images.yml"
yml_file = os.path.expanduser(yml_file)
yml_data = read_yaml(yml_file)

images_folder = "~/Documents/GitHub/727/images/"
images_folder = os.path.expanduser(images_folder)

for key in yml_data:

    temp_list = []

    for item in yml_data[key]:

        image_path = key+"/"+item['image']
        source = os.path.join(images_folder, image_path)

        exif_data = get_exif_data(source)
        geotags = get_geotagging(exif_data)
        exif_date = exif_data.get('DateTime')

        coords = ("", "")
        if geotags is not None:
            coords = get_decimal_coords(geotags)
            item['lat']=coords[0]
            item['lon']=coords[1]
        else:
            continue

        if(exif_date):
            item['date']=exif_date
        else:
            continue

        temp_list.append(item)

    yml_data[key] = temp_list

print(yml_data)
#write_yaml(yml_file, yml_data)
        