import os
from datetime import datetime
import xml.etree.ElementTree as ET
from tkinter import filedialog
import csv
from exiftool import ExifTool
import re

# -*- coding: utf-8 -*-

date_ajd = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")




"""
IMPORT DE L'ARBORESCENCE / IMPORT DE L'IR / LECTURE DE L'IR / EXTRACTION DES METADONNEES INTERNES
"""


def select_directory():
    #input("Bonjour ! Appuyez sur Entrée pour choisir un dossier.")
    dir_path = filedialog.askdirectory()
    return dir_path


def select_csv():
    #input("Choisir un fichier csv.")
    csv_path = filedialog.askopenfilename()
    return csv_path


def lire_ir_csv(csv_path):
    data_ir = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data_ir.append(row)
    return data_ir


def exif_extract(dir_path):

    with ExifTool() as et:
        data = et.execute_json(*['-r', '-b', '-FileName', '-CreateDate', '-By-line', '-City', '-Country',
                                 '-Country-PrimaryLocationName', '-Caption-Abstract', '-Subject', '-Artist'] + [dir_path])
        return data






"""
CREATION DE L'EN-TETE DU MANIFEST
"""


def creer_root():
    root = ET.Element("ArchiveTransfer")
    root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    root.set('xmlns:pr', 'info:lc/xmlns/premis-v2')
    root.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'fr:gouv:culture:archivesdefrance:seda:v2.1 seda-2.1-main.xsd')
    root.set('xml:id', 'ID1')
    comment = ET.SubElement(root, "Comment")
    comment.text = "SIP Application"

    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    ET.SubElement(root, "MessageIdentifier").text = "MessageIdentifier0"
    archag = ET.SubElement(root, "ArchivalAgreement")
    archag.text = "TEST"
    archag.set('xmlns','fr:gouv:culture:archivesdefrance:seda:v2.1')
    archag.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')
    codelist = ET.SubElement(root, "CodeListVersions")
    codelist.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    codelist.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')
    ET.SubElement(codelist, "ReplyCodeListVersion").text = "ReplyCodeListVersion0"
    ET.SubElement(codelist, "MessageDigestAlgorithmCodeListVersion").text = "MessageDigestAlgorithmCodeListVersion0"
    ET.SubElement(codelist, "MimeTypeCodeListVersion").text = "MimeTypeCodeListVersion0"
    ET.SubElement(codelist, "EncodingCodeListVersion").text = "EncodingCodeListVersion0"
    ET.SubElement(codelist, "FileFormatCodeListVersion").text = "FileFormatCodeListVersion0"
    ET.SubElement(codelist, "CompressionAlgorithmCodeListVersion").text = "CompressionAlgorithmCodeListVersion0"
    ET.SubElement(codelist, "DataObjectVersionCodeListVersion").text = "DataObjectVersionCodeListVersion0"
    ET.SubElement(codelist, "StorageRuleCodeListVersion").text = "StorageRuleCodeListVersion0"
    ET.SubElement(codelist, "AppraisalRuleCodeListVersion").text = "AppraisalRuleCodeListVersion0"
    ET.SubElement(codelist, "AccessRuleCodeListVersion").text = "AccessRuleCodeListVersion0"
    ET.SubElement(codelist, "DisseminationRuleCodeListVersion").text = "DisseminationRuleCodeListVersion0"
    ET.SubElement(codelist, "ReuseRuleCodeListVersion").text = "ReuseRuleCodeListVersion0"
    ET.SubElement(codelist, "ClassificationRuleCodeListVersion").text = "ClassificationRuleCodeListVersion0"
    ET.SubElement(codelist, "AuthorizationReasonCodeListVersion").text = "AuthorizationReasonCodeListVersion0"
    ET.SubElement(codelist, "RelationshipCodeListVersion").text = "RelationshipCodeListVersion0"
    ET.SubElement(root, "DataObjectPackage")
    ET.SubElement(root, "DescriptiveMetadata")
    return root



"""
CREATION DU DATAOBJECTPACKAGE
"""
def dataobjgrp(arbre, directory, data_ir):
    root = arbre
    dtbjpck = root.find("DataObjectPackage")
    for dirpath, dirnames, filenames in os.walk(directory):
        for RP in data_ir:
            if RP[0] in dirpath:
                for item in filenames:
                    if "DS_Store" not in item:
                        dtbjgrp = ET.SubElement(dtbjpck,"DataObjectGroup")
                        bdtbj = ET.SubElement(dtbjgrp, "BinaryDataObject")
                        ET.SubElement(bdtbj, "DataObjectVersion").text = "BinaryMaster_1"
                        fileinfo = ET.SubElement(dtbjgrp, "FileInfo")
                        ET.SubElement(fileinfo, "Filename").text = item
    return root








