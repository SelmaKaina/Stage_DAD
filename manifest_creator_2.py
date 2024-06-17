import os
from datetime import datetime
import xml.etree.ElementTree as ET
from tkinter import filedialog
import csv
from exiftool import ExifTool
import re
import subprocess
import json
import shutil
import logging
from xml.dom import minidom

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -*- coding: utf-8 -*-

date_ajd = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")




"""
IMPORT DE L'ARBORESCENCE / IMPORT DE L'IR / LECTURE DE L'IR / EXTRACTION DES METADONNEES INTERNES
"""


def get_archiveunit_id():
    num_entree = input("Saisissez le numéro d'entrée :")
    num_paquet = input("Saisissez le numéro du paquet :")
    archival_agency_archive_unit_identifier = num_entree + "_" + num_paquet + "_"
    return archival_agency_archive_unit_identifier


def comment_message_id():
    value = input("Saisissez la valeur des balises Comment et MessageIdentifier :")
    return value


def select_list_rp():
    input("Appuyez sur Entrée pour sélectionner le fichier txt contenant la liste des reportages à ajouter au paquet.")
    list_rp = filedialog.askopenfilename()
    my_file = open(list_rp, "r")
    data = my_file.read()
    data_into_list = data.replace('\n', ',').split(",")
    return data_into_list


def select_directory():
    input("Appuyez sur Entrée pour sélectionner le dossier contenant les reportages à ajouter au paquet.")
    dir_path = filedialog.askdirectory()
    return dir_path


def select_csv():
    input("Appuyez sur Entrée pour sélectionner le fichier csv de métadonnées externes.")
    csv_path = filedialog.askopenfilename()
    data_ir = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data_ir.append(row)
    return data_ir


def chose_target_dir():
    input("Appuyez sur Entrée pour sélectionner le dossier de destination.")
    target_dir = filedialog.askdirectory()
    content = 'content'
    path = os.path.join(target_dir, content)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def exif_extract(dir_path, liste_rp):
    data = []
    processed_files = set()  # Pour garder une trace des fichiers déjà traités
    with ExifTool() as et:
        for rp in liste_rp:
            for item in os.listdir(dir_path):
                if rp in item:
                    item_path = os.path.join(dir_path, item)
                    if item_path in processed_files:
                        continue  # Passer au prochain fichier si celui-ci a déjà été traité
                    exif_data_list = et.execute_json(
                        '-r', '-b', '-FileName', '-CreateDate', '-By-line', '-City', '-Country',
                        '-Country-PrimaryLocationName', '-Caption-Abstract', '-Subject', '-Artist',
                        '-FileModifyDate', '-Filesize#', '-charset', 'utf8', item_path
                    )
                    if exif_data_list:
                        data.extend(exif_data_list)
                        processed_files.add(item_path)  # Ajouter le fichier à la liste des fichiers traités
    return data



def siegfried(dir_path, liste_rp):
    format_rp = []
    for rp in liste_rp:
        for item in os.listdir(dir_path):
            if rp in item:
                item_path = os.path.join(dir_path, item)
                md_format = subprocess.run(["sf", "-hash", "sha512", "-json", item_path], capture_output=True, text=True)
                md_format = json.loads(md_format.stdout)
                format_rp.append(md_format)

    for rp in format_rp:
        fichiers = rp.get("files", [])
        for file in fichiers:
            file["filename"] = file["filename"].replace("\\", "/")

    return format_rp

def metadata_json(data1, data2):
    new_data = []
    fichiers = []

    for rp in data1:
        files = rp.get("files", [])
        for file in files:
            filename = file["filename"]
            # Ajouter les métadonnées de Siegfried
            #fichiers.append(file)
            # Ajouter les métadonnées de ExifTool correspondantes
            for item in data2:
                if item.get("SourceFile") == filename:
                    file.update(item)
        new_data.append({'files': files})

    return new_data


"""
CREATION DE L'EN-TETE DU MANIFEST
"""


