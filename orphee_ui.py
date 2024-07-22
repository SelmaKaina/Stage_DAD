import os
from datetime import datetime
import xml.etree.ElementTree as ET
import csv
from exiftool import ExifTool
import re
import subprocess
import json
import shutil
import logging
import sys
from xml.dom import minidom
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QCheckBox, QFileDialog,
    QHBoxLayout, QGridLayout, QScrollArea, QComboBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -*- coding: utf-8 -*-

# Import de la date du jour de fabrication du SIP
date_ajd = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Définir tous les attributs d'instance ici
        self.num_entree = None
        self.entree_input = None
        self.num_paquet = None
        self.paquet_input = None
        self.versement_label = None
        self.versement_input = None
        self.archival_agency_identifier_label = None
        self.archival_agency_identifier_input = None
        self.transferring_agency_identifier_label = None
        self.transferring_agency_identifier_input = None
        self.originating_agency_identifier_label = None
        self.originating_agency_identifier_input = None
        self.submission_agency_identifier_label = None
        self.submission_agency_identifier_input = None
        self.archival_agreement_label = None
        self.archival_agreement_input = None
        self.authorized_agent_activity_label = None
        self.authorized_agent_activity_input = None
        self.authorized_agent_mandate_label = None
        self.authorized_agent_mandate_input = None
        self.archival_profile_label = None
        self.archival_profile_input = None
        self.acquisition_information_label = None
        self.acquisition_information_input = None
        self.legal_status_label = None
        self.legal_status_input = None
        self.metadata_checkboxes = []
        self.optional_checkbox = None
        self.rattachement_label = None
        self.rattachement_input = None
        self.nom_rattachement_label = None
        self.nom_rattachement_input = None
        self.entree_dir_button = None
        self.entree_dir_label = None
        self.cible_dir_button = None
        self.cible_dir_label = None
        self.csv_file_button = None
        self.csv_file_label = None
        self.txt_file_button = None
        self.txt_file_label = None
        self.submit_button = None

        self.initui()

    def initui(self):
        """
        Initialise l'interface utilisateur de l'application ORPhEE.
        """
        self.setWindowTitle("ORPhEE")
        # Style pour l'ensemble de l'application
        self.setStyleSheet("""
            background-color: #f6ecdb;
            font-size: 12px;
            font-family: Cambria;
            padding: 10px;
        """)
        self.resize(800, 600)
        self.setWindowIcon(QIcon("./package/lyre.png"))

        # Texte introductif
        intro_label = QLabel("Veuillez remplir le formulaire ci-dessous :")
        intro_label.setStyleSheet("color: #865746;")
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Créer les widgets pour les champs de texte existants
        self.num_entree = QLabel("Numéro de l'entrée :")
        self.num_entree.setStyleSheet("color: #865746;")
        self.entree_input = QLineEdit()
        self.entree_input.setPlaceholderText("ex : 20240001")

        self.num_paquet = QLabel("Numéro du paquet :")
        self.num_paquet.setStyleSheet("color: #865746;")
        self.paquet_input = QLineEdit()
        self.paquet_input.setPlaceholderText("ex : 1")

        self.versement_label = QLabel("Intitulé du versement :")
        self.versement_label.setStyleSheet("color: #865746;")
        self.versement_input = QLineEdit()
        self.versement_input.setPlaceholderText("Valeur des éléments Comment et MessageIdentifier.")

        # Ajouter les nouveaux champs requis

        self.archival_agency_identifier_label = QLabel("ArchivalAgency Identifier :")
        self.archival_agency_identifier_label.setStyleSheet("color: #865746;")
        self.archival_agency_identifier_input = QLineEdit()
        self.archival_agency_identifier_input.setPlaceholderText("Identifiant du service d'archives.")

        self.transferring_agency_identifier_label = QLabel("TransferringAgency :")
        self.transferring_agency_identifier_label.setStyleSheet("color: #865746;")
        self.transferring_agency_identifier_input = QLineEdit()
        self.transferring_agency_identifier_input.setPlaceholderText("Nom du service versant.")

        self.originating_agency_identifier_label = QLabel("OriginatingAgency Identifier :")
        self.originating_agency_identifier_label.setStyleSheet("color: #865746;")
        self.originating_agency_identifier_input = QLineEdit()
        self.originating_agency_identifier_input.setPlaceholderText("Identifiant du service producteur.")

        self.submission_agency_identifier_label = QLabel("SubmissionAgency :")
        self.submission_agency_identifier_label.setStyleSheet("color: #865746;")
        self.submission_agency_identifier_input = QLineEdit()
        self.submission_agency_identifier_input.setPlaceholderText(
            "Identifiant du service versant responsable du transfert de données.")

        self.archival_agreement_label = QLabel("ArchivalAgreement :")
        self.archival_agreement_label.setStyleSheet("color: #865746;")
        self.archival_agreement_input = QLineEdit()
        self.archival_agreement_input.setPlaceholderText("Référence à un accord de service / contrat d'entrée.")

        self.authorized_agent_activity_label = QLabel("AuthorizedAgent Activity :")
        self.authorized_agent_activity_label.setStyleSheet("color: #865746;")
        self.authorized_agent_activity_input = QLineEdit()
        self.authorized_agent_activity_input.setPlaceholderText(
            "Activité de la personne détenant des droits sur la photo (ex : Photographe).")

        self.authorized_agent_mandate_label = QLabel("AuthorizedAgent Mandate :")
        self.authorized_agent_mandate_label.setStyleSheet("color: #865746;")
        self.authorized_agent_mandate_input = QLineEdit()
        self.authorized_agent_mandate_input.setPlaceholderText(
            "Statut du détenteur de droits (ex : Photographe service public, d'agence, privé).")

        self.archival_profile_label = QLabel("ArchivalProfile :")
        self.archival_profile_label.setStyleSheet("color: #865746;")
        self.archival_profile_input = QLineEdit()
        self.archival_profile_input.setPlaceholderText(
            "Référence au profil d’archivage applicable aux unités d’archives.")

        self.acquisition_information_label = QLabel("AcquisitionInformation :")
        self.acquisition_information_label.setStyleSheet("color: #865746;")
        self.acquisition_information_input = QLineEdit()
        self.acquisition_information_input.setPlaceholderText("Référence aux modalités d'entrée des archives.")

        self.legal_status_label = QLabel("LegalStatus :")
        self.legal_status_label.setStyleSheet("color: #865746;")
        self.legal_status_input = QComboBox()
        self.legal_status_input.addItems(["Public Archive", "Private Archive", "Public and Private Archive"])

        # Cases à cocher pour les valeurs à sélectionner
        self.metadata_checkboxes = []
        createdate = QCheckBox(f"-CreateDate")
        createdate.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(createdate)

        modifdate = QCheckBox(f"-FileModifyDate")
        modifdate.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(modifdate)

        by_line = QCheckBox(f"-By-line")
        by_line.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(by_line)

        artist = QCheckBox(f"-Artist")
        artist.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(artist)

        creator = QCheckBox(f"-Creator")
        creator.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(creator)

        city = QCheckBox(f"-City")
        city.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(city)

        country = QCheckBox(f"-Country")
        country.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(country)

        country_pln = QCheckBox(f"-Country-PrimaryLocationName")
        country_pln.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(country_pln)

        caption = QCheckBox(f"-Caption-Abstract")
        caption.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(caption)

        description = QCheckBox(f"-Description")
        description.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(description)

        subject = QCheckBox(f"-Subject")
        subject.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(subject)

        keywords = QCheckBox(f"-Keywords")
        keywords.setStyleSheet("color: #865746;")
        self.metadata_checkboxes.append(keywords)

        # Créer la checkbox pour les champs optionnels
        self.optional_checkbox = QCheckBox("Effectuer un rattachement à une autre unité archivistique")
        self.optional_checkbox.setStyleSheet("color: #865746;")
        self.optional_checkbox.stateChanged.connect(self.toggle_optional_fields)

        # Créer les widgets pour les champs de texte optionnels
        self.rattachement_label = QLabel("Cote de l'UA de rattachement :")
        self.rattachement_label.setStyleSheet("color: #865746;")
        self.rattachement_input = QLineEdit()

        self.nom_rattachement_label = QLabel("Nom de l'UA de rattachement :")
        self.nom_rattachement_label.setStyleSheet("color: #865746;")
        self.nom_rattachement_input = QLineEdit()

        # Initialement, les champs optionnels ne sont pas visibles
        self.rattachement_label.setVisible(False)
        self.rattachement_input.setVisible(False)
        self.nom_rattachement_label.setVisible(False)
        self.nom_rattachement_input.setVisible(False)

        # Boutons pour sélectionner répertoires et fichiers
        self.entree_dir_button = QPushButton("Sélectionner le répertoire contenant les reportages")
        self.entree_dir_button.setStyleSheet("background-color: #1c85f6; color: #fffbef;")
        self.entree_dir_button.clicked.connect(self.select_entree_dir)
        self.entree_dir_label = QLabel("Aucun répertoire sélectionné")
        self.entree_dir_label.setStyleSheet("color: #865746;")

        self.cible_dir_button = QPushButton("Sélectionner le répertoire où sera créé le SIP")
        self.cible_dir_button.setStyleSheet("background-color: #1c85f6; color: #fffbef;")
        self.cible_dir_button.clicked.connect(self.select_cible_dir)
        self.cible_dir_label = QLabel("Aucun répertoire sélectionné")
        self.cible_dir_label.setStyleSheet("color: #865746;")

        self.csv_file_button = QPushButton("Sélectionner l'instrument de recherche (CSV)")
        self.csv_file_button.setStyleSheet("background-color: #1c85f6; color: #fffbef;")
        self.csv_file_button.clicked.connect(self.select_csv_file)
        self.csv_file_label = QLabel("Aucun fichier CSV sélectionné")
        self.csv_file_label.setStyleSheet("color: #865746;")

        self.txt_file_button = QPushButton("Sélectionner la liste des reportages (TXT)")
        self.txt_file_button.setStyleSheet("background-color: #1c85f6; color: #fffbef;")
        self.txt_file_button.clicked.connect(self.select_txt_file)
        self.txt_file_label = QLabel("Aucun fichier texte sélectionné")
        self.txt_file_label.setStyleSheet("color: #865746;")

        # Créer un bouton de soumission
        self.submit_button = QPushButton("Soumettre")
        self.submit_button.setStyleSheet("background-color: #F5BD02; color: #fffbef;")
        self.submit_button.clicked.connect(self.handle_submit)  # Connecter à la fonction de traitement
        self.submit_button.setEnabled(False)  # Initialement désactivé

        # Créer un layout en grille pour organiser les widgets
        grid_layout = QGridLayout()
        grid_layout.addWidget(intro_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.num_entree, 1, 0)
        grid_layout.addWidget(self.entree_input, 1, 1)
        grid_layout.addWidget(self.num_paquet, 2, 0)
        grid_layout.addWidget(self.paquet_input, 2, 1)
        grid_layout.addWidget(self.versement_label, 3, 0)
        grid_layout.addWidget(self.versement_input, 3, 1)
        grid_layout.addWidget(self.archival_agency_identifier_label, 4, 0)
        grid_layout.addWidget(self.archival_agency_identifier_input, 4, 1)
        grid_layout.addWidget(self.transferring_agency_identifier_label, 5, 0)
        grid_layout.addWidget(self.transferring_agency_identifier_input, 5, 1)
        grid_layout.addWidget(self.originating_agency_identifier_label, 6, 0)
        grid_layout.addWidget(self.originating_agency_identifier_input, 6, 1)
        grid_layout.addWidget(self.submission_agency_identifier_label, 7, 0)
        grid_layout.addWidget(self.submission_agency_identifier_input, 7, 1)
        grid_layout.addWidget(self.archival_agreement_label, 8, 0)
        grid_layout.addWidget(self.archival_agreement_input, 8, 1)
        grid_layout.addWidget(self.authorized_agent_activity_label, 9, 0)
        grid_layout.addWidget(self.authorized_agent_activity_input, 9, 1)
        grid_layout.addWidget(self.authorized_agent_mandate_label, 10, 0)
        grid_layout.addWidget(self.authorized_agent_mandate_input, 10, 1)
        grid_layout.addWidget(self.archival_profile_label, 11, 0)
        grid_layout.addWidget(self.archival_profile_input, 11, 1)
        grid_layout.addWidget(self.acquisition_information_label, 12, 0)
        grid_layout.addWidget(self.acquisition_information_input, 12, 1)
        grid_layout.addWidget(self.legal_status_label, 13, 0)
        grid_layout.addWidget(self.legal_status_input, 13, 1)

        # Ajouter les cases à cocher pour les métadonnées
        metadata_label = QLabel("Métadonnées internes à extraire :")
        metadata_label.setStyleSheet("color: #865746;")
        grid_layout.addWidget(metadata_label, 14, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        row = 17
        # Ajouter les checkboxes dans des QVBoxLayout pour les centrer en colonnes
        checkbox_column1 = QVBoxLayout()
        checkbox_column2 = QVBoxLayout()
        checkbox_column3 = QVBoxLayout()

        for checkbox in self.metadata_checkboxes[:4]:
            checkbox_column1.addWidget(checkbox)
        for checkbox in self.metadata_checkboxes[4:8]:
            checkbox_column2.addWidget(checkbox)
        for checkbox in self.metadata_checkboxes[8:]:
            checkbox_column3.addWidget(checkbox)

        # Ajouter ces QVBoxLayout dans un QHBoxLayout pour centrer les colonnes
        metadata_layout = QHBoxLayout()
        metadata_layout.addLayout(checkbox_column1)
        metadata_layout.addLayout(checkbox_column2)
        metadata_layout.addLayout(checkbox_column3)

        grid_layout.addLayout(metadata_layout, 15, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # Ajouter la checkbox optionnelle et les champs optionnels
        grid_layout.addWidget(self.optional_checkbox, row + 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.rattachement_label, row + 2, 0)
        grid_layout.addWidget(self.rattachement_input, row + 2, 1)
        grid_layout.addWidget(self.nom_rattachement_label, row + 3, 0)
        grid_layout.addWidget(self.nom_rattachement_input, row + 3, 1)

        # Ajouter les boutons pour sélectionner les répertoires et fichiers
        grid_layout.addWidget(self.entree_dir_button, row + 4, 0)
        grid_layout.addWidget(self.entree_dir_label, row + 4, 1)
        grid_layout.addWidget(self.cible_dir_button, row + 5, 0)
        grid_layout.addWidget(self.cible_dir_label, row + 5, 1)
        grid_layout.addWidget(self.csv_file_button, row + 6, 0)
        grid_layout.addWidget(self.csv_file_label, row + 6, 1)
        grid_layout.addWidget(self.txt_file_button, row + 7, 0)
        grid_layout.addWidget(self.txt_file_label, row + 7, 1)

        # Ajouter le bouton Soumettre en bas, centré
        grid_layout.addWidget(self.submit_button, row + 8, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # Créer un widget pour le contenu principal et définir le layout
        main_widget = QWidget()
        main_widget.setLayout(grid_layout)

        # Créer une zone de défilement pour le widget principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)

        self.setCentralWidget(scroll_area)

        # Connecter la vérification des champs obligatoires
        self.entree_input.textChanged.connect(self.check_fields)
        self.paquet_input.textChanged.connect(self.check_fields)
        self.versement_input.textChanged.connect(self.check_fields)
        self.archival_agency_identifier_input.textChanged.connect(self.check_fields)
        self.transferring_agency_identifier_input.textChanged.connect(self.check_fields)
        self.originating_agency_identifier_input.textChanged.connect(self.check_fields)
        self.submission_agency_identifier_input.textChanged.connect(self.check_fields)
        self.archival_agreement_input.textChanged.connect(self.check_fields)
        self.authorized_agent_activity_input.textChanged.connect(self.check_fields)
        self.authorized_agent_mandate_input.textChanged.connect(self.check_fields)
        self.archival_profile_input.textChanged.connect(self.check_fields)
        self.acquisition_information_input.textChanged.connect(self.check_fields)
        self.legal_status_input.currentTextChanged.connect(self.check_fields)

        # Vérifier les champs au démarrage de l'application
        self.check_fields()

    def check_fields(self):
        # Vérifier si tous les champs obligatoires sont remplis pour activer le bouton Soumettre
        mandatory_fields = [
            self.entree_input, self.paquet_input, self.versement_input,
            self.transferring_agency_identifier_input, self.originating_agency_identifier_input,
            self.submission_agency_identifier_input, self.archival_agreement_input,
            self.authorized_agent_activity_input, self.authorized_agent_mandate_input,
            self.archival_profile_input, self.acquisition_information_input
        ]

        for field in mandatory_fields:
            if field.text().strip() == "":
                self.submit_button.setEnabled(False)
                return

        # Vérifier le champ Legal Status
        if self.legal_status_input.currentText().strip() == "":
            self.submit_button.setEnabled(False)
            return

        self.submit_button.setEnabled(True)

    def toggle_optional_fields(self):
        # Afficher ou cacher les champs optionnels en fonction de l'état de la checkbox
        is_checked = self.optional_checkbox.isChecked()
        self.rattachement_label.setVisible(is_checked)
        self.rattachement_input.setVisible(is_checked)
        self.nom_rattachement_label.setVisible(is_checked)
        self.nom_rattachement_input.setVisible(is_checked)

    def select_entree_dir(self):
        """
        Ouvre une boîte de dialogue pour sélectionner le répertoire contenant les reportages
        et met à jour le champ correspondant avec le chemin sélectionné.
        """
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire contenant les reportages")
        if directory:
            self.entree_dir_label.setText(directory)

    def select_cible_dir(self):
        """
        Ouvre une boîte de dialogue pour sélectionner le répertoire où sera créé le SIP
        et met à jour le champ correspondant avec le chemin sélectionné.
        """
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire où sera créé le SIP")
        if directory:
            self.cible_dir_label.setText(directory)

    def select_csv_file(self):
        """
        Ouvre une boîte de dialogue pour sélectionner le fichier CSV utilisé comme instrument de recherche,
        et met à jour le champ correspondant avec le chemin du fichier sélectionné.
        """
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner l'instrument de recherche (CSV)", "",
                                              "CSV Files (*.csv)")
        if file:
            self.csv_file_label.setText(file)

    def select_txt_file(self):
        """
        Ouvre une boîte de dialogue pour sélectionner le fichier texte contenant la liste des reportages,
        et met à jour le champ correspondant avec le chemin du fichier sélectionné.
        """
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner la liste des reportages (TXT)", "",
                                              "Text Files (*.txt)")
        if file:
            self.txt_file_label.setText(file)

    def handle_submit(self):
        # Cette fonction est appelée lorsque l'utilisateur clique sur Soumettre
        try:
            formulaire = self.submit()

            archival_agency_archive_unit_identifier = (str(formulaire["Num_entree"]) + "_" +
                                                       str(formulaire["Num_paquet"]) + "_")
            archive_unit_id = archival_agency_archive_unit_identifier

            if formulaire["Rattachement"] is not None:
                rattachement = formulaire["Rattachement"]
            else:
                rattachement = None

            value = formulaire["Versement"]

            selected_directory = formulaire["dir_path"]

            csv_file = formulaire["csv"]
            data_ir = select_csv(csv_file)
            print("Fichier de métadonnées externe sélectionné.")

            liste = formulaire["liste_rp"]
            liste_rp = select_list_rp(liste)
            print("Reportages sélectionnés :", liste_rp)

            cible_dir = formulaire["cible"]
            target_dir = chose_target_dir(cible_dir)
            print("Répertoire cible :", target_dir)

            print("Extraction des métadonnées internes des photos.")
            data_exif = exif_extract(selected_directory, liste_rp, formulaire)
            data_sig = siegfried(selected_directory, liste_rp)
            data = metadata_json(data_sig, data_exif)

            print("Création de l'en-tête du manifest.")
            root = creer_root(value, formulaire)
            print("Création des DataObjectGroup.")
            root = create_dataobjectgroup(root, selected_directory, liste_rp)
            print("Ajout des métadonnées aux DataObjectGroup")
            root = package_metadata(root, data)
            print("Création des éléments ArchiveUnit.")
            arbre = ua_rp(selected_directory, data_ir, root, data, liste_rp, rattachement, formulaire)
            print("Suppression des doublons dans les DataObjectGroup.")
            arbre = delete_duplicate_dog(arbre)
            print("Attribution des identifiants.")
            arbre = id_attrib(arbre, archive_unit_id)
            print("Création de l'élément DescriptiveMetadata.")
            arbre = create_management_metadata(arbre, formulaire)
            print("Ecriture du manifest.")
            arbre_str = minidom.parseString(ET.tostring(arbre, encoding='unicode')).toprettyxml(indent="   ")
            target_manifest = os.path.split(target_dir)
            target_manifest = target_manifest[0]
            target_manifest = os.path.join(target_manifest, "manifest.xml")
            with open(target_manifest, "w", encoding="utf-8") as f:
                f.write(arbre_str)

            print("Copie et renommage des fichiers dans le dossier content.")
            copy(target_dir, arbre, data)
            print("Bravo, le paquet est terminé !")
            input("Appuyez sur Entrée pour fermer l'application.")
            QApplication.instance().quit()  # Quitter l'application PyQt
        except Exception as excep:
            print("error : ", excep)
            input("Appuyez sur Entrée pour fermer l'application.")
            QApplication.instance().quit()  # Quitter l'application PyQt

    def submit(self):
        # Récupérer les valeurs des champs de texte
        entree_dir = self.entree_dir_label.text()
        cible_dir = self.cible_dir_label.text()
        csv_file = self.csv_file_label.text()
        txt_file = self.txt_file_label.text()

        # Vérifier si les champs de rattachement sont vides
        rattachement_value = self.rattachement_input.text().strip()
        nom_rattachement_value = self.nom_rattachement_input.text().strip()

        if rattachement_value or nom_rattachement_value:
            rattachement_data = [rattachement_value if rattachement_value else "N/A",
                                 nom_rattachement_value if nom_rattachement_value else "N/A"]
        else:
            rattachement_data = None

        data = {
            "Num_entree": self.entree_input.text(),
            "Num_paquet": self.paquet_input.text(),
            "Versement": self.versement_input.text(),
            "ArchivalAgency_Identifier": self.archival_agency_identifier_input.text(),
            "TransferringAgency_Identifier": self.transferring_agency_identifier_input.text(),
            "OriginatingAgency_Identifier": self.originating_agency_identifier_input.text(),
            "SubmissionAgency_Identifier": self.submission_agency_identifier_input.text(),
            "ArchivalAgreement": self.archival_agreement_input.text(),
            "AuthorizedAgent_Activity": self.authorized_agent_activity_input.text(),
            "AuthorizedAgent_Mandate": self.authorized_agent_mandate_input.text(),
            "ArchivalProfile": self.archival_profile_input.text(),
            "AcquisitionInformation": self.acquisition_information_input.text(),
            "LegalStatus": self.legal_status_input.currentText(),
            "Champs_metadata": [checkbox.text() for checkbox in self.metadata_checkboxes if checkbox.isChecked()],
            "dir_path": entree_dir,
            "cible": cible_dir,
            "csv": csv_file,
            "liste_rp": txt_file,
            "Rattachement": None
        }

        if rattachement_data is not None:
            data["Rattachement"] = rattachement_data

        self.close()

        return data


def select_list_rp(liste_rp):
    """
    Sélectionne le fichier texte contenant les numéros des reportages à ajouter au SIP.

    :return: list - la liste des numéros des reportages à analyser.
    """
    list_rp = liste_rp
    my_file = open(list_rp, "r")
    data = my_file.read()
    # Fichier texte transformé en liste en transformant chaque retour à la ligne en virgule
    data_into_list = data.replace('\n', ',').split(",")
    return data_into_list


def select_csv(csv_file):
    """
    Sélectionne le csv contenant les métadonnées externes des reportages.

    :return: list[list] - le contenu du csv de métadonnées.
    """
    csv_path = csv_file
    data_ir = []
    with open(csv_path, encoding="utf-8", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data_ir.append(row)
    return data_ir


def chose_target_dir(cible_dir):
    """
    Sélectionne le répertoire où sera créé le SIP.

    :return: str - le chemin du répertoire de destination.
    """
    target_dir = cible_dir
    content = 'content'
    path = os.path.join(target_dir, content)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def exif_extract(dir_path, liste_rp, formulaire):
    """
    Utilise la librairie PyExiftool pour extraire les métadonnées internes des photos.
    :param str dir_path: Le chemin vers le répertoire "racine" contenant les reportages.
    :param list liste_rp: La liste des numéros des reportages à ajouter au SIP.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: List[dict] - une liste de dictionnaires, chaque dictionnaire contenant les métadonnées extraites
    pour un fichier.
    """
    data = []  # Initialisation de la liste qui va contenir les métadonnées extraites
    processed_files = set()  # Pour garder une trace des fichiers déjà traités
    # Utilisation de PyExiftool pour extraire les métadonnées internes des photographies
    with ExifTool(encoding="utf-8") as et:
        for rp in liste_rp:  # Parcours de chaque numéro de reportage dans la liste
            # Si un numéro de reportage de la liste n'est pas identifié dans les noms de dossier, interrompre le script
            if rp.lower() not in str(os.listdir(dir_path)).lower():
                input("ERREUR : Le reportage " + rp + " n'a pas été trouvé dans le répertoire "+dir_path+".")
                sys.exit("ANNULATION")
            for item in os.listdir(dir_path):  # Parcours de chaque élément dans le répertoire racine
                # Vérification si le nom de dossier contient un numéro de reportage
                if (
                        str(rp+" ").lower() in item.lower() or item.lower().endswith(rp.lower()) or
                        str(rp+"_").lower() in item.lower()
                ):
                    item_path = os.path.join(dir_path, item)  # Chemin complet vers le dossier ou fichier
                    # Extraction des métadonnées spécifiques pour les fichiers du dossier
                    exif_data_list = et.execute_json(
                        '-r', '-b', '-FileName', *formulaire["Champs_metadata"], '-Filesize#', item_path
                    )
                    # Vérification si le fichier a déjà été traité pour éviter les doublons
                    if item_path in processed_files:
                        continue  # Passer au prochain fichier si celui-ci a déjà été traité
                        # Si des métadonnées sont extraites, les ajouter à la liste des données
                    if exif_data_list:
                        data.extend(exif_data_list)
                        processed_files.add(item_path)  # Ajouter le fichier à la liste des fichiers traités
    return data  # Retourner la liste des métadonnées extraites pour tous les fichiers concernés


def siegfried(dir_path, liste_rp):
    """
    Utilise l'outil Siegfried pour extraire les métadonnées de format des fichiers.
    :param str dir_path: le chemin vers le répertoire "racine" contenant les reportages.
    :param list liste_rp: la liste des numéros des reportages à analyser.

    :return: list[dict] - une liste de dictionnaires contenant les métadonnées de format des fichiers.
    """
    format_rp = []  # Liste qui va contenir les métadonnées de format des fichiers par reportage
    # Parcours de chaque numéro de reportage dans la liste
    for rp in liste_rp:
        # Parcours de chaque élément (fichier ou dossier) dans le répertoire racine
        for item in os.listdir(dir_path):
            if str(rp+" ").lower() in item.lower() or item.lower().endswith(rp.lower()):
                item_path = os.path.join(dir_path, item)  # Chemin complet vers le dossier ou fichier
                # Appel à Siegfried pour obtenir les métadonnées de format au format JSON
                md_format = subprocess.run(["sf", "-hash", "sha512", "-json", item_path], capture_output=True,
                                           text=True, encoding="utf-8")
                md_format = json.loads(md_format.stdout)  # Conversion de la sortie JSON en dictionnaire Python
                format_rp.append(md_format)  # Ajouter le fichier à la liste des fichiers traités
                # Ajout des métadonnées de format pour ce reportage à la liste

    # Correction des chemins de fichier dans chaque dictionnaire de métadonnées de format
    for rp in format_rp:
        fichiers = rp.get("files", [])   # Récupération de la liste des fichiers dans les métadonnées du reportage
        for file in fichiers:
            # Remplacement des séparateurs de chemin Windows par des slashs
            file["filename"] = file["filename"].replace("\\", "/")

    return format_rp  # Retourne la liste de dictionnaires contenant les métadonnées de format des reportages analysés


def metadata_json(data_sig, data_exif):
    """
    Fusionne les métadonnées des fichiers provenant de deux sources de données.
    :param list data_sig: liste de dictionnaires contenant des métadonnées calculées par Siegfried, chacun avec une clé
    "files" qui est une liste de fichiers.
    :param list data_exif: liste de dictionnaires contenant des métadonnées extraites par Exiftool, chacun avec une clé
    "SourceFile" indiquant le chemin du fichier.

    :return: list[dict] - une nouvelle liste de dictionnaires avec les métadonnées fusionnées pour chaque fichier.
    """
    new_data = []  # Initialisation d'une liste vide pour stocker les données fusionnées

    # Parcours de chaque reportage dans les données de Siegfried
    for rp in data_sig:
        files = rp.get("files", [])  # Récupération de la liste des fichiers pour ce reportage

        # Parcours de chaque fichier dans le reportage
        for file in files:
            filename = file["filename"]  # Extraction du nom du fichier
            # Recherche correspondante dans les métadonnées extraites par Exiftool
            for item in data_exif:
                if item.get("SourceFile") == filename:
                    file.update(item)  # Mise à jour des métadonnées du fichier avec celles de Exiftool

        # Ajout du reportage avec les fichiers fusionnés à la liste finale
        new_data.append({'files': files})

    return new_data  # Retourne une liste de dictionnaires avec les métadonnées fusionnées pour tous les fichiers


def creer_root(value, formulaire):
    """
    Crée l'élément XML racine et l'en-tête du manifest.

    :param str value: La valeur textuelle des balises <Comment> et <Message Identifier>.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: ElementTree Element - l'élément racine XML créé.
    """
    root = ET.Element("ArchiveTransfer")  # Création de l'élément racine XML 'ArchiveTransfer'

    # Définition des espaces de noms et de l'emplacement du schéma XML
    root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    root.set('xmlns:pr', 'info:lc/xmlns/premis-v2')
    root.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'fr:gouv:culture:archivesdefrance:seda:v2.1 seda-2.1-main.xsd')
    root.set('xml:id', 'ID1')   # Attribution de l'identifiant XML 'ID1'

    # Ajout de l'élément 'Comment' avec la valeur spécifiée
    comment = ET.SubElement(root, "Comment")
    comment.text = value
    # Ajout de l'élément 'Date' avec la date du jour de fabrication du SIP
    date = ET.SubElement(root, "Date")
    date.text = date_ajd

    # Ajout de l'élément 'MessageIdentifier' avec la valeur spécifiée
    ET.SubElement(root, "MessageIdentifier").text = value

    # Ajout de l'élément 'ArchivalAgreement' avec sa valeur et ses espaces de noms
    archag = ET.SubElement(root, "ArchivalAgreement")
    archag.text = formulaire["ArchivalAgreement"]
    archag.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    archag.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')

    # Ajout de l'élément 'CodeListVersions' avec ses sous-éléments et leurs valeurs
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

    # Ajout de l'élément 'DataObjectPackage'
    ET.SubElement(root, "DataObjectPackage")

    # Ajout de l'élément 'TransferRequestReplyIdentifier' avec sa valeur
    ET.SubElement(root, "TransferRequestReplyIdentifier").text = "Identifier3"

    # Ajout de l'élément 'ArchivalAgency' avec son identifiant
    archival_agency = ET.SubElement(root, "ArchivalAgency")
    ET.SubElement(archival_agency, "Identifier").text = formulaire["ArchivalAgency_Identifier"]

    # Ajout de l'élément 'TransferringAgency' avec son identifiant et ses espaces de noms
    transferring_agency = ET.SubElement(root, "TransferringAgency")
    transferring_agency.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    transferring_agency.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')
    ET.SubElement(transferring_agency, "Identifier").text = formulaire["TransferringAgency_Identifier"]

    return root  # Retourne l'élément racine XML créé


def create_dataobjectgroup(arbre, directory, liste_rp):
    """
        Crée l'élément <DataObjectPackage> et un élément <DataObjectGroup> pour chaque fichier correspondant aux
        reportages spécifiés.

        :param ElementTree Element arbre: L'élément racine de l'arbre XML.
        :param str directory: Le chemin vers le répertoire racine contenant les dossiers des reportages.
        :param list liste_rp: La liste des numéros des reportages à inclure dans le SIP.

        :return: ElementTree Element - l'élément racine XML mis à jour avec les groupes d'objets techniques ajoutés.
        """
    root = arbre  # Utilisation de l'arbre XML passé en paramètre comme racine

    # Recherche de l'élément DataObjectPackage dans l'arbre XML
    data_object_package = root.find("DataObjectPackage")

    # Parcours récursif de tous les fichiers et répertoires dans le répertoire spécifié
    for dirpath, dirnames, filenames in os.walk(directory):
        # Remplacement des antislashs pour compatibilité avec les chemins
        dirpath = dirpath.replace("\\", "/")
        for item in filenames:
            item = dirpath + "/" + item  # Chemin complet du fichier
            for num in liste_rp:
                # Vérification si le numéro de reportage est dans le chemin du fichier
                if str(num+" ").lower() in item.lower() or str(num+"/").lower() in item.lower():
                    # Exclusions de certains fichiers non pertinents (fichiers système ou masqués)
                    if (
                            "DS_Store" not in item and "Thumbs" not in item and "BridgeSort" not in item and
                            "PM_lock" not in item and "desktop.ini" not in item and
                            "._" not in item and "/." not in item
                    ):
                        # Création de l'élément DataObjectGroup sous DataObjectPackage et de ses descendants
                        data_object_group = ET.SubElement(data_object_package, "DataObjectGroup")
                        binary_data_object = ET.SubElement(data_object_group, "BinaryDataObject")
                        ET.SubElement(binary_data_object, "DataObjectVersion").text = "BinaryMaster_1"
                        ET.SubElement(binary_data_object, "Uri")
                        message_digest = ET.SubElement(binary_data_object, "MessageDigest")
                        message_digest.set("algorithm", "SHA-512")
                        ET.SubElement(binary_data_object, "Size")
                        format_identification = ET.SubElement(binary_data_object, "FormatIdentification")
                        ET.SubElement(format_identification, "FormatLitteral")
                        file_info = ET.SubElement(binary_data_object, "FileInfo")
                        filename = ET.SubElement(file_info, "Filename")
                        filename.text = item  # Création de l'élément Filename avec pour valeur le nom du fichier
                        ET.SubElement(file_info, "LastModified")

    return root  # Retourne l'élément racine XML mis à jour avec les nouveaux groupes d'objets de données


def package_metadata(arbre, data):
    """
    Complète les métadonnées des objets techniques dans l'arbre XML avec les informations fournies dans data.

    :param xml.etree.ElementTree.Element arbre: l'élément racine de l'arbre XML à mettre à jour.
    :param list[dict] data: une liste de dictionnaires contenant les métadonnées des fichiers (fusion des exports
    Siegfried et Exiftool).

    :return: xml.etree.ElementTree.Element - l'élément racine XML mis à jour avec les métadonnées des objets techniques.
    """
    root = arbre  # Utilisation de l'arbre XML passé en paramètre comme racine

    # Recherche de l'élément DataObjectPackage dans l'arbre XML
    data_object_package = root.find("DataObjectPackage")

    # Recherche de tous les éléments BinaryDataObject sous DataObjectPackage
    binary_data_object = data_object_package.findall(".//BinaryDataObject")

    # Parcours de chaque BinaryDataObject
    for obj in binary_data_object:
        item = obj.find(".//Filename").text  # Récupération du nom de fichier

        # Parcours des données fournies (fusion des exports Siegfried et Exiftool)
        for rp in data:
            files = rp.get("files", [])  # Récupération des fichiers et leurs métadonnées
            for file in files:
                if file.get("filename") == item:  # Vérification si le fichier correspond à l'objet actuel
                    # Mise à jour des métadonnées dans l'élément XML
                    if file.get("File:FileSize"):
                        filesize = obj.find("Size")
                        filesize.text = str(file["File:FileSize"])  # Mise à jour de la taille du fichier

                    if file.get("File:FileModifyDate"):
                        last_modified = obj.find(".//LastModified")
                        modif_date = file.get("File:FileModifyDate")  # Récupération de la date de dernière modification
                        # Extraction de la date au format attendu
                        match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(\\.\d+)?([-+]\d{2}:\d{2})?",
                                         modif_date)
                        if match:
                            modif_date = match.group(1)
                            # Conversion de la date en format ISO 8601
                            modif_date = datetime.strptime(modif_date, "%Y:%m:%d %H:%M:%S")
                            modif_date = modif_date.strftime("%Y-%m-%dT%H:%M:%S")
                            last_modified.text = modif_date

                    # Mise à jour du nom de fichier
                    file_name = obj.find(".//Filename")
                    file_name.text = file.get("File:FileName")

                    # Mise à jour des éléments d'identification du format
                    message_digest = obj.find("MessageDigest")
                    message_digest.text = file.get("sha512")
                    format_identification = obj.find("FormatIdentification")
                    format_litteral = format_identification.find("FormatLitteral")
                    for i in file.get("matches"):
                        format_litteral.text = i["format"]  # Mise à jour du format littéral
                        if i["mime"]:
                            ET.SubElement(format_identification, "MimeType").text = i["mime"]  # Ajout du type mime
                        formatid = ET.SubElement(format_identification, "FormatId")
                        formatid.text = i["id"]  # Mise à jour de l'ID de format

    return root  # Retourne l'élément racine XML mis à jour avec les métadonnées des objets techniques