"""
CREATION DE DESCRIPTIVE METADATA
"""


# Création d'un élément ArchiveUnit de niveau reportage pour chaque dossier dans le répertoire fourni en entrée
def ua_rp(directory, data_ir, arbre_rp, data):
    root = arbre_rp
    descrmd = root.find("DescriptiveMetadata")
    for item in os.listdir(directory):
        for RP in data_ir:
            if RP[0] in item:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    archiveunitrp = ET.Element("ArchiveUnit")
                    contentrp = ET.SubElement(archiveunitrp, "Content")
                    titlerp = ET.SubElement(contentrp, "Title")
                    titlerp.text = RP[1]
                    ET.SubElement(contentrp, "DescriptionLevel").text = "RecordGrp"
                    numrp = ET.SubElement(contentrp, "OriginatingAgencyArchiveUnitIdentifier")
                    numrp.text = RP[0]
                    origag = ET.SubElement(contentrp, "OriginatingAgency")
                    ET.SubElement(origag, "Identifier").text = "TEST"
                    subag = ET.SubElement(contentrp, "SubmissionAgency")
                    ET.SubElement(subag, "Identifier").text = "TEST"
                    startdate = ET.SubElement(contentrp, "StartDate")
                    dtd = datetime.strptime(RP[2], "%d.%m.%Y")
                    dtd = dtd.strftime("%Y-%m-%dT%H:%M:%S")
                    startdate.text = dtd
                    enddate = ET.SubElement(contentrp, "EndDate")
                    dtf = datetime.strptime(RP[3], "%d.%m.%Y")
                    dtf = dtf.strftime("%Y-%m-%dT%H:%M:%S")
                    enddate.text = dtf
                    archiveunitchild = sub_unit(item_path, data, data_ir)
                    for child in archiveunitchild:
                        archiveunitrp.append(child)
                    descrmd.append(archiveunitrp)
    return root


# Reproduction de l'aborescence des sous-dossiers et fichiers dans le dossier de niveau reportage
def sub_unit(directory, data, data_ir, parent=None):
    if parent is None:
        archiveunit = ET.Element("ArchiveUnit")
    else:
        archiveunit = parent
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            sub_archive_unit = ET.SubElement(archiveunit, "ArchiveUnit")
            contentsub = create_archive_unit_dir(item, data_ir)
            sub_archive_unit.append(contentsub)
            sub_unit(item_path, data, data_ir, sub_archive_unit)
        elif os.path.isfile(item_path) and "DS_Store" not in item:
            file_unit = create_archive_unit_file(item, data)
            archiveunit.append(file_unit)
    if parent is None:
        au_child = archiveunit.findall("./ArchiveUnit")
        return au_child


# Création d'un élément ArchiveUnit par sous-dossier
def create_archive_unit_dir(title_dir, data_ir):
    for RP in data_ir:
        if RP[0] in title_dir:
            pass
        else:
            contentdir = ET.Element("Content")
            title_element = ET.SubElement(contentdir, "Title")
            title_element.text = title_dir
            ET.SubElement(contentdir, "DescriptionLevel").text = "RecordGrp"
            return contentdir


# Création d'un élément ArchiveUnit par fichier + import des métadonnées extraites avec Exiftool
def create_archive_unit_file(title_file, data):
    arch_unit_item = ET.Element("ArchiveUnit")
    contentit = ET.SubElement(arch_unit_item,"Content")
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
            if item.get("IPTC:Caption-Abstract"):
                description = ET.SubElement(contentit, "Description")
                description.text = item["IPTC:Caption-Abstract"]
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
    return arch_unit_item


# Rattachement de l'arborescence à l'élément DescriptiveMetadata
def attach_sub_rp(selected_directory, arbre_rp, data_ir):
    root = arbre_rp
    descrmd = root.find("DescriptiveMetadata")
    arbre_dir = sub_unit(selected_directory, data, data_ir)
    descrmd.append(arbre_dir)
    return root





"""
MAIN
"""

selected_directory = select_directory()
#print("Dossier sélectionné :", selected_directory)

selected_csv = select_csv()
#print("Fichier sélectionné :", selected_csv)
data_ir = lire_ir_csv(selected_csv)
data = exif_extract(selected_directory)

root = creer_root()
root = dataobjgrp(root, selected_directory, data_ir)
arbre = ua_rp(selected_directory, data_ir, root, data)
arbre_str = ET.tostring(arbre, encoding='unicode')
print(arbre_str)
