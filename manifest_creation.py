import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import json
import csv
from time import sleep
from tqdm import tqdm
from xml.dom import minidom
import xml.etree.ElementTree as ET
from datetime import datetime

date_ajd = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")


def select_directory():
    input("Bonjour ! Appuyez sur Entrée pour choisir un dossier.")
    dir_path = filedialog.askdirectory()
    return dir_path


def select_csv():
    input("Choisir un fichier csv.")
    csv_path = filedialog.askopenfilename()
    return csv_path


def lire_ir_csv(csv_path):
    data_ir = []
    with open("20180419_INDEX_Cindoc.csv", newline='', encoding='iso-8859-1') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data_ir.append(row)
    return data_ir



def parcourir_arborescence(dir_path):
    # Listes pour stocker les noms de fichiers et de dossiers
    fichiers = []
    dossiers = []
    # Parcourir les répertoires et fichiers avec os.walk
    for root, directories, files in os.walk(dir_path):
        for dossier in directories:
            dossiers.append(dossier)  # Ajouter le nom du dossier à la liste
        for fichier in files:
            fichiers.append(fichier)  # Ajouter le nom du fichier à la liste


def creer_xml(data_ir):
    root = ET.Element("ArchiveTransfer")
    comment = ET.SubElement(root, "Comment")
    comment.text = "SIP Application"

    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    ET.SubElement(root, "MessageIdentifier", name="MessageIdentifier").text = "MessageIdentifier0"
    ET.SubElement(root, "ArchivalAgreement", name="ArchivalAgreement").text = "TEST"
    ET.SubElement(root, "CodeListVersions", name="CodeListVersions").text = "TEST"
    descrmd = ET.SubElement(root, "DescriptiveMetadata", name="DescriptiveMetadata")

    for RP in data_ir:
        ET.SubElement(descrmd, "ArchiveUnit", name="ArchiveUnit")
        content = ET.SubElement(descrmd, "Content", name="Content")
        ET.SubElement(content, "DescriptionLevel", name="DescriptionLevel").text = "RecordGrp"
        title = ET.SubElement(content, "Title", name="Title")
        title.text = RP[1]
        startdate = ET.SubElement(content, "StartDate", name="StartDate")
        startdate.text = RP[2]
        enddate = ET.SubElement(content, "EndDate", name="EndDate")
        enddate.text = RP[3]

    # Créer et retourner un objet ElementTree avec l'élément racine
    return ET.ElementTree(root)


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    selected_csv = select_csv()
    print("Fichier sélectionné :", selected_csv)
    data_ir = lire_ir_csv(selected_csv)
    arbre_xml = creer_xml(data_ir)
    ET.indent(arbre_xml, space="\t", level=0)

    # Enregistrer l'arborescence XML dans un fichier

    arbre_xml.write("test.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()