def ua_rp(directory, data_ir, arbre_rp, data, liste_rp, rattachement, formulaire):
    """
    Crée des unités d'archive pour chaque reportage et appelle la fonction sub_unit() pour les UA de niveau inférieur,
    puis les ajoute à l'arbre XML.

    :param str directory: Le chemin du répertoire contenant les reportages.
    :param list[list] data_ir: Une liste de liste, chacune contenant les métadonnées externes d'un reportage.
    :param xml.etree.ElementTree.Element arbre_rp: L'arbre XML mis à jour.
    :param list[dict] data: Une liste de dictionnaires contenant les métadonnées des fichiers (fusion des exports
    Siegfried et Exiftool).
    :param list liste_rp: Une liste des numéros des reportages à ajouter au SIP.
    :param list rattachement: Une liste contenant les informations de rattachement, ou None.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: ElementTree Element - l'élément racine XML mis à jour.
    """
    root = arbre_rp  # Utilisation de l'arbre XML passé en paramètre comme racine
    data_object_package = root.find("DataObjectPackage")  # Recherche de l'élément DataObjectPackage

    # Création de l'élément DescriptiveMetadata sous DataObjectPackage s'il n'existe pas déjà
    descriptive_metadata = ET.SubElement(data_object_package, "DescriptiveMetadata")
    if rattachement is not None:
        # Si des informations de rattachement sont fournies, créer une unité d'archive "fantôme"
        ua_ghost = ET.Element("ArchiveUnit")  # Création de l'élément ArchiveUnit
        management = ET.SubElement(ua_ghost, "Management")  # Sous-élément Management de ArchiveUnit
        update_operation = ET.SubElement(management, "UpdateOperation")  # Sous-élément UpdateOperation de Management
        archive_unit_identifier_key = ET.SubElement(update_operation, "ArchiveUnitIdentifierKey")
        metadata_name = ET.SubElement(archive_unit_identifier_key, "MetadataName")
        metadata_name.text = "ArchivalAgencyArchiveUnitIdentifier"  # Valeur de MetadataName
        metadata_value = ET.SubElement(archive_unit_identifier_key, "MetadataValue")
        metadata_value.text = rattachement[0]  # Valeur de MetadataValue issue de la liste "rattachement"
        content_ghost = ET.SubElement(ua_ghost, "Content")  # Sous-élément Content de ArchiveUnit
        ET.SubElement(content_ghost, "DescriptionLevel").text = "RecordGrp"  # Valeur de DescriptionLevel
        title_ghost = ET.SubElement(content_ghost, "Title")
        title_ghost.text = rattachement[1]  # Valeur de Title issue de la liste "rattachement"

        # Parcours des fichiers dans le répertoire spécifié
        for num in liste_rp:
            for item in os.listdir(directory):
                for RP in data_ir:
                    if num == RP[0]:
                        if (
                                str(num+" ").lower() in item.lower() or item.lower().endswith(num.lower()) or
                                str(num+"_").lower() in item.lower()
                        ):
                            item_path = os.path.join(directory, item)
                            if os.path.isdir(item_path):
                                # Création d'une nouvelle unité d'archive pour chaque reportage
                                archiveunitrp = ET.SubElement(ua_ghost, "ArchiveUnit")
                                contentrp = ET.SubElement(archiveunitrp, "Content")
                                ET.SubElement(contentrp, "DescriptionLevel").text = "RecordGrp"
                                titlerp = ET.SubElement(contentrp, "Title")
                                titlerp.text = RP[1]  # Titre du reportage issu du csv de métadonnées externes
                                ET.SubElement(contentrp, "ArchivalAgencyArchiveUnitIdentifier")
                                numrp = ET.SubElement(contentrp, "OriginatingAgencyArchiveUnitIdentifier")
                                numrp.text = RP[0]  # Identifiant du reportage issu du csv de métadonnées externes
                                if len(RP) > 4:
                                    if RP[4]:
                                        cote = ET.SubElement(contentrp, "TransferringAgencyArchiveUnitIdentifier")
                                        cote.text = RP[4]
                                description = ET.SubElement(contentrp, "Description")
                                # Numéro du reportage en description (pour indexation dans le SAE)
                                description.text = str("Reportage n°"+RP[0])
                                # Identifiant du service producteur et versant
                                originating_agency = ET.SubElement(contentrp, "OriginatingAgency")
                                ET.SubElement(originating_agency, "Identifier").text = (
                                    formulaire)["OriginatingAgency_Identifier"]
                                submission_agency = ET.SubElement(contentrp, "SubmissionAgency")
                                ET.SubElement(submission_agency, "Identifier").text = (
                                    formulaire)["SubmissionAgency_Identifier"]
                                startdate = ET.SubElement(contentrp, "StartDate")
                                if RP[2] is not None:
                                    dtd = datetime.strptime(RP[2], "%d.%m.%Y")
                                    dtd = dtd.strftime("%Y-%m-%dT%H:%M:%S")
                                    startdate.text = dtd  # Date de début du reportage issue du csv
                                else:
                                    startdate.text = "0000-00-00T00:00:00"
                                enddate = ET.SubElement(contentrp, "EndDate")
                                if RP[3] is not None:
                                    dtf = datetime.strptime(RP[3], "%d.%m.%Y")
                                    dtf = dtf.strftime("%Y-%m-%dT%H:%M:%S")
                                    enddate.text = dtf  # Date de fin du reportage issue du csv de métadonnées externes
                                else:
                                    enddate.text = "0000-00-00T00:00:00"

                                # Appel à la fonction sub_unit pour les sous-unités d'archive
                                archiveunitchild = sub_unit(item_path, data, data_ir, liste_rp, formulaire)
                                for child in archiveunitchild:
                                    # Ajout des sous-unités d'archive à l'unité d'archive parente
                                    archiveunitrp.append(child)

        descriptive_metadata.append(ua_ghost)  # Ajout de l'unité d'archive "fantôme" à DescriptiveMetadata

    else:
        # Si aucune information de rattachement n'est fournie, procéder de manière similaire sans UA "fantôme"
        for num in liste_rp:
            for item in os.listdir(directory):
                for RP in data_ir:
                    if num == RP[0]:
                        if (
                                str(num+" ").lower() in item.lower() or item.lower().endswith(num.lower()) or
                                str(num+"_").lower() in item.lower()
                        ):
                            print(item)  # Affichage du nom du fichier pour vérification
                            item_path = os.path.join(directory, item)
                            if os.path.isdir(item_path):
                                # Création d'une nouvelle unité d'archive pour chaque reportage
                                archiveunitrp = ET.Element("ArchiveUnit")
                                contentrp = ET.SubElement(archiveunitrp, "Content")
                                ET.SubElement(contentrp, "DescriptionLevel").text = "RecordGrp"
                                titlerp = ET.SubElement(contentrp, "Title")
                                titlerp.text = RP[1]  # Titre du reportage issu du csv de métadonnées externes
                                ET.SubElement(contentrp, "ArchivalAgencyArchiveUnitIdentifier")
                                numrp = ET.SubElement(contentrp, "OriginatingAgencyArchiveUnitIdentifier")
                                numrp.text = RP[0]  # Identifiant du reportage issu du csv de métadonnées externes
                                if len(RP) > 4:
                                    if RP[4]:
                                        cote = ET.SubElement(contentrp, "TransferringAgencyArchiveUnitIdentifier")
                                        cote.text = RP[4]
                                description = ET.SubElement(contentrp, "Description")
                                # Numéro du reportage en description (pour indexation dans le SAE)
                                description.text = str("Reportage n°"+RP[0])
                                # Identifiant du service producteur et versant
                                originating_agency = ET.SubElement(contentrp, "OriginatingAgency")
                                ET.SubElement(originating_agency, "Identifier").text = (
                                    formulaire)["OriginatingAgency_Identifier"]
                                submission_agency = ET.SubElement(contentrp, "SubmissionAgency")
                                ET.SubElement(submission_agency, "Identifier").text = (
                                    formulaire)["SubmissionAgency_Identifier"]
                                startdate = ET.SubElement(contentrp, "StartDate")
                                if RP[2] is not None:
                                    dtd = datetime.strptime(RP[2], "%d.%m.%Y")
                                    dtd = dtd.strftime("%Y-%m-%dT%H:%M:%S")
                                    startdate.text = dtd  # Date de début du reportage issue du csv
                                else:
                                    startdate.text = "0000-00-00T00:00:00"
                                enddate = ET.SubElement(contentrp, "EndDate")
                                if RP[3] is not None:
                                    dtf = datetime.strptime(RP[3], "%d.%m.%Y")
                                    dtf = dtf.strftime("%Y-%m-%dT%H:%M:%S")
                                    enddate.text = dtf  # Date de fin du reportage issue du csv de métadonnées externes
                                else:
                                    enddate.text = "0000-00-00T00:00:00"

                                # Appel à la fonction sub_unit pour les sous-unités d'archive
                                archiveunitchild = sub_unit(item_path, data, data_ir, liste_rp, formulaire)
                                for child in archiveunitchild:
                                    archiveunitrp.append(child)
                                # Ajout des sous-unités d'archive à l'unité d'archive parente

                                # Ajout de l'unité d'archive à DescriptiveMetadata
                                descriptive_metadata.append(archiveunitrp)

    return root  # Retour de l'arbre XML mis à jour avec les unités d'archive


