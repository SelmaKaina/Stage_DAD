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
import re
import xml.dom.minidom

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
    with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data_ir.append(row)
    return data_ir


def parcourir_arborescence(dir_path):
    # Liste pour stocker les noms de fichiers et de dossiers avec leur emplacement
    fichiers_dossiers = []
    # Parcourir les répertoires et fichiers avec os.walk
    for root, directories, files in os.walk(dir_path):
        for dossier in directories:
            # Ajouter chaque fichier avec son emplacement à la liste
            fichiers_dossiers.append((root, dossier))
        for file in files:
            # Ajouter chaque fichier avec son emplacement à la liste
            fichiers_dossiers.append((root, file))
    return fichiers_dossiers


def creer_xml(data_ir, fichiers_dossiers):
    root = ET.Element("ArchiveTransfer")
    comment = ET.SubElement(root, "Comment")
    comment.text = "SIP Application"

    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    ET.SubElement(root, "MessageIdentifier").text = "MessageIdentifier0"
    ET.SubElement(root, "ArchivalAgreement").text = "TEST"
    ET.SubElement(root, "CodeListVersions").text = "TEST"
    descrmd = ET.SubElement(root, "DescriptiveMetadata")

    for RP in data_ir:
        archiveunitgr = ET.SubElement(descrmd, "ArchiveUnit")
        content = ET.SubElement(archiveunitgr, "Content")
        ET.SubElement(content, "DescriptionLevel").text = "RecordGrp"
        title = ET.SubElement(content, "Title")
        title.text = RP[1]
        numrp = ET.SubElement(content, "OriginatingAgencyArchiveUnitIdentifier")
        numrp.text = RP[0]
        origag = ET.SubElement(content, "OriginatingAgency")
        ET.SubElement(origag, "Identifier").text = "TEST"
        subag = ET.SubElement(content, "SubmissionAgency")
        ET.SubElement(subag, "Identifier").text = "TEST"
        startdate = ET.SubElement(content, "StartDate")
        startdate.text = RP[2]
        enddate = ET.SubElement(content, "EndDate")
        enddate.text = RP[3]
        for path, name in fichiers_dossiers:
            if RP[0] in path:
                if re.search("\\d{2}\\s", name):
                    name_sec = name
                    archiveunitsec = ET.SubElement(archiveunitgr, "ArchiveUnit")
                    content_sec = ET.SubElement(archiveunitsec, "Content")
                    title_sec = ET.SubElement(content_sec, "Title")
                    title_sec.text = name_sec
                    for path, name in fichiers_dossiers:
                        if name_sec in path:
                            if name.startswith(RP[0]):
                                archiveunitit = ET.SubElement(archiveunitsec, "ArchiveUnit")
                                content_it = ET.SubElement(archiveunitit, "Content")
                                ET.SubElement(content_it, "DescriptionLevel").text = "Item"
                                title_it = ET.SubElement(content_it, "Title")
                                title_it.text = name
                                origag = ET.SubElement(content_it, "OriginatingAgency")
                                ET.SubElement(origag, "Identifier").text = "TEST"
                                subag = ET.SubElement(content_it, "SubmissionAgency")
                                ET.SubElement(subag, "Identifier").text = "TEST"

    # Créer et retourner un objet ElementTree avec l'élément racine
    return ET.ElementTree(root)


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    selected_csv = select_csv()
    print("Fichier sélectionné :", selected_csv)
    data_ir = lire_ir_csv(selected_csv)

    selected_directory = select_directory()
    print("Dossier sélectionné :", selected_directory)
    fichiers_dossiers = parcourir_arborescence(selected_directory)

    arbre_xml = creer_xml(data_ir, fichiers_dossiers)
    xml_str = ET.tostring(arbre_xml.getroot(), encoding='unicode')

    # Parser la chaîne de caractères XML avec minidom pour l'indenter
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml()

    # Enregistrer l'arborescence XML indentée dans un fichier
    with open("test.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml_str)


if __name__ == "__main__":
    main()


