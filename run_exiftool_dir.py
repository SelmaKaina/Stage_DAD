
import tkinter as tk
from tkinter import filedialog
import os
import csv
from exiftool import ExifTool
from tqdm import tqdm

root = tk.Tk()
root.withdraw()
metadata_names = ['r', 'FileName','CreateDate', 'By-line', 'Caption-Abstract', 'Subject']

input("Bonjour ! Appuyez sur Entrée pour choisir le dossier")
dir_path = filedialog.askdirectory()
print("Répertoire choisi : ", dir_path)

with ExifTool() as et:
    data = et.execute_json(*['-r', '-FileName', '-CreateDate', '-By-line',
                                            '-Caption-Abstract', '-Subject'] + [dir_path])
    with open('metadata.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['SourceFile', 'File:FileName', 'EXIF:CreateDate', 'XMP:CreateDate',
                                                     'IPTC:By-line', 'IPTC:Caption-Abstract', 'XMP:Subject'])
        writer.writeheader()
        if data:
            for d in data:
                writer.writerow(d)
            print("L'extraction des métadonnées s'est bien déroulée.")
        else:
            print("L'extraction ou l'écriture des métadonnées a échoué.")