def creer_root(value):
    root = ET.Element("ArchiveTransfer")
    root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    root.set('xmlns:pr', 'info:lc/xmlns/premis-v2')
    root.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'fr:gouv:culture:archivesdefrance:seda:v2.1 seda-2.1-main.xsd')
    root.set('xml:id', 'ID1')
    comment = ET.SubElement(root, "Comment")
    comment.text = value

    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    ET.SubElement(root, "MessageIdentifier").text = value
    archag = ET.SubElement(root, "ArchivalAgreement")
    archag.text = "FRAN_CE_0001"
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

    data_object_package = ET.SubElement(root, "DataObjectPackage")

    ET.SubElement(root, "TransferRequestReplyIdentifier").text = "TEST"
    archival_agency = ET.SubElement(root, "ArchivalAgency")
    ET.SubElement(archival_agency, "Identifier").text = "Archives nationales"
    transferring_agency = ET.SubElement(root, "TransferringAgency")
    transferring_agency.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    transferring_agency.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')
    ET.SubElement(transferring_agency, "Identifier").text = "Mission Pr\xc3\xa9sidence de la R\xc3\xa9publique"

    return root



"""
CREATION DU DATAOBJECTPACKAGE
"""


def create_dataobjectgroup(arbre, directory, liste_rp):
    root = arbre
    data_object_package = root.find("DataObjectPackage")
    for dirpath, dirnames, filenames in os.walk(directory):
        dirpath = dirpath.replace("\\", "/")
        for item in filenames:
            item = dirpath + "/" + item
            for num in liste_rp:
                if str(num + " ").lower() in item.lower():
                    if "DS_Store" not in item and "Thumbs" not in item and "BridgeSort" not in item and "._" not in item:
                        data_object_group = ET.SubElement(data_object_package,"DataObjectGroup")
                        binary_data_object = ET.SubElement(data_object_group, "BinaryDataObject")
                        ET.SubElement(binary_data_object, "DataObjectVersion").text = "BinaryMaster_1"
                        ET.SubElement(binary_data_object, "Uri")
                        message_digest = ET.SubElement(binary_data_object, "MessageDigest")
                        message_digest.set("algorithm", "SHA-512")
                        ET.SubElement(binary_data_object, "Size")
                        format_identification = ET.SubElement(binary_data_object, "FormatIdentification")
                        ET.SubElement(format_identification, "FormatLitteral")
                        ET.SubElement(format_identification, "FormatId")
                        file_info = ET.SubElement(binary_data_object, "FileInfo")
                        filename = ET.SubElement(file_info, "Filename")
                        filename.text = item
                        ET.SubElement(file_info, "LastModified")
    return root


def package_metadata(arbre, data):
    root = arbre
    data_object_package = root.find("DataObjectPackage")
    binary_data_object = data_object_package.findall(".//BinaryDataObject")
    for obj in binary_data_object:
        item = obj.find(".//Filename").text
        for rp in data:
            files = rp.get("files", [])
            for file in files:
                if file.get("filename") == item:
                    if file.get("File:FileSize"):
                        filesize = obj.find("Size")
                        filesize.text = str(file["File:FileSize"])
                    if file.get("File:FileModifyDate"):
                        last_modified = obj.find(".//LastModified")
                        modif_date = file.get("File:FileModifyDate")
                        match = re.match(
                            r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?",
                            modif_date)
                        if match:
                            modif_date = match.group(1)
                            modif_date = datetime.strptime(modif_date, "%Y:%m:%d %H:%M:%S")
                            modif_date = modif_date.strftime("%Y-%m-%dT%H:%M:%S")
                            last_modified.text = modif_date
                    file_name = obj.find(".//Filename")
                    file_name.text = file.get("File:FileName")
                    message_digest = obj.find("MessageDigest")
                    message_digest.text = file.get("sha512")
                    format_identification = obj.find("FormatIdentification")
                    format_litteral = format_identification.find("FormatLitteral")
                    formatid = format_identification.find("FormatId")
                    for i in file.get("matches"):
                        format_litteral.text = i["format"]
                        if i["mime"]:
                            ET.SubElement(format_identification, "MimeType").text = i["mime"]
                        formatid.text = i["id"]

    return root