def sub_unit(directory, data, data_ir, liste_rp, formulaire, parent=None):
    """
    Crée des unités d'archive pour les fichiers en appelant la fonction et sous-répertoires dans le répertoire spécifié,
    et les ajoute à l'unité d'archive parent.

    :param str directory: le chemin du répertoire contenant les fichiers et sous-répertoires.
    :param list[dict] data: une liste de dictionnaires contenant les métadonnées des fichiers (fusion des exports
    Siegfried et Exiftool).
    :param list[list] data_ir: une liste de liste, chacune contenant les métadonnées externes d'un reportage.
    :param list liste_rp: une liste des numéros des reportages à traiter.
    :param xml.etree.ElementTree.Element parent: l'unité d'archive parent à laquelle ajouter les sous-unités, ou None
    pour créer une nouvelle unité d'archive racine.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: list - une liste des sous-unités d'archive
    """
    if parent is None:
        archiveunit = ET.Element("ArchiveUnit")  # Création de l'élément ArchiveUnit
    else:
        archiveunit = parent

    # Parcours des éléments (fichiers et sous-répertoires) dans le répertoire spécifié
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path):
            if item.startswith('.'):
                pass
            else:
                # Si l'élément est un répertoire, créer une sous-unité d'archive
                sub_archive_unit = ET.SubElement(archiveunit, "ArchiveUnit")
                contentsub = create_archive_unit_dir(item, formulaire)
                sub_archive_unit.append(contentsub)
                # Appel récursif de la fonction pour traiter les sous-répertoires
                sub_unit(item_path, data, data_ir, liste_rp, formulaire, sub_archive_unit)

        elif (
                os.path.isfile(item_path) and "DS_Store" not in item and "Thumbs" not in item and
                "BridgeSort" not in item and "desktop.ini" not in item
        ):
            # Si l'élément est un fichier valide (et non un fichier système)
            if item.startswith('.'):
                pass
            else:
                file_unit = create_archive_unit_file(item, data, item_path, formulaire)
                archiveunit.append(file_unit)  # Ajout de l'unité d'archive du fichier à l'unité d'archive parent

    # Si aucune unité d'archive parente n'a été fournie, retourne les sous-unités d'archive créées
    if parent is None:
        au_child = archiveunit.findall("./ArchiveUnit")
        return au_child


