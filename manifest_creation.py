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

# -*- coding: utf-8 -*-

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
    with open(csv_path, newline='') as csvfile:
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
        data = et.execute_json(*['-r', '-b', '-FileName', '-CreateDate', '-By-line',
                                 '-Caption-Abstract', '-Subject', '-Artist'] + [dir_path])
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
        dtd = datetime.strptime(RP[2], "%d.%m.%Y")
        dtd = dtd.strftime("%Y-%m-%dT%H:%M:%S")
        startdate.text = dtd
        enddate = ET.SubElement(content, "EndDate")
        dtf = datetime.strptime(RP[3], "%d.%m.%Y")
        dtf = dtf.strftime("%Y-%m-%dT%H:%M:%S")
        enddate.text = dtf
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
                                            item["IPTC:By-line"] = item["IPTC:By-line"]
                                            agname.text = item["IPTC:By-line"]
                                            ET.SubElement(authag, "Activity").text = "Photographe"
                                            ET.SubElement(authag, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
                                        else:
                                            if item.get("EXIF:Artist"):
                                                authag = ET.SubElement(content_it, "AuthorizedAgent")
                                                agname = ET.SubElement(authag, "FullName")
                                                item["EXIF:Artist"] = item["EXIF:Artist"]
                                                agname.text = item["EXIF:Artist"]
                                                ET.SubElement(authag, "Activity").text = "Photographe"
                                                ET.SubElement(authag, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
                                            else:
                                                pass
                                        if item.get("IPTC:Caption-Abstract"):
                                            description = ET.SubElement(content_it, "Description")
                                            description.text = item["IPTC:Caption-Abstract"]
                                        else:
                                            pass
                                        if item.get("XMP:CreateDate"):
                                            startdateit = ET.SubElement(content_it, "StartDate")
                                            createdate = item["XMP:CreateDate"]
                                            match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?", createdate)
                                            if match:
                                                createdate = match.group(1)
                                                createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                                                createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                                                startdateit.text = createdate
                                                enddateit = ET.SubElement(content_it, "EndDate")
                                                enddateit.text = createdate
                                        if item.get("EXIF:CreateDate"):
                                            startdateit = ET.SubElement(content_it, "StartDate")
                                            createdate = item["EXIF:CreateDate"]
                                            match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?", createdate)
                                            if match:
                                                createdate = match.group(1)
                                                createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                                                createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                                                startdateit.text = createdate
                                                enddateit = ET.SubElement(content_it, "EndDate")
                                                enddateit.text = createdate
                                            else:
                                                pass
                                        if item.get("XMP:Subject"):
                                            if not isinstance(item["XMP:Subject"], list):
                                                tagit = ET.SubElement(content_it, "Tag")
                                                tagit.text = tag
                                            else:
                                                for tag in item["XMP:Subject"]:
                                                    tagit = ET.SubElement(content_it, "Tag")
                                                    tagit.text = tag
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
    xml_str = ET.tostring(arbre_xml.getroot())

    # Parser la chaîne de caractères XML avec minidom pour l'indenter
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml()

    # Enregistrer l'arborescence XML indentée dans un fichier
    with open("test.xml", "w") as t:
        t.write(pretty_xml_str)


if __name__ == "__main__":
    main()