"""
CREATION DE DESCRIPTIVE METADATA
"""


# Création d'un élément ArchiveUnit de niveau reportage pour chaque dossier dans le répertoire fourni en entrée
def ua_rp(directory, data_ir, arbre_rp, data, liste_rp):
    root = arbre_rp
    data_object_package = root.find("DataObjectPackage")
    descriptive_metadata = ET.SubElement(data_object_package, "DescriptiveMetadata")
    for item in os.listdir(directory):
        for num in liste_rp:
            for RP in data_ir:
                if num == RP[0] and str(num+" ").lower() in item.lower():
                    print(item)
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        archiveunitrp = ET.Element("ArchiveUnit")
                        contentrp = ET.SubElement(archiveunitrp, "Content")
                        ET.SubElement(contentrp, "DescriptionLevel").text = "RecordGrp"
                        titlerp = ET.SubElement(contentrp, "Title")
                        titlerp.text = RP[1]
                        ET.SubElement(contentrp, "ArchivalAgencyArchiveUnitIdentifier")
                        numrp = ET.SubElement(contentrp, "OriginatingAgencyArchiveUnitIdentifier")
                        numrp.text = RP[0]
                        originating_agency = ET.SubElement(contentrp, "OriginatingAgency")
                        ET.SubElement(originating_agency, "Identifier").text = "FRAN_NP_009886"
                        submission_agency = ET.SubElement(contentrp, "SubmissionAgency")
                        ET.SubElement(submission_agency, "Identifier").text = "FRAN_NP_009886"
                        startdate = ET.SubElement(contentrp, "StartDate")
                        dtd = datetime.strptime(RP[2], "%d.%m.%Y")
                        dtd = dtd.strftime("%Y-%m-%dT%H:%M:%S")
                        startdate.text = dtd
                        enddate = ET.SubElement(contentrp, "EndDate")
                        dtf = datetime.strptime(RP[3], "%d.%m.%Y")
                        dtf = dtf.strftime("%Y-%m-%dT%H:%M:%S")
                        enddate.text = dtf
                        archiveunitchild = sub_unit(item_path, data, data_ir, liste_rp)
                        for child in archiveunitchild:
                            archiveunitrp.append(child)
                        descriptive_metadata.append(archiveunitrp)
    return root


# Reproduction de l'aborescence des sous-dossiers et fichiers dans le dossier de niveau reportage
def sub_unit(directory, data, data_ir, liste_rp, parent=None):
    if parent is None:
        archiveunit = ET.Element("ArchiveUnit")
    else:
        archiveunit = parent
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            sub_archive_unit = ET.SubElement(archiveunit, "ArchiveUnit")
            contentsub = create_archive_unit_dir(item, data_ir, liste_rp)
            sub_archive_unit.append(contentsub)
            sub_unit(item_path, data, data_ir, liste_rp, sub_archive_unit)
        elif os.path.isfile(item_path) and "DS_Store" not in item and "Thumbs" not in item and "BridgeSort" not in item and "._" not in item:
            file_unit = create_archive_unit_file(item, data, item_path)
            archiveunit.append(file_unit)
    if parent is None:
        au_child = archiveunit.findall("./ArchiveUnit")
        return au_child


# Création d'un élément ArchiveUnit par sous-dossier
def create_archive_unit_dir(title_dir, data_ir, liste_rp):
    for num in liste_rp:
        for RP in data_ir:
            if num == RP[0] and num in title_dir:
                pass
            else:
                contentdir = ET.Element("Content")
                ET.SubElement(contentdir, "DescriptionLevel").text = "RecordGrp"
                title_element = ET.SubElement(contentdir, "Title")
                title_element.text = title_dir
                ET.SubElement(contentdir,"ArchivalAgencyArchiveUnitIdentifier")
                originating_agency = ET.SubElement(contentdir, "OriginatingAgency")
                ET.SubElement(originating_agency, "Identifier").text = "FRAN_NP_009886"
                submission_agency = ET.SubElement(contentdir, "SubmissionAgency")
                ET.SubElement(submission_agency, "Identifier").text = "FRAN_NP_009886"
                return contentdir