def create_archive_unit_dir(title_dir, formulaire):
    """
    Crée le contenu d'une unité d'archive pour un répertoire.

    :param str title_dir: Le titre du répertoire à utiliser comme titre de l'unité d'archive.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: ElementTree Element - un élément XML représentant le contenu de l'unité d'archive pour le
    répertoire.
    """
    # Création d'un élément Content contenant les métadonnées relatives au sous-dossier
    contentdir = ET.Element("Content")
    ET.SubElement(contentdir, "DescriptionLevel").text = "RecordGrp"
    title_element = ET.SubElement(contentdir, "Title")
    title_element.text = title_dir  # Titre du sous-dossier
    ET.SubElement(contentdir, "ArchivalAgencyArchiveUnitIdentifier")
    originating_agency = ET.SubElement(contentdir, "OriginatingAgency")
    ET.SubElement(originating_agency, "Identifier").text = (
        formulaire)["OriginatingAgency_Identifier"]  # Identifiant du service producteur
    submission_agency = ET.SubElement(contentdir, "SubmissionAgency")
    ET.SubElement(submission_agency, "Identifier").text = (
        formulaire)["SubmissionAgency_Identifier"]  # Identifiant du service versant

    return contentdir  # Retourner le Content créé pour l'ajouter à l'UA correspondante, crée par la fonction sub_unit()


