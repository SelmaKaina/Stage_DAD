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


def exif_extract(directory):

    with ExifTool() as et:
        data = et.execute_json(*['-r', '-b', '-FileName', '-CreateDate', '-By-line', '-City', '-Country',
                                 '-Country-PrimaryLocationName', '-Caption-Abstract', '-Subject', '-Artist'] + [directory])
        return data






def unit_rp(directory, data, data_ir):
    descrmd = ET.Element("DescriptiveMetadata")
    for RP in data_ir:
        archiveunitgr = ET.SubElement(descrmd,"ArchiveUnit")
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
        archiveunitchild = sub_unit(directory, data, RP[0])
        if archiveunitchild is not None and archiveunitchild != "":
            archiveunitgr.append(archiveunitchild)
    return descrmd


def create_archive_unit_dir(title_dir, content):
    contentdir = ET.Element("Content")
    title_element = ET.SubElement(contentdir, "Title")
    title_element.text = title_dir
    ET.SubElement(contentdir, "DescriptionLevel").text = "RecordGrp"
    contentdir.extend(content)
    return contentdir

def sub_unit(directory, data, rp):
    archiveunit = ""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if rp in item_path:
            if os.path.isdir(item_path):
                archiveunit = ET.Element("ArchiveUnit")
                contentsub = create_archive_unit_dir(item, archiveunit)
                archiveunit.append(contentsub)
                archiveunitchild = sub_unit(item_path, data, rp)
                archiveunit.append(archiveunitchild)
            elif os.path.isfile(item_path) and "DS_Store" not in item:
                archiveunit = ET.Element("ArchiveUnit")
                file_unit = create_archive_unit_file(item, data)
                archiveunit.append(file_unit)
    return archiveunit





def create_archive_unit_file(title_file, data):
    contentit = ET.Element("Content")
    title_element = ET.SubElement(contentit, "Title")
    title_element.text = title_file
    ET.SubElement(contentit, "DescriptionLevel").text = "Item"
    for item in data:
        if item["File:FileName"] == title_file:
            if item.get("IPTC:By-line"):
                authag = ET.SubElement(contentit, "AuthorizedAgent")
                agname = ET.SubElement(authag, "FullName")
                item["IPTC:By-line"] = item["IPTC:By-line"]
                agname.text = item["IPTC:By-line"]
                ET.SubElement(authag, "Activity").text = "Photographe"
                ET.SubElement(authag, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
            else:
                if item.get("EXIF:Artist"):
                    authag = ET.SubElement(contentit, "AuthorizedAgent")
                    agname = ET.SubElement(authag, "FullName")
                    item["EXIF:Artist"] = item["EXIF:Artist"]
                    agname.text = item["EXIF:Artist"]
                    ET.SubElement(authag, "Activity").text = "Photographe"
                    ET.SubElement(authag, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
                else:
                    pass
                if item.get("XMP:CreateDate"):
                    startdateit = ET.SubElement(contentit, "StartDate")
                    createdate = item["XMP:CreateDate"]
                    match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?",
                                     createdate)
                    if match:
                        createdate = match.group(1)
                        createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                        createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                        startdateit.text = createdate
                        enddateit = ET.SubElement(contentit, "EndDate")
                        enddateit.text = createdate
                if item.get("EXIF:CreateDate"):
                    startdateit = ET.SubElement(contentit, "StartDate")
                    createdate = item["EXIF:CreateDate"]
                    match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?",
                                     createdate)
                    if match:
                        createdate = match.group(1)
                        createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                        createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                        startdateit.text = createdate
                        enddateit = ET.SubElement(contentit, "EndDate")
                        enddateit.text = createdate
                    else:
                        pass
                    if item.get("XMP:Subject"):
                        if not isinstance(item["XMP:Subject"], list):
                            tagit = ET.SubElement(contentit, "Tag")
                            tagit.text = item["XMP:Subject"]
                        else:
                            for tag in item["XMP:Subject"]:
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = tag
                    else:
                        if item.get("IPTC:Keywords"):
                            if not isinstance(item["IPTC:Keywords"], list):
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = item["IPTC:Keywords"]
                            else:
                                for tag in item["IPTC:Keywords"]:
                                    tagit = ET.SubElement(contentit, "Tag")
                                    tagit.text = tag
                        else:
                            pass
                    if item.get("XMP:Country" or "IPTC:Country-PrimaryLocationName" or "XMP:City" or "IPTC:City"):
                        cov = ET.SubElement(contentit, "Coverage")
                        if item.get("XMP:Country"):
                            spatial_pays = ET.SubElement(cov, "Spatial")
                            spatial_pays.text = item["XMP:Country"]
                        else:
                            if item.get("IPTC:Country-PrimaryLocationName"):
                                spatial_pays = ET.SubElement(cov, "Spatial")
                                spatial_pays.text = item["IPTC:Country-PrimaryLocationName"]
                            else:
                                pass
                        if item.get("XMP:City"):
                            spatial_ville = ET.SubElement(cov, "Spatial")
                            spatial_ville.text = item["XMP:City"]
                        else:
                            if item.get("IPTC:City"):
                                spatial_ville = ET.SubElement(cov, "Spatial")
                                spatial_ville.text = item["IPTC:City"]
                            else:
                                pass
                    else:
                        pass

    return contentit

def create_xml_tree(descrmd):
    root = ET.Element("ArchiveTransfer")
    comment = ET.SubElement(root, "Comment")
    comment.text = "SIP Application"
    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    ET.SubElement(root, "MessageIdentifier").text = "MessageIdentifier0"
    ET.SubElement(root, "ArchivalAgreement").text = "TEST"
    ET.SubElement(root, "CodeListVersions").text = "TEST"
    root.append(descrmd)
    return root

def indent(elem, level=0):

    indent_size = 4
    i = "\n" + level * indent_size * " "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent_size * " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i





directory = select_directory()

chemin_ir = select_csv()

data_ir = lire_ir_csv(chemin_ir)

data = exif_extract(directory)

descrmd = unit_rp(directory, data, data_ir)

xml_tree = create_xml_tree(descrmd)

indent(xml_tree)

xml_str = ET.tostring(xml_tree, encoding='unicode')
with open("test3.xml", "w") as t:
    t.write(xml_str)

