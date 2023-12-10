# pip install Pillow


import os
import shutil
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

source_folder = os.path.expanduser("~/Desktop/VracBureau/VTT/g727photos")
target_folder = os.path.expanduser(f"~/Documents/GitHub/727/images/posts/")
yml_file = os.path.expanduser("~/Documents/GitHub/727/_data/posts.yml")
posts_folder = os.path.expanduser(f"~/Documents/GitHub/727/posts/")

try:
    with open(yml_file, 'r') as file:
        yml_data = yaml.safe_load(file) or {}
except FileNotFoundError:
    yml_data = {}

# Parcours du dossier source pour copier les images
for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
 
        source_path = os.path.join(source_folder, filename)

        exif_data = get_exif_data(source_path)
        geotags = get_geotagging(exif_data)
        exif_date = exif_data.get('DateTime')

        coords = ("", "")
        if geotags is not None:
            coords = get_decimal_coords(geotags)

        if(exif_date):
            subdir = exif_date.split(' ')[0].replace(':', '')
            date_object = datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
            date_fr = date_object.strftime('%d/%m/%Y')
        else:
            source_time = os.path.getmtime(source_path)
            subdir = datetime.fromtimestamp(source_time).strftime('%Y%m%d')
            date_fr = datetime.fromtimestamp(source_time).strftime('%d/%m/%Y')

        print(exif_data['DateTime'])
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")

        target_path = os.path.join(target_folder, subdir, filename)

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy(source_path, target_path)

        if subdir not in yml_data:
            yml_data[subdir] = []

        lat, lon = coords
        yml_data[subdir].append({"image": filename, "lat": lat, "lon": lon})

        markdown_file =  os.path.join(posts_folder, f"{subdir}.md")
        if not os.path.exists(markdown_file):
            markdown=f"""---
layout: page
date: '{subdir}'
title: "Reco du {date_fr}"
permalink: /posts/{subdir}/
---
{{% include slideshow.html %}}"""
            with open(markdown_file, 'w') as file:
                file.write(markdown)
        

with open(yml_file, "w") as file:
    yaml.dump(yml_data, file, default_flow_style=False)
