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
from exiftool import ExifTool

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


def exif_extract(dir_path):
    with ExifTool() as et:
        data = et.execute_json(*['-r', '-FileName', '-CreateDate', '-By-line',
                                 '-Caption-Abstract', '-Subject'] + [dir_path])
        return data


def creer_xml(data_ir, fichiers_dossiers, data):
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
                if re.search("\\d{2}\\s" or "\\d{3}\\s", name):
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
                                for item in data:
                                    if item["File:FileName"] == name:
                                        if item.get("IPTC:By-line"):
                                            authag = ET.SubElement(content_it, "AuthorizedAgent")
                                            agname = ET.SubElement(authag, "FullName")
                                            agname.text = item["IPTC:By-line"]
                                            ET.SubElement(authag, "Activity").text = "Photographe"
                                            ET.SubElement(authag, "Mandate").text = "Photographe Elysée"
                                        else:
                                            pass
                                        if item.get("IPTC:Caption-Abstract"):
                                            description = ET.SubElement(content_it, "Description")
                                            description.text = item["IPTC:Caption-Abstract"]
                                        else:
                                            pass
                                        if item.get("XMP:CreateDate"):
                                            startdateit = ET.SubElement(content_it, "StartDate")
                                            startdateit.text = item["XMP:CreateDate"]
                                            enddateit = ET.SubElement(content_it, "EndDate")
                                            enddateit.text = item["XMP:CreateDate"]
                                        else:
                                            pass

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
    data = exif_extract(selected_directory)

    arbre_xml = creer_xml(data_ir, fichiers_dossiers, data)
    xml_str = ET.tostring(arbre_xml.getroot(), encoding='unicode')

    # Parser la chaîne de caractères XML avec minidom pour l'indenter
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml()

    # Enregistrer l'arborescence XML indentée dans un fichier
    with open("test.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml_str)


if __name__ == "__main__":
    main()


