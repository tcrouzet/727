import os
import re
import shutil
import yaml


page_name="727"

file_path = '~/Documents/GitHub/727/python/webpage.html'
file_path = os.path.expanduser(file_path)

source_folder = "~/Documents/tcrouzet/images_tc/"
source_folder = os.path.expanduser(source_folder)

target_folder = "~/Documents/GitHub/727/images/"+page_name+"/"
target_folder = os.path.expanduser(target_folder)

yml_file = "~/Documents/GitHub/727/_data/images.yml"
yml_file = os.path.expanduser(yml_file)


def copy_image_with_unique_name(source_dir, target_dir, filename):

    new_filename = filename.split('/')[-1]

    source = os.path.join(source_dir, filename.replace('/', os.sep))
    target = os.path.join(target_dir, new_filename)


    # If the file already exists, append a number to its name
    count = 1
    while os.path.exists(target):
        name, ext = os.path.splitext(new_filename)
        target = os.path.join(target_dir, f"{name}_{count}{ext}")
        count += 1

    # Copy file to the new target path
    shutil.copy(source, target)
    print(source, target)

    return True


# Lecture du fichier HTML
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

pattern = r'<img[^>]*src="http://localhost:8888/images_tc//(\d{4}/\d{2}/[^"]+)-\d+x\d+\.(jpeg|jpg|png)"[^>]*alt="([^"]*)"'
extracted_data = re.findall(pattern, html_content)
images = [{"filename": f"{path}.{ext}", "alt": alt} for path, ext, alt in extracted_data]
unique_images = {img['filename']: img for img in images}.values()
unique_images = list(unique_images)
#print(unique_images)
#exit()

# Assurer la création du dossier cible
os.makedirs(target_folder, exist_ok=True)

# Copier les images et préparer les données YML
yml_data = {page_name: []}

for img in images:
    copy_image_with_unique_name(source_folder, target_folder, img["filename"])

    # Ajouter les informations dans le dictionnaire pour le fichier YML
    new_filename = img["filename"].split('/')[-1]

    alt_text = img['alt'].strip('"')
    #alt_text = f"\"{alt_text}\""
    #print(alt_text)
    #alt_text = f"\"{alt_text}\""

    yml_data[page_name].append({"image": new_filename, "alt": alt_text})

# Écriture des données dans le fichier YML
with open(yml_file, "a", encoding='utf-8') as file:
    yml_string = yaml.dump(yml_data, allow_unicode=True)
    file.write(yml_string)