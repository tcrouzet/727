#Utilisé lors de la création

import os

source_folder= os.path.expanduser(f"~/Documents/GitHub/727/_posts/")

for filename in os.listdir(source_folder):
    if filename.lower().endswith('.md'):
        source_path = os.path.join(source_folder, filename)

        with open(source_path, 'r+') as file:
            content = file.readlines()

            if 'leaflet: true\n' in content:
                print(f"'leaflet: true' déjà présent dans {source_path}")
                continue

            # Ajouter 'leaflet: true' à l'entête
            for i, line in enumerate(content):
                if line.strip() == '---' and i != 0:  # Fin de l'entête
                    content.insert(i, 'leaflet: true\n')
                    break

            # Sauvegarder les modifications dans le fichier
            file.seek(0)
            file.writelines(content)
            #file.truncate()
            print(f"'leaflet: true' ajouté à {source_path}")