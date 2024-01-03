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

os.system('clear')

source_folder = os.path.expanduser("~/Documents/GitHub/727/images/posts/")
posts_folder = os.path.expanduser(f"~/Documents/GitHub/727/_posts/")
yml_file = os.path.expanduser("~/Documents/GitHub/727/_data/posts.yml")

count_newpost = 0

yml_data = {}

# Parcours du dossier source pour copier les images
for root, dirs, files in os.walk(source_folder):
    for filename in files:

        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            continue

        filepath = os.path.join(root, filename)
        subdir = os.path.basename(root)

        date_obj = datetime.strptime(subdir, "%Y-%m-%d")
        date_fr = date_obj.strftime("%d/%m/%Y")


        #print(subdir)  # Affiche le chemin complet du fichier
        #break
 
        exif_data = get_exif_data(filepath)
        geotags = get_geotagging(exif_data)
        exif_date = exif_data.get('DateTime')

        coords = ("", "")
        if geotags is not None:
            coords = get_decimal_coords(geotags)

        #print(exif_data['DateTime'])
        #print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")

        if subdir not in yml_data:
            yml_data[subdir] = []

        lat, lon = coords
        yml_data[subdir].append({"image": filename, "lat": lat, "lon": lon})

        markdown_file =  os.path.join(posts_folder, f"{subdir}-reco.md")
        if not os.path.exists(markdown_file):
            count_newpost += 1
            markdown=f"""---
layout: page
title: "Reco du {date_fr}"
permalink: /posts/{subdir}/
---
{{% include slideshow.html %}}"""
            with open(markdown_file, 'w') as file:
                file.write(markdown)
        

with open(yml_file, "w") as file:
    yaml.dump(yml_data, file, default_flow_style=False)

print("New posts",count_newpost)