def create_archive_unit_file(title_file, data, item_path, formulaire):
    """
    Crée un élément ArchiveUnit pour représenter les métadonnées d'un fichier.

    :param str title_file: Le nom du fichier.
    :param list[dict] data: une liste de dictionnaires contenant les métadonnées des fichiers (fusion des exports
    Siegfried et Exiftool).
    :param str item_path: Le chemin complet du fichier.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: xml.etree.ElementTree.Element - L'élément XML ArchiveUnit et ses descendants, contenant les métadonnées du
    fichier.
    """
    # Remplace les backslashes par des slashes dans le chemin du fichier (pour compatibilité système)
    item_path = item_path.replace("\\", "/")

    # Crée l'élément principal ArchiveUnit
    arch_unit_item = ET.Element("ArchiveUnit")
    # Crée le sous-élément Content
    contentit = ET.SubElement(arch_unit_item, "Content")
    # Ajoute le niveau de description de l'élément
    ET.SubElement(contentit, "DescriptionLevel").text = "Item"
    # Ajoute le titre du fichier
    title_element = ET.SubElement(contentit, "Title")
    title_element.text = title_file
    # Ajoute un identifiant d'archive (complété plus tard)
    ET.SubElement(contentit, "ArchivalAgencyArchiveUnitIdentifier")

    # Parcourt les métadonnées fournies pour trouver celles correspondant au fichier actuel
    for item in data:
        files = item.get("files", [])
        for file in files:
            sourcefile = file.get("SourceFile")
            if sourcefile == item_path:
                # Ajoute les métadonnées spécifiques au fichier si elles n'existent pas déjà dans l'élément
                if contentit.find("BaliseTemp") is None:
                    # Ajout d'un élément temporaire BaliseTemp qui permettra d'identifier les doublons techniques
                    temp_hash = ET.SubElement(contentit, "BaliseTemp")
                    temp_hash.text = file.get("sha512")

                # Ajout d'un élément Description si une description existe dans les métadonnées internes du fichier
                if contentit.find("Description") is None:
                    if file.get("IPTC:Caption-Abstract"):
                        description = ET.SubElement(contentit, "Description")
                        description.text = file.get("IPTC:Caption-Abstract")
                    else:
                        if file.get("XMP:Description"):
                            description = ET.SubElement(contentit, "Description")
                            description.text = file.get("XMP:Description")
                        else:
                            pass

                # Ajout d'éléments Tag si des mots-clés sont présents dans les métadonnées internes du fichier
                if contentit.find("Tag") is None:
                    # Chercher en priorité les mots-clés issus du champs XMP Subject
                    if file.get("XMP:Subject"):
                        # S'il n'y a qu'un seul mot-clé, créer un élément Tag
                        if not isinstance(file.get("XMP:Subject"), list):
                            tagit = ET.SubElement(contentit, "Tag")
                            tagit.text = str(file.get("XMP:Subject"))
                        else:
                            # S'il y a une liste de mots-clés, créer un élément par mot-clé de la liste
                            for tag in file.get("XMP:Subject"):
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = str(tag)
                    else:
                        # Si le champ XMP Subject est vide, chercher des mots-clés dans le champ IPTC Keywords
                        if file.get("IPTC:Keywords"):
                            # S'il n'y a qu'un seul mot-clé, créer un élément Tag
                            if not isinstance(file.get("IPTC:Keywords"), list):
                                tagit = ET.SubElement(contentit, "Tag")
                                tagit.text = str(file.get("IPTC:Keywords"))
                            else:
                                # S'il y a une liste de mots-clés, créer un élément par mot-clé de la liste
                                for tag in file.get("IPTC:Keywords"):
                                    tagit = ET.SubElement(contentit, "Tag")
                                    tagit.text = str(tag)
                        else:
                            pass

                # Ajout d'éléments Coverage si des informations de localisation sont présentes
                if contentit.find("Coverage") is None:
                    # Chercher si des champs de localisation sont renseignés dans les métadonnées internes du fichier
                    if file.get("XMP:Country" or "IPTC:Country-PrimaryLocationName" or "XMP:City" or "IPTC:City"):
                        # Créer un élément Coverage
                        cov = ET.SubElement(contentit, "Coverage")
                        # Chercher en priorité des informations de localisation sur le pays dans le champ XMP Country
                        if file.get("XMP:Country"):
                            # Créer l'élément Spatial ayant pour valeur la métadonnée de lieu du pays
                            spatial_pays = ET.SubElement(cov, "Spatial")
                            spatial_pays.text = file.get("XMP:Country")
                        else:
                            # Si le champ XMP Country est vide, chercher le pays dans le champ IPTC équivalent
                            if file.get("IPTC:Country-PrimaryLocationName"):
                                # Créer l'élément Spatial ayant pour valeur la métadonnée de lieu du pays
                                spatial_pays = ET.SubElement(cov, "Spatial")
                                spatial_pays.text = file.get("IPTC:Country-PrimaryLocationName")
                            else:
                                pass
                        # Chercher en priorité des informations de localisation sur la ville dans le champ XMP City
                        if file.get("XMP:City"):
                            # Créer l'élément Spatial ayant pour valeur la métadonnée de lieu de la ville
                            spatial_ville = ET.SubElement(cov, "Spatial")
                            spatial_ville.text = file.get("XMP:City")
                        else:
                            # Si le champ XMP City est vide, chercher le pays dans le champ IPTC City
                            if file.get("IPTC:City"):
                                # Créer l'élément Spatial ayant pour valeur la métadonnée de lieu de la ville
                                spatial_ville = ET.SubElement(cov, "Spatial")
                                spatial_ville.text = file.get("IPTC:City")
                            else:
                                pass
                    else:
                        pass

                # Créer un élément OriginatingAgency contenant l'identifiant du service producteur
                if contentit.find("OriginatingAgency") is None:
                    originating_agency = ET.SubElement(contentit, "OriginatingAgency")
                    ET.SubElement(originating_agency, "Identifier").text = (
                        formulaire)["OriginatingAgency_Identifier"]

                # Créer un élément SubmissionAgency contenant l'identifiant du service versant
                if contentit.find("SubmissionAgency") is None:
                    submission_agency = ET.SubElement(contentit, "SubmissionAgency")
                    ET.SubElement(submission_agency, "Identifier").text = (
                        formulaire)["SubmissionAgency_Identifier"]

                # Ajout d'éléments AuthorizedAgent si le nom du photographe est présent dans les métadonnées du fichier
                if contentit.find("AuthorizedAgent") is None:
                    # Chercher en priorité le nom du photographe dans le champ IPTC By-line
                    if file.get("IPTC:By-line"):
                        authorized_agent = ET.SubElement(contentit, "AuthorizedAgent")
                        # Créer l'élément FullName contenant le nom du photographe issu du champ IPTC By-line
                        fullname = ET.SubElement(authorized_agent, "FullName")
                        fullname.text = file.get("IPTC:By-line")
                        # Créer les éléments Activity et Mandate avec leurs valeurs respectives
                        ET.SubElement(authorized_agent, "Activity").text = formulaire["AuthorizedAgent_Activity"]
                        ET.SubElement(authorized_agent, "Mandate").text = formulaire["AuthorizedAgent_Mandate"]
                    else:
                        # Si le champ IPTC By-line est vide, chercher le pays dans le champ EXIF Artist
                        if file.get("EXIF:Artist"):
                            authorized_agent = ET.SubElement(contentit, "AuthorizedAgent")
                            # Créer l'élément FullName contenant le nom du photographe issu du champ EXIF Artist
                            fullname = ET.SubElement(authorized_agent, "FullName")
                            fullname.text = file.get("EXIF:Artist")
                            # Créer les éléments Activity et Mandate avec leurs valeurs respectives
                            ET.SubElement(authorized_agent, "Activity").text = (
                                formulaire)["AuthorizedAgent_Activity"]
                            ET.SubElement(authorized_agent, "Mandate").text = (
                                formulaire)["AuthorizedAgent_Mandate"]
                        else:
                            if file.get("XMP:Creator"):
                                authorized_agent = ET.SubElement(contentit, "AuthorizedAgent")
                                # Créer l'élément FullName contenant le nom du photographe issu du champ EXIF Artist
                                fullname = ET.SubElement(authorized_agent, "FullName")
                                fullname.text = file.get("XMP:Creator")
                                # Créer les éléments Activity et Mandate avec leurs valeurs respectives
                                ET.SubElement(authorized_agent, "Activity").text = (
                                    formulaire)["AuthorizedAgent_Activity"]
                                ET.SubElement(authorized_agent, "Mandate").text = (
                                    formulaire)["AuthorizedAgent_Mandate"]
                            else:
                                pass

                # Ajout d'éléments StartDate et EndDate si des métadonnées de date sont présentes dans le fichier
                if contentit.find("StartDate") is None:
                    # Chercher en priorité la date dans le champ XMP CreateDate
                    if file.get("XMP:CreateDate"):
                        createdate = file.get("XMP:CreateDate")
                        # Si la date ne comporte pas de champ "secondes", en créer un avec une valeur fixe de "00"
                        if len(createdate) == 16:
                            createdate += ":00"
                        else:
                            createdate = createdate
                        # Expression régulière pour isoler les éléments de date qu'on souhaite récupérer
                        match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(\.\d+)?([-+]\d{2}:\d{2})?",
                                         createdate)
                        if match:
                            # Match sur le groupe 1 de l'expression régulière
                            createdate = match.group(1)
                            # Définition du format de date actuel
                            createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                            # Transformation vers le format de date souhaité
                            createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                            # Création des éléments StartDate et EndDate avec pour valeur la date modifiée
                            startdateit = ET.SubElement(contentit, "StartDate")
                            startdateit.text = createdate
                            enddateit = ET.SubElement(contentit, "EndDate")
                            enddateit.text = createdate
                        else:
                            pass
                    else:
                        # Si le champ XMP CreateDate est vide, chercher la date dans le champ EXIF CreateDate
                        if file.get("EXIF:CreateDate"):
                            createdate = file.get("EXIF:CreateDate")
                            # Si la date ne comporte pas de champ "secondes", en créer un avec une valeur fixe de "00"
                            if len(createdate) == 16:
                                createdate += ":00"
                            else:
                                createdate = createdate
                            # Expression régulière pour isoler les éléments de date qu'on souhaite récupérer
                            match = re.match(r"(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})(\.\d+)?([-+]\d{2}:\d{2})?",
                                             createdate)
                            if match:
                                # Match sur le groupe 1 de l'expression régulière
                                createdate = match.group(1)
                                # Définition du format de date actuel
                                createdate = datetime.strptime(createdate, "%Y:%m:%d %H:%M:%S")
                                # Transformation vers le format de date souhaité
                                createdate = createdate.strftime("%Y-%m-%dT%H:%M:%S")
                                # Création des éléments StartDate et EndDate avec pour valeur la date modifiée
                                startdateit = ET.SubElement(contentit, "StartDate")
                                startdateit.text = createdate
                                enddateit = ET.SubElement(contentit, "EndDate")
                                enddateit.text = createdate
                            else:
                                pass
                        else:
                            pass

    # Création de l'élément DataObjectReference (complété plus tard)
    data_object_reference = ET.SubElement(arch_unit_item, "DataObjectReference")
    ET.SubElement(data_object_reference, "DataObjectGroupReferenceId")

    return arch_unit_item  # Retourner l'élément ArchiveUnit créé


