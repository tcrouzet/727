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

source_folder= os.path.expanduser(f"~/Documents/GitHub/727/images/")
images_data = []
unique_images = set()

# Parcours du dossier source pour copier les images
for root, dirs, files in os.walk(source_folder):
    for filename in files:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            source_path = os.path.join(root, filename)
            
            exif_data = get_exif_data(source_path)
            geotags = get_geotagging(exif_data)
            exif_date = exif_data.get('DateTime')

            coords = ("", "")
            if geotags is not None:
                coords = get_decimal_coords(geotags)
            else:
                continue

            if(exif_date):
                source_time = datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
                date_fr = source_time.strftime('%d/%m/%Y')
                subdir = source_time.strftime('%Y-%m-%d')
            else:
                continue

            unique_key = (filename, exif_date, coords[0], coords[1])

            if unique_key not in unique_images:
                unique_images.add(unique_key)
  
                relative_path = os.path.relpath(root, source_folder)
                images_data.append({
                    "date": source_time,
                    "filename": os.path.join(relative_path, filename),
                    "latitude": coords[0],
                    "longitude": coords[1],
                    "alt": date_fr
                })

                print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")

images_data.sort(key=lambda x: x['date'], reverse=True)

yml_content = []
for data in images_data:
    yml_content.append({
        "image": data['filename'],
        "date": data['date'].strftime('%Y-%m-%d %H:%M:%S'),
        "lat": data['latitude'],
        "lon": data['longitude'],
        "alt": data['alt']
    })

yml_file = os.path.expanduser("~/Documents/GitHub/727/_data/diaporama.yml")
with open(yml_file, "w") as file:
    yaml.dump(yml_content, file, default_flow_style=False)
