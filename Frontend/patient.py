import json
from web3 import Web3
import customtkinter as ctk


class PatientInterface:
    def __init__(self, contract_address, abi_path, provider_url):
        """Initialisation de l'interface et de la connexion au contrat."""
        self.web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

        if not self.web3.isConnected():
            raise Exception("Échec de la connexion au fournisseur Web3.")

        with open(abi_path, 'r') as file:
            self.contract_abi = json.load(file)

        self.contract = self.web3.eth.contract(address=Web3.to_checksum_address(contract_address),
                                               abi=self.contract_abi)
        self.account = None  # Adresse du portefeuille connecté

        # Initialisation de l'interface CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Gestion des Patients")
        self.build_interface()

    def connect_wallet(self, address, private_key):
        """Connecte un portefeuille Ethereum pour signer les transactions."""
        self.account = address
        self.web3.eth.default_account = address
        self.private_key = private_key

    def build_interface(self):
        """Crée l'interface utilisateur."""
        self.label_title = ctk.CTkLabel(self.root, text="Gestion des Patients Blockchain", font=("Arial", 20))
        self.label_title.pack(pady=10)

        # Champs d'enregistrement du patient
        self.entry_patient_address = ctk.CTkEntry(self.root, placeholder_text="Adresse du patient")
        self.entry_patient_address.pack(pady=5)

        self.entry_patient_name = ctk.CTkEntry(self.root, placeholder_text="Nom du patient")
        self.entry_patient_name.pack(pady=5)

        self.btn_register_patient = ctk.CTkButton(self.root, text="Enregistrer le patient",
                                                  command=self.register_patient)
        self.btn_register_patient.pack(pady=10)

        # Gestion de l'accès médecins
        self.entry_doctor_address = ctk.CTkEntry(self.root, placeholder_text="Adresse du médecin")
        self.entry_doctor_address.pack(pady=5)

        self.btn_grant_access = ctk.CTkButton(self.root, text="Accorder l'accès", command=self.grant_access)
        self.btn_grant_access.pack(pady=5)

        self.btn_revoke_access = ctk.CTkButton(self.root, text="Révoquer l'accès", command=self.revoke_access)
        self.btn_revoke_access.pack(pady=5)

        # Ajout de dossier médical
        self.entry_record_hash = ctk.CTkEntry(self.root, placeholder_text="Hash du dossier médical")
        self.entry_record_hash.pack(pady=5)

        self.btn_add_record = ctk.CTkButton(self.root, text="Ajouter un dossier médical",
                                            command=self.add_medical_record)
        self.btn_add_record.pack(pady=10)

        # Visualisation des dossiers
        self.btn_view_records = ctk.CTkButton(self.root, text="Afficher les dossiers", command=self.view_records)
        self.btn_view_records.pack(pady=10)

    def register_patient(self):
        """Enregistre un nouveau patient dans le contrat."""
        patient_address = self.entry_patient_address.get()
        patient_name = self.entry_patient_name.get()

        try:
            tx = self.contract.functions.registerPatient(patient_address, patient_name).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Patient enregistré avec succès. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Erreur d'enregistrement du patient:", e)

    def grant_access(self):
        """Accorde l'accès à un médecin."""
        doctor_address = self.entry_doctor_address.get()
        try:
            tx = self.contract.functions.grantAccess(doctor_address).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Accès accordé avec succès. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Erreur lors de l'accord d'accès:", e)

    def revoke_access(self):
        """Révoque l'accès d'un médecin."""
        doctor_address = self.entry_doctor_address.get()
        try:
            tx = self.contract.functions.revokeAccess(doctor_address).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Accès révoqué avec succès. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Erreur lors de la révocation de l'accès:", e)

    def add_medical_record(self):
        """Ajoute un dossier médical au patient connecté."""
        record_hash = self.entry_record_hash.get()
        try:
            tx = self.contract.functions.addMedicalRecord(record_hash).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Dossier médical ajouté avec succès. TX Hash:", tx_hash.hex())
        except Exception as e:
            print("Erreur lors de l'ajout du dossier médical:", e)

    def view_records(self):
        """Affiche les dossiers médicaux du patient."""
        try:
            records = self.contract.functions.getRecords(self.account).call()
            print("Dossiers médicaux:", records)
        except Exception as e:
            print("Erreur lors de la récupération des dossiers:", e)

    def run(self):
        self.root.mainloop()