def delete_duplicate_dog(arbre):
    """
    Supprime les groupes DataObjectGroup qui sont des doublons techniques d'autres DataObjectGroup.

    :param xml.etree.ElementTree.Element arbre: L'arbre xml à mettre à jour.

    :return: xml.etree.ElementTree.Element - L'arbre XML modifié avec les doublons supprimés.
    """
    # Dictionnaire pour stocker les objets uniques par leur empreinte et nom de fichier
    objets_uniques = {}
    # Liste pour stocker les objets à supprimer
    objects_a_supprimer = []

    # Trouve l'élément DataObjectPackage dans l'arbre
    data_object_package = arbre.find(".//DataObjectPackage")

    # Parcourt tous les DataObjectGroup dans le DataObjectPackage
    for data_object_group in data_object_package.findall("DataObjectGroup"):
        # Trouve l'élément BinaryDataObject dans le DataObjectGroup
        binary_data_object = data_object_group.find("BinaryDataObject")
        # Extrait le texte de l'élément MessageDigest
        message_digest = binary_data_object.find("MessageDigest").text

        objet = message_digest

        # Vérifie si cet objet est déjà dans objets_uniques
        if objet in objets_uniques:
            # Si oui, ajoute le DataObjectGroup actuel à la liste des objets à supprimer
            objects_a_supprimer.append((data_object_group, data_object_package))
        else:
            # Sinon, ajoute cet objet au dictionnaire des objets uniques
            objets_uniques[objet] = data_object_group

    # Supprime tous les DataObjectGroup marqués comme doublons
    for element, parent in objects_a_supprimer:
        parent.remove(element)

    return arbre  # Retourner l'arbre modifié


