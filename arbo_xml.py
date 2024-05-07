import os

import xml.etree.ElementTree as ET


directory = "C:\\Users\\selma.bensidhoum\\Documents\\Scripts\\pythonProject\\2012_test\\009918_20180419_001_120001 INVESTITURE 15 -LB-CA-PS-SR-"

def create_archive_unit_dir(title_dir):
    contentdir = ET.Element("Content")
    title_element = ET.SubElement(contentdir, "Title")
    title_element.text = title_dir
    ET.SubElement(contentdir, "DescriptionLevel").text = "RecordGrp"
    return contentdir

def create_archive_unit_file(title_file):
    contentit = ET.Element("Content")
    title_element = ET.SubElement(contentit, "Title")
    title_element.text = title_file
    ET.SubElement(contentit, "DescriptionLevel").text = "Item"
    return contentit

def sub_unit(directory):
    archiveunit = ET.Element("ArchiveUnit")
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            contentsub = create_archive_unit_dir(item)
            archiveunit.append(contentsub)
            archiveunitchild = sub_unit(item_path)
            archiveunit.append(archiveunitchild)
        elif os.path.isfile(item_path) and "DS_Store" not in item:
            file_unit = create_archive_unit_file(item)
            archiveunit.append(file_unit)
    return archiveunit


root = ET.Element("Racine")
arbre = sub_unit(directory)
root.append(arbre)
arbre_str = ET.tostring(root, encoding='unicode')
print(arbre_str)