# Création d'un élément ArchiveUnit par fichier + import des métadonnées extraites avec Exiftool
def create_archive_unit_file(title_file, data, item_path):
    item_path = item_path.replace("\\","/")
    arch_unit_item = ET.Element("ArchiveUnit")
    contentit = ET.SubElement(arch_unit_item,"Content")
    ET.SubElement(contentit, "DescriptionLevel").text = "Item"
    title_element = ET.SubElement(contentit, "Title")
    title_element.text = title_file
    ET.SubElement(contentit, "ArchivalAgencyArchiveUnitIdentifier")
    for item in data:
        files = item.get("files", [])
        for file in files:
            sourcefile = file.get("SourceFile")
            if sourcefile == item_path:
                if contentit.find("BaliseTemp") is not None:
                    pass
                else:
                    temp_hash = ET.SubElement(contentit, "BaliseTemp")
                    temp_hash.text = file.get("sha512")
                if contentit.find("Description") is not None:
                    pass
                else:
                    if file.get("IPTC:Caption-Abstract"):
                        description = ET.SubElement(contentit, "Description")
                        description.text = file.get("IPTC:Caption-Abstract")
                    else:
                        pass
                if contentit.find("Tag") is not None:
                    pass
                else:
                    if file.get("XMP:Subject"):
                        if not isinstance(file.get("XMP:Subject"), list):
                            tagit = ET.SubElement(contentit, "Tag")
                            tagit.text = str(file.get("XMP:Subject"))
                        else:
                            for tag in file.get("XMP:Subject"):
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = str(tag)
                    else:
                        if file.get("IPTC:Keywords"):
                            if not isinstance(file.get("IPTC:Keywords"), list):
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = str(file.get("IPTC:Keywords"))
                            else:
                                for tag in file.get("IPTC:Keywords"):
                                    tagit = ET.SubElement(contentit, "Tag")
                                    tagit.text = str(tag)
                        else:
                            pass
                if contentit.find("Coverage") is not None:
                    pass
                else:
                    if file.get("XMP:Country" or "IPTC:Country-PrimaryLocationName" or "XMP:City" or "IPTC:City"):
                        cov = ET.SubElement(contentit, "Coverage")
                        if file.get("XMP:Country"):
                            spatial_pays = ET.SubElement(cov, "Spatial")
                            spatial_pays.text = file.get("XMP:Country")
                        else:
                            if file.get("IPTC:Country-PrimaryLocationName"):
                                spatial_pays = ET.SubElement(cov, "Spatial")
                                spatial_pays.text = file.get("IPTC:Country-PrimaryLocationName")
                            else:
                                pass
                        if file.get("XMP:City"):
                            spatial_ville = ET.SubElement(cov, "Spatial")
                            spatial_ville.text = file.get("XMP:City")
                        else:
                            if file.get("IPTC:City"):
                                spatial_ville = ET.SubElement(cov, "Spatial")
                                spatial_ville.text = file.get("IPTC:City")
                            else:
                                pass
                    else:
                        pass
                if contentit.find("OriginatingAgency") is not None:
                    pass
                else:
                    originating_agency = ET.SubElement(contentit, "OriginatingAgency")
                    ET.SubElement(originating_agency, "Identifier").text = "FRAN_NP_009886"
                if contentit.find("SubmissionAgency") is not None:
                    pass
                else:
                    submission_agency = ET.SubElement(contentit, "SubmissionAgency")
                    ET.SubElement(submission_agency, "Identifier").text = "FRAN_NP_009886"
                if contentit.find("AuthorizedAgent") is not None:
                    pass
                else:
                    if file.get("IPTC:By-line"):
                        authorized_agent = ET.SubElement(contentit, "AuthorizedAgent")
                        fullname = ET.SubElement(authorized_agent, "FullName")
                        fullname.text = file.get("IPTC:By-line")
                        ET.SubElement(authorized_agent, "Activity").text = "Photographe"
                        ET.SubElement(authorized_agent, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
                    else:
                        if file.get("EXIF:Artist"):
                            authorized_agent = ET.SubElement(contentit, "AuthorizedAgent")
                            fullname = ET.SubElement(authorized_agent, "FullName")
                            fullname.text = file.get("EXIF:Artist")
                            ET.SubElement(authorized_agent, "Activity").text = "Photographe"
                            ET.SubElement(authorized_agent, "Mandate").text = "Photographe Pr\xc3\xa9sidence"
                        else:
                            pass
                if contentit.find("StartDate") is not None:
                    pass
                else:
                    if file.get("XMP:CreateDate") is not None:
                        createdate = file.get("XMP:CreateDate")
                        if len(createdate) == 16:
                            createdate += ":00"
                        else:
                            createdate = createdate
                        match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?",
                                         createdate)
                        if match:
                            createdate = match.group(1)
                            createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                            createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                            startdateit = ET.SubElement(contentit, "StartDate")
                            startdateit.text = createdate
                            enddateit = ET.SubElement(contentit, "EndDate")
                            enddateit.text = createdate
                        else:
                            print("Format de date incompatible")
                    else:
                        if file.get("EXIF:CreateDate") is not None:
                            createdate = file.get("EXIF:CreateDate")
                            if len(createdate) == 16:
                                createdate += ":00"
                            else:
                                createdate = createdate
                            match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(?:(\.\d+))?(?:([-+]\d{2}:\d{2}))?",
                                             createdate)
                            if match:
                                createdate = match.group(1)
                                createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                                createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                                startdateit = ET.SubElement(contentit, "StartDate")
                                startdateit.text = createdate
                                enddateit = ET.SubElement(contentit, "EndDate")
                                enddateit.text = createdate
                            else:
                                print("Format de date incompatible")
                        else:
                            pass
    data_object_reference = ET.SubElement(arch_unit_item, "DataObjectReference")
    ET.SubElement(data_object_reference, "DataObjectGroupReferenceId")
    return arch_unit_item


