import re
import csv
import xml.etree.ElementTree as ET

# Charger le fichier XML
tree = ET.parse("FRAN_IR_054605.xml")
root = tree.getroot()

# Définir la valeur de la cote de consultation à rechercher
cote_consultation_recherchee = "20100562"

# Ouvrir un fichier CSV pour écrire les données
with open("donnees_extraites.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Écrire l'en-tête du fichier CSV
    writer.writerow(["Cote", "Numéro du reportage", "Titre", "Date", "Photographe(s)"])

    # Parcourir chaque élément <c> dans le document XML
    for c_element in root.findall(".//c"):
        # Trouver l'élément <unitid> de type "cote-de-consultation" et vérifier si sa valeur correspond à celle recherchée
        unitid_element = c_element.find("./did/unitid[@type='cote-de-consultation']")
        if unitid_element is not None and cote_consultation_recherchee in unitid_element.text:
            # Récupérer les valeurs des balises demandées
            pieces_element = c_element.find("./did/unitid[@type='pieces']")
            if pieces_element is not None:
                pieces = ""
                if pieces_element is not None:
                    # Utiliser une expression régulière pour extraire les chiffres après "Reportage"
                    match = re.search(r"Reportages?\s*(\d{4}\s?\w?\w?\w?)", pieces_element.text, re.IGNORECASE)
                    if match:
                        pieces = match.group(1)

                unittitle_element = c_element.find("./did/unittitle")
                unittitle = unittitle_element.text if unittitle_element is not None else ""
                if unittitle:
                    unittitle = f'"{unittitle}"'

                unitdate_element = c_element.find("./did/unitdate")
                unitdate_normal = unitdate_element.get("normal") if unitdate_element is not None else ""

                # Récupérer le texte du premier paragraphe de <scopecontent> contenant "photographe"
                scopecontent_p = ""
                scopecontent_p_elements = c_element.findall("./scopecontent/p")
                for scopecontent_p_element in scopecontent_p_elements:
                    if scopecontent_p_element.text and "photographe" in scopecontent_p_element.text.lower():
                        match = re.search(r"(?:photographes?\s?:?\s*)(([A-Z]\.\s*+[A-Z][a-z]*,?\s?)*)", scopecontent_p_element.text, re.IGNORECASE)
                        if match:
                            scopecontent_p = match.group(1)
                            break  # Sortir de la boucle dès qu'un nom de photographe est trouvé

                # Écrire les données dans le fichier CSV
                writer.writerow([unitid_element.text, pieces, unittitle, unitdate_normal, scopecontent_p])

print("Données extraites et exportées vers le fichier CSV avec succès.")