def id_attrib(arbre, archive_unit_id):
    """
    Ajoute les attributs 'id' et met à jour les références entre les ArchiveUnits et les DataObjectGroup.

    :param xml.etree.ElementTree.Element arbre: L'arbre XML à mettre à jour.
    :param str archive_unit_id: Le numéro d'entrée du SIP, utilisé pour la génération des identifiants.

    :return: xml.etree.ElementTree.Element - L'arbre XML avec les identifiants et les références mis à jour.
    """
    # Racine de l'arbre XML
    root = arbre
    # Trouve l'élément DataObjectPackage dans l'arbre
    data_object_package = root.find("DataObjectPackage")
    # Trouve tous les éléments DataObjectGroup dans DataObjectPackage
    data_object_group = data_object_package.findall(".//DataObjectGroup")
    # Trouve l'élément DescriptiveMetadata dans DataObjectPackage
    descriptive_metadata = data_object_package.find("DescriptiveMetadata")
    # Trouve tous les éléments ArchiveUnit dans DescriptiveMetadata
    aus = descriptive_metadata.findall(".//ArchiveUnit")

    # Initialisation du compteur d'identifiants pour ArchiveUnit
    id_au = 0

    # Parcourt tous les ArchiveUnits trouvés
    for au in aus:
        # Incrémente le compteur d'identifiants
        id_au = id_au+1
        # Assigne un attribut 'id' unique à chaque ArchiveUnit
        au.set("id", "AU"+str(id_au))

        # Trouve les éléments DataObjectGroupReferenceId et ArchivalAgencyArchiveUnitIdentifier dans ArchiveUnit
        data_object_group_ref_id = au.find(".//DataObjectGroupReferenceId")
        archival_agency_archive_unit_identifier = au.find(".//ArchivalAgencyArchiveUnitIdentifier")

        # Met à jour le texte de l'élément ArchivalAgencyArchiveUnitIdentifier
        archival_agency_archive_unit_identifier.text = archive_unit_id+str(id_au)

        # Vérifie si le niveau de description est 'Item' pour n'itérer que sur les UA de fichiers
        if au.find(".//DescriptionLevel").text == "Item":
            # Trouve le hash temporaire dans BaliseTemp
            temp_hash = au.find(".//BaliseTemp").text
            got = 0

            # Parcourt tous les DataObjectGroup
            for obj in data_object_group:
                got = got + 1
                # Assigne des attributs 'id' uniques à chaque DataObjectGroup et son BinaryDataObject
                obj.set('id', 'GOT' + str(got))
                binary_data_object = obj.find("BinaryDataObject")
                binary_data_object.set('id', 'BDO'+str(got))

                # Met à jour l'URI dans BinaryDataObject
                myid = binary_data_object.attrib['id']
                uri = binary_data_object.find("Uri")
                filename = obj.find(".//Filename").text
                uri.text = 'content/' + myid + "." + filename.split('.')[-1]

                # Vérifie si le MessageDigest correspond au hash temporaire
                message_digest = obj.find(".//MessageDigest").text
                obj_id = obj.attrib['id']
                if temp_hash == message_digest:
                    # Met à jour DataObjectGroupReferenceId avec l'identifiant du DataObjectGroup correspondant
                    data_object_group_ref_id.text = obj_id

    return root  # Retourner l'arbre modifié