def delete_duplicate_dog(arbre):
    objets_uniques = {}
    objects_a_supprimer = []

    data_object_package = arbre.find(".//DataObjectPackage")
    for data_object_group in data_object_package.findall("DataObjectGroup"):
        binary_data_object = data_object_group.find("BinaryDataObject")
        message_digest = binary_data_object.find("MessageDigest").text
        filename = binary_data_object.find(".//Filename").text
        objet = (message_digest, filename)
        if objet in objets_uniques:
            objects_a_supprimer.append((data_object_group, data_object_package))
        else:
            objets_uniques[objet] = data_object_group

    for element, parent in objects_a_supprimer:
        parent.remove(element)

    return arbre



def id_attrib(arbre, archive_unit_id):
    root = arbre
    data_object_package = root.find("DataObjectPackage")
    data_object_group = data_object_package.findall(".//DataObjectGroup")
    descriptive_metadata = data_object_package.find("DescriptiveMetadata")
    AUs = descriptive_metadata.findall(".//ArchiveUnit")
    id_au = 0
    for AU in AUs:
        id_au = id_au+1
        AU.set("id", "AU"+str(id_au))
        data_object_group_ref_id = AU.find(".//DataObjectGroupReferenceId")
        archival_agency_archive_unit_identifier = AU.find(".//ArchivalAgencyArchiveUnitIdentifier")
        archival_agency_archive_unit_identifier.text = archive_unit_id+str(id_au)
        if AU.find(".//DescriptionLevel").text == "Item":
            temp_hash = AU.find(".//BaliseTemp").text
            got = 0
            for obj in data_object_group:
                got = got + 1
                obj.set('id', 'GOT' + str(got))
                binary_data_object = obj.find("BinaryDataObject")
                binary_data_object.set('id', 'BDO'+str(got))
                myid = binary_data_object.attrib['id']
                uri = binary_data_object.find("Uri")
                filename = obj.find(".//Filename").text
                uri.text = 'content/' + myid + "." + filename.split('.')[-1]
                message_digest = obj.find(".//MessageDigest").text
                id = obj.attrib['id']

                if temp_hash == message_digest:
                    data_object_group_ref_id.text = id

    return root


def create_descriptive_metadata(arbre):
    root = arbre
    data_object_package = root.find("DataObjectPackage")
    management_metadata = ET.SubElement(data_object_package, "ManagementMetadata")
    management_metadata.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    management_metadata.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')
    ET.SubElement(management_metadata, "ArchivalProfile").text = "FRAN_PR_0001"
    ET.SubElement(management_metadata, "AcquisitionInformation").text = "Versement"
    ET.SubElement(management_metadata, "LegalStatus").text = "Public Archive"
    ET.SubElement(management_metadata, "OriginatingAgencyIdentifier").text = "TEST"
    ET.SubElement(management_metadata, "SubmissionAgencyIdentifier").text = "TEST"
    descriptive_metadata = data_object_package.find("DescriptiveMetadata")
    AUs = descriptive_metadata.findall(".//ArchiveUnit")
    for AU in AUs:
        content = AU.find("Content")
        if content.find("BaliseTemp") is not None:
            temp_hash = content.find("BaliseTemp")
            content.remove(temp_hash)
        else:
            pass
    return root

def copy(target_dir, arbre, data):
    root = arbre
    data_object_package = root.find("DataObjectPackage")
    data_object_group = data_object_package.findall("DataObjectGroup")
    for objet in data_object_group:
        file_name = objet.find(".//Filename").text
        binary_data_object = objet.find("BinaryDataObject")
        message_digest = binary_data_object.find("MessageDigest").text
        new_name = binary_data_object.attrib['id']
        oldext = os.path.splitext(file_name)[1]
        new_name = new_name + oldext
        new_path = os.path.join(target_dir, new_name)
        for item in data:
            files = item.get("files", [])
            for file in files:
                if message_digest == file.get("sha512"):
                    old_path = file.get("filename")
                    shutil.copy(old_path, new_path)


"""
MAIN
"""

archive_unit_id = get_archiveunit_id()
print(archive_unit_id)

value = comment_message_id()

selected_directory = select_directory()
print("Dossier sélectionné :", selected_directory)

data_ir = select_csv()
print("Fichier sélectionné de métadonnées externe sélectionné.")

liste_rp = select_list_rp()
print("Reportages sélectionnés :", liste_rp)

target_dir = chose_target_dir()
print("Répertoire cible :", target_dir)

data_exif = exif_extract(selected_directory, liste_rp)
data_sig = siegfried(selected_directory, liste_rp)
data = metadata_json(data_sig, data_exif)
print("Métadonnées internes des photos extraites.")


root = creer_root(value)
print("En-tête du manifest créé")
root = create_dataobjectgroup(root, selected_directory, liste_rp)
print("DataObjectGroup créés")
root = package_metadata(root, data)
print("Metadonnées ajoutées aux DataObjectGroup")
arbre = ua_rp(selected_directory, data_ir, root, data, liste_rp)
print("ArchiveUnit créés")
arbre = delete_duplicate_dog(arbre)
print("Doublons supprimés des DataObjectGroup")
arbre = id_attrib(arbre, archive_unit_id)
print("Identifiants attribués.")
arbre = create_descriptive_metadata(arbre)
print("DescriptiveMetadata créé")
arbre_str = minidom.parseString(ET.tostring(arbre, encoding='unicode')).toprettyxml(indent="   ")
target_manifest = os.path.split(target_dir)
target_manifest = target_manifest[0]
target_manifest = os.path.join(target_manifest, "manifest.xml")
with open(target_manifest, "w") as f:
    f.write(arbre_str)
print("Manifest créé.")

copy(target_dir, arbre, data)
print("Fichiers copiés et renommés")