def create_management_metadata(arbre, formulaire):
    """
    Crée et ajoute les métadonnées de gestion relatives au SIP.

    :param xml.etree.ElementTree.Element arbre: L'arbre XML à mettre à jour.
    :param dict formulaire: Formulaire contenant les informations saisies par l'utilisateur.

    :return: xml.etree.ElementTree.Element - L'arbre XML avec les métadonnées descriptives ajoutées ou mises à jour.
    """
    # Racine de l'arbre XML
    root = arbre

    # Trouve l'élément DataObjectPackage dans l'arbre
    data_object_package = root.find("DataObjectPackage")

    # Crée un nouvel élément ManagementMetadata sous DataObjectPackage
    management_metadata = ET.SubElement(data_object_package, "ManagementMetadata")

    # Ajoute les attributs XMLNS à ManagementMetadata
    management_metadata.set('xmlns', 'fr:gouv:culture:archivesdefrance:seda:v2.1')
    management_metadata.set('xmlns:ns2', 'http://www.w3.org/1999/xlink')

    # Ajoute des sous-éléments avec des valeurs de texte prédéfinies
    ET.SubElement(management_metadata, "ArchivalProfile").text = formulaire["ArchivalProfile"]
    ET.SubElement(management_metadata, "AcquisitionInformation").text = formulaire["AcquisitionInformation"]
    ET.SubElement(management_metadata, "LegalStatus").text = formulaire["LegalStatus"]
    ET.SubElement(management_metadata, "OriginatingAgencyIdentifier").text = (
        formulaire)["OriginatingAgency_Identifier"]
    ET.SubElement(management_metadata, "SubmissionAgencyIdentifier").text = (
        formulaire)["SubmissionAgency_Identifier"]

    # Trouve l'élément DescriptiveMetadata dans DataObjectPackage
    descriptive_metadata = data_object_package.find("DescriptiveMetadata")

    # Trouve tous les éléments ArchiveUnit dans DescriptiveMetadata
    aus = descriptive_metadata.findall(".//ArchiveUnit")

    # Parcourt tous les ArchiveUnits trouvés
    for au in aus:
        # Trouve l'élément Content dans chaque ArchiveUnit
        content = au.find("Content")

        # Si l'élément BaliseTemp existe dans Content, le supprime
        if content.find("BaliseTemp") is not None:
            temp_hash = content.find("BaliseTemp")
            content.remove(temp_hash)
        else:
            pass
    return root  # Retourner l'arbre modifié


def copy(target_dir, arbre, data):
    """
    Copie les fichiers correspondant aux objets du paquet d'archives vers un répertoire cible, en utilisant
    les données de hachage SHA-512 pour identifier les fichiers correspondants.

    :param str target_dir: Le répertoire cible où les fichiers doivent être copiés.
    :param xml.etree.ElementTree.Element arbre: L'élément racine de l'arbre XML représentant le paquet d'archives.
    :param list[dict] data: une liste de dictionnaires contenant les métadonnées des fichiers (fusion des exports
    Siegfried et Exiftool).

    :return: None.
    """
    # Racine de l'arbre XML
    root = arbre

    # Trouve l'élément DataObjectPackage dans l'arbre
    data_object_package = root.find("DataObjectPackage")

    # Trouve tous les éléments DataObjectGroup dans DataObjectPackage
    data_object_group = data_object_package.findall("DataObjectGroup")

    # Parcourt chaque DataObjectGroup
    for objet in data_object_group:
        # Récupère le nom de fichier
        file_name = objet.find(".//Filename").text

        # Trouve l'élément BinaryDataObject et son message digest
        binary_data_object = objet.find("BinaryDataObject")
        message_digest = binary_data_object.find("MessageDigest").text

        # Crée un nouveau nom de fichier en utilisant l'attribut 'id' et l'extension du fichier original
        new_name = binary_data_object.attrib['id']
        oldext = os.path.splitext(file_name)[1]
        new_name = new_name + oldext

        # Crée le chemin complet vers le nouveau fichier dans le répertoire cible
        new_path = os.path.join(target_dir, new_name)

        # Parcourt les données de métadonnées pour trouver le fichier correspondant au message digest
        for item in data:
            files = item.get("files", [])
            for file in files:
                # Vérifier que les empreintes matchent
                if message_digest == file.get("sha512"):
                    # Récupère l'ancien chemin du fichier et copie le fichier vers le nouveau chemin
                    old_path = file.get("filename")
                    shutil.copy(old_path, new_path)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        input("Appuyez sur Entrée pour fermer l'application.")
        QApplication.instance().quit()  # Quitter l'application PyQt
