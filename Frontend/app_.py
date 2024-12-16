import customtkinter
from PIL import Image
from click import command
from netaddr.strategy.ipv4 import width
from web3 import Web3
import csv
import os
import ipfshttpclient
import json
import requests
from dotenv import load_dotenv
import zipfile


# Blockchain setup
GANACHE_URL = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
load_dotenv()
print(web3.eth.accounts[5])
def upload_to_pinata(medical_data):
    # Récupérer le token JWT de l'environnement
    PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

    # URL de l'API de Pinata pour ajouter des données à IPFS
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    # Définir les en-têtes avec le token d'autorisation Bearer
    headers = {'Authorization': f'Bearer {PINATA_JWT_TOKEN}'}

    json_data = {"data":medical_data} # Convertir en JSON pour vérifier la validité
    print(f"Sending data to Pinata: {json_data}")

    # Faire une requête POST pour envoyer les données JSON à Pinata
    response = requests.post(url, json=json_data, headers=headers)

    # Vérifier la réponse de l'API Pinata
    if response.status_code == 200:
        # Extraire le hash IPFS de la réponse
        ipfs_hash = response.json()['IpfsHash']
        print(f"Les données ont été chargées avec succès sur IPFS. Hash : {ipfs_hash}")
        return ipfs_hash
    else:
        print(f"Erreur lors du téléchargement sur Pinata : {response.status_code}, {response.text}")
        return None


def upload_directory_to_pinata(directory_path):
        # Récupérer le token JWT de l'environnement
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

        # URL de l'API de Pinata pour ajouter des données à IPFS
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        # Définir les en-têtes avec le token d'autorisation Bearer
        headers = {'Authorization': f'Bearer {PINATA_JWT_TOKEN}'}

        # Créer un fichier zip à partir du dossier
        zip_file_path = f"{directory_path}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory_path))

        print(f"Dossier compressé en: {zip_file_path}")

        # Ouvrir le fichier zip pour l'envoyer à Pinata
        with open(zip_file_path, 'rb') as file:
            files = {'file': file}

            # Faire une requête POST pour envoyer le fichier zip à Pinata
            response = requests.post(url, files=files, headers=headers)

        # Vérifier la réponse de l'API Pinata
        if response.status_code == 200:
            # Extraire le hash IPFS de la réponse
            ipfs_hash = response.json()['IpfsHash']
            print(f"Les données ont été chargées avec succès sur IPFS. Hash : {ipfs_hash}")
            return ipfs_hash
        else:
            print(f"Erreur lors du téléchargement sur Pinata : {response.status_code}, {response.text}")
            return None


if web3.is_connected():
    print("Connecté à la blockchain")
else:
    print("Connexion échouée")

def load_user_profiles(csv_file_path):
    user_profiles = {}

    try:
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Extract fields from the CSV
                address = row["Address"]
                role = row["Role"]
                specialization = row["Specialization"]
                name = row["Name"]

                # Convert "N/A" or empty specialization to None
                specialization = specialization if specialization != "N/A" else None

                # Populate the dictionary
                user_profiles[address] = {"role": role, "specialization": specialization, "name":name}

    except FileNotFoundError:
        print(f"File '{csv_file_path}' not found. Starting with an empty dictionary.")

    return user_profiles

# Example usage
csv_file_path = 'user_accounts.csv'
user_profiles = load_user_profiles(csv_file_path)

# Print the dictionary to verify
print(user_profiles)



class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, msg,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x100")
        self.title("Notification")
        self.label = customtkinter.CTkLabel(self, text=msg)
        self.label.pack(padx=20, pady=20)



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDICA")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.selected_files = []
        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        self.frame1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        self.frame2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.create_interface()

        doctor_contract_address = "0x24dA47fc46A1dAD599679Aa368D20e2284413b63"
        doctor_abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "_patientContract", "type": "address"}
            ],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "address", "name": "doctorAddress", "type": "address"},
                {"indexed": False, "internalType": "string", "name": "name", "type": "string"}
            ],
            "name": "DoctorRegistered",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "address", "name": "patientAddress", "type": "address"},
                {"indexed": False, "internalType": "string", "name": "recordHash", "type": "string"},
                {"indexed": False, "internalType": "address", "name": "updatedBy", "type": "address"}
            ],
            "name": "RecordUpdated",
            "type": "event"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "_patientAddress", "type": "address"},
                {"internalType": "string", "name": "_recordHash", "type": "string"}
            ],
            "name": "addRecordForPatient",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
        self.doctor_contract = web3.eth.contract(address=doctor_contract_address,abi=doctor_abi)

        patient_contract_address = "0xf8e81D47203A594245E36C48e151709F0C19fBe8"
        patient_abi = [
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "patientAddress",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "doctorAddress",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "recordHash",
				"type": "string"
			}
		],
		"name": "AccessGranted",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "patientAddress",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "doctorAddress",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "recordHash",
				"type": "string"
			}
		],
		"name": "AccessRevoked",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_patientAddress",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_recordHash",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_doctorAddress",
				"type": "address"
			}
		],
		"name": "authorizeToMedicalFolder",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_patientAddress",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_recordHash",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_doctorAddress",
				"type": "address"
			}
		],
		"name": "isDoctorAuthorized",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_patientAddress",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_recordHash",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_doctorAddress",
				"type": "address"
			}
		],
		"name": "revokeFromMedicalFolder",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
        self.patient_contract = web3.eth.contract(address=patient_contract_address, abi=patient_abi)

        #web3.eth.default_account = web3.eth.accounts[0]  # Compte par défaut
    def create_medical_record(self, patient_address, medical_data):
        try:
            # 1. Vérifier si l'adresse du patient est valide
            if not web3.is_address(patient_address):
                self.show_message("Invalid patient address!")
                return

            # 2. Charger les données médicales sur IPFS
            #client = ipfshttpclient.connect()  # Connexion à IPFS
            #ipfs_response = client.add_json(medical_data)  # Ajoutez les données médicales (en JSON)
            #ipfs_hash = ipfs_response["Hash"]
            #client.close()
            ipfs_response = upload_to_pinata(medical_data)  # Ajoutez les données médicales (en JSON)
            ipfs_hash = ipfs_response["Hash"]

            # 3. Enregistrer le hachage dans la blockchain via le smart contract
            doctor_address = web3.eth.default_account  # Adresse Ethereum du médecin connecté
            doctor_contract = web3.eth.contract(
                address=self.doctor_contract_address,
                abi=self.doctor_abi
            )

            # Appelez la méthode pour créer un dossier médical
            tx = doctor_contract.functions.createMedicalRecord(
                patient_address,
                ipfs_hash
            ).transact({'from': doctor_address})
            web3.eth.wait_for_transaction_receipt(tx)

            self.show_message("Medical record created successfully!")

        except Exception as e:
            self.show_message(f"Error creating medical record: {str(e)}")

    def create_interface(self):
        # Frame 1: Image Display
        my_image = customtkinter.CTkImage(light_image=Image.open("bg1.png"), size=(500, 800))
        image_label = customtkinter.CTkLabel(self.frame1, image=my_image, text="")
        image_label.pack()

        # Frame 2: Tabs for Sign In and Sign Up
        tabview_log = customtkinter.CTkTabview(master=self.frame2, width=460, height=600)
        tabview_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tabview_log.add("Sign In")
        tabview_log.add("Sign Up")
        tabview_log.set("Sign In")

        # Sign In Tab
        self.create_sign_in_tab(tabview_log)

        # Sign Up Tab
        self.create_sign_up_tab(tabview_log)

        ########msg balance#########
        label_msg = customtkinter.CTkLabel(master=self.frame2, text="The login process is empowered by metamask,")
        label_msg.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")
        label_msg_ = customtkinter.CTkLabel(master=self.frame2,
                                            text="please verify that your wallet contain some ETH balance.",
                                            text_color="#029CFF")
        label_msg_.grid(row=2, column=0, padx=10, pady=0, sticky="nsew")

    def create_sign_in_tab(self, tabview):
        logo_w = customtkinter.CTkImage(light_image=Image.open("logoooo.png"), size=(100, 80))
        logo_label = customtkinter.CTkLabel(tabview.tab("Sign In"), image=logo_w, text="")
        logo_label.pack(pady=50)

        label_up = customtkinter.CTkLabel(master=tabview.tab("Sign In"), text="Welcome to medica!", fg_color="transparent", text_color="#FFFFFF", font=("arial", 30))
        label_up.pack(pady=20)

        label_adr = customtkinter.CTkLabel(master=tabview.tab("Sign In"), text="Account Address *", fg_color="transparent", justify="left")
        label_adr.pack(padx=20, pady=(100, 5), anchor="w")
        self.entry_signin_address = customtkinter.CTkEntry(master=tabview.tab("Sign In"), placeholder_text="Ex: 0x123456...", width=400)
        self.entry_signin_address.pack(padx=20, pady=(0, 10), anchor="w")

        signin_btn = customtkinter.CTkButton(master=tabview.tab("Sign In"), corner_radius=20, width=300, text="Sign in!", command=self.sign_in)
        signin_btn.pack(padx=30, pady=20)

    def create_sign_up_tab(self, tabview):
        logo_w = customtkinter.CTkImage(light_image=Image.open("logoooo.png"), size=(100, 80))
        logo_label = customtkinter.CTkLabel(tabview.tab("Sign Up"), image=logo_w, text="")
        logo_label.pack()

        label_up = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Welcome to medica!", fg_color="transparent", text_color="#FFFFFF", font=("arial", 30))
        label_up.pack(pady=20)

        # Full Name
        label_name = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Full Name *", fg_color="transparent", justify="left")
        label_name.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_name = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: John Doe", width=400)
        self.entry_signup_name.pack(padx=20, pady=(0, 10), anchor="w")

        # Ethereum Address
        label_adr = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Account Address *", fg_color="transparent", justify="left")
        label_adr.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_address = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: 0x123456...", width=400)
        self.entry_signup_address.pack(padx=20, pady=(0, 10), anchor="w")

        # Profile Role
        label_profil = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Patient/Doctor *", fg_color="transparent", justify="left")
        label_profil.pack(padx=20, pady=(10, 5), anchor="w")
        self.optionmenu_role = customtkinter.CTkOptionMenu(master=tabview.tab("Sign Up"), width=400, values=["Patient", "Doctor"])
        self.optionmenu_role.pack(padx=20, pady=(0, 10), anchor="w")

        # Specialization (if Doctor)
        label_spe = customtkinter.CTkLabel(master=tabview.tab("Sign Up"), text="Specialization", fg_color="transparent", justify="left")
        label_spe.pack(padx=20, pady=(10, 5), anchor="w")
        self.entry_signup_specialization = customtkinter.CTkEntry(master=tabview.tab("Sign Up"), placeholder_text="Ex: Cardiologist", width=400)
        self.entry_signup_specialization.pack(padx=20, pady=(0, 10), anchor="w")
        self.entry_signup_specialization.configure(state="disabled")

        # Role-dependent behavior
        def update_specialization_state(choice):
            if choice == "Patient":
                self.entry_signup_specialization.configure(state="disabled")
                self.entry_signup_specialization.delete(0, "end")
            else:
                self.entry_signup_specialization.configure(state="normal")

        self.optionmenu_role.configure(command=update_specialization_state)

        # Sign Up Button
        signup_btn = customtkinter.CTkButton(master=tabview.tab("Sign Up"), corner_radius=20, text="Create Account!", command=self.sign_up)
        signup_btn.pack(padx=30, pady=20)



    def sign_in(self):
        def check_balance(address):
            balance = web3.eth.get_balance(address)
            return web3.from_wei(balance, "ether")
        self.address = self.entry_signin_address.get()
        if web3.is_address(self.address):
            balance = check_balance(self.address)
            print(balance)
            if balance < 0.01:  # Exige un minimum de 0.01 ETH
                self.show_message("Insufficient ETH balance for authentication!")
                return

        if web3.is_address(self.address):
            profile = user_profiles.get(self.address)
            if profile:
                self.show_profile_interface(profile)
            else:
                self.show_message("Address not registered!")
        else:
            self.show_message("Invalid Ethereum address!")

    def sign_up(self):
        name = self.entry_signup_name.get()
        address = self.entry_signup_address.get()
        role = self.optionmenu_role.get()
        specialization = self.entry_signup_specialization.get() if role == "Doctor" else None

        if web3.is_address(address):
            user_profiles[address] = {"name": name, "role": role, "specialization": specialization}
            self.save_to_csv(name, address, role, specialization)
            self.show_message(f"Account created for {role}!")
        else:
            self.show_message("Invalid Ethereum address!")

    def save_to_csv(self, name, address, role, specialization):
        # Define the CSV file path
        file_path = 'user_accounts.csv'

        # Check if the file already exists to write headers only once
        file_exists = os.path.exists(file_path)

        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write header if the file does not exist
            if not file_exists:
                writer.writerow(["Name", "Address", "Role", "Specialization"])

            # Write the user data row
            writer.writerow([name, address, role, specialization if specialization else "N/A"])

    def show_profile_interface(self, profile):
        role = profile["role"]
        print(profile)
        name = profile["name"]
        specialization = profile.get("specialization", "N/A")
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        #self.geometry(f"{screen_width}x{screen_height}")
        #self.resizable(True, True)
        self.frame1.destroy()
        self.frame2.destroy()

        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        #self.frame1.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.frame1.pack(fill="x", padx=10, pady=5)

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        #self.frame2.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.frame2.pack(side="left",padx=10, fill="y", pady=5)

        self.frame3 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        #self.frame3.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.frame3.pack(side="right",padx=10, fill="both", expand=True, pady=5)


        frame_lab1 = customtkinter.CTkFrame(master=self.frame1,width=200)
        frame_lab1.pack(side="left",padx=10,pady=10)

        frame_lab2 = customtkinter.CTkFrame(master=self.frame1,width=500)
        frame_lab2.pack(side="left",padx=10,pady=10)

        label = customtkinter.CTkLabel(master=frame_lab1, text=f"Welcome, {role} {name}!", font=("Arial", 30),width=500)
        label.pack(pady=20,padx=20,side="top",fill="x")

        # Ajouter un label pour afficher le solde
        self.balance_label = customtkinter.CTkLabel(master=frame_lab2,width=500,height=45, text="Chargement du solde...", font=("Arial", 20))
        self.balance_label.pack(pady=20,padx=20,side="top",fill="x")

        # Deconnecter
        button_signout = customtkinter.CTkButton(master=frame_lab2,width=450,text="sign out",fg_color="red",command=self.signout)
        button_signout.pack(side="left",fill="x",padx=10,pady=5)

        # Lancer la mise à jour du solde dès le démarrage
        self.update_balance_label()
        if role == "Doctor":
            specialization_label = customtkinter.CTkLabel(master=frame_lab1, text=f"Specialization: {specialization}")
            specialization_label.pack(pady=10,padx=20, side="bottom",fill="x")

            frame_btn = customtkinter.CTkFrame(self.frame3,width=500)
            frame_btn.pack(padx=20,pady=5,side="top")

            # Create buttons for Create and Update Medical Folder
            create_btn = customtkinter.CTkButton(
                frame_btn,fg_color='#29453C',text_color='#45C976',
                text="Create Medical Folder",
                command=self.open_create_medical_folder_window
            )
            create_btn.pack(pady=10,padx=30,side="left")

            update_btn = customtkinter.CTkButton(
                frame_btn,fg_color='#2D3A54',text_color='#5994E2',
                text="Update Medical Folder",
                command=self.open_update_window
            )
            update_btn.pack(pady=10,padx=30,side="left")

            self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame3, height=400, width=500)
            self.scrollable_frame.pack(padx=20, pady=5,side="top")

            self.update_btn = customtkinter.CTkButton(self.frame3,text="Update list", command=self.get_medical_files_from_pinata)
            self.update_btn.pack(padx=20, pady=5,side="top")
            #self.get_medical_files_from_pinata()

            # Liste pour afficher les événements
            self.textbox = customtkinter.CTkTextbox(self.frame2, height=200, width=400)
            self.textbox.pack(padx=20, pady=10, fill="both", expand=True)

            self.start_button = customtkinter.CTkButton(self.frame2, text="Get Transactions",
                                                        command=self.start_retrieving_transactions)
            self.start_button.pack(pady=10)

        else:
            specialization_label = customtkinter.CTkLabel(master=frame_lab1, text="Hope you feel better soon!")
            specialization_label.pack(pady=10, padx=20, side="bottom", fill="x")

            frame_btn = customtkinter.CTkFrame(self.frame3, width=500)
            frame_btn.pack(padx=20, pady=5, side="top")

            self.update_btn = customtkinter.CTkButton(frame_btn, text="Update list",
                                                      command=self.get_medical_files_from_pinata_patient)
            self.update_btn.pack(padx=10, pady=5, side="left")

            # Create buttons for Autorise and revoke acces to Medical Folder
            autorise_btn = customtkinter.CTkButton(
                frame_btn, fg_color='#29453C', text_color='#45C976',
                text="Autorise doctor",
                command=self.autorise_medical_folder_window
            )
            autorise_btn.pack(pady=5, padx=10, side="left")

            revoque_btn = customtkinter.CTkButton(
                frame_btn, fg_color='#4C3039', text_color='#E86B6C',
                text="revoke doctor",
                command=self.revoke_medical_folder_window
            )
            revoque_btn.pack(pady=5, padx=10, side="left")

            self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame3, height=400, width=500)
            self.scrollable_frame.pack(padx=20, pady=5, side="top")

            # Liste pour afficher les événements
            self.textbox = customtkinter.CTkTextbox(self.frame2, height=200, width=400)
            self.textbox.pack(padx=20, pady=10, fill="both", expand=True)

            self.start_button = customtkinter.CTkButton(self.frame2, text="Get Transactions",
                                                        command=self.start_retrieving_transactions)
            self.start_button.pack(pady=10)



    def get_transactions(self, address, start_block=0, end_block=None):
        """Récupère les transactions associées à une adresse dans la blockchain."""
        if end_block is None:
            end_block = web3.eth.block_number  # Récupère le dernier bloc

        address = self.address

        transactions = []

        for block_number in range(start_block, end_block + 1):
            self.update_textbox(f"Récupération du bloc {block_number}...\n")
            try:
                block = web3.eth.get_block(block_number, full_transactions=True)
                for tx in block['transactions']:
                    # Vérifie si l'adresse est l'expéditeur ou le destinataire
                    if tx['from'] == address or tx['to'] == address:
                        transactions.append(tx)
                        message = (
                            f"De: {tx['from']}, Vers: {tx['to']}, Montant: {web3.from_wei(tx['value'], 'ether')} ETH, "
                            f"Bloc: {tx['blockNumber']}\n")
                        self.update_textbox(message)
            except Exception as e:
                self.update_textbox(f"Erreur lors de la récupération du bloc {block_number} : {str(e)}\n")

        return transactions

    def update_textbox(self, message):
        """Met à jour la TextBox avec de nouvelles informations."""
        self.textbox.insert('end', message)  # Insère le texte à la fin
        self.textbox.yview('end')  # Fait défiler automatiquement vers la fin

    def start_retrieving_transactions(self):
        import threading
        """Lance le processus de récupération des transactions dans un thread séparé."""
        start_block = 0  # Vous pouvez personnaliser le bloc de départ
        end_block = web3.eth.block_number
        self.textbox.insert('end', "Lancement de la récupération des transactions...\n")

        # Lancement du thread
        threading.Thread(
            target=self.get_transactions,
            args=(web3.eth.accounts[0], start_block, end_block),
            daemon=True
        ).start()


    def get_medical_files_from_pinata_patient(self):
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')
        url = "https://api.pinata.cloud/data/pinList"
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}',
        }

        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            files_data = response.json()
            files = files_data.get('rows', [])
            print("files in pinata: ", files_data)

            # Ajouter les fichiers dans le Scrollable Frame
            self.display_files_in_scrollable_frame_patient(files)
        else:
            print("Erreur lors de la récupération des fichiers depuis Pinata.")

    def display_files_in_scrollable_frame_patient(self,files):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file in files:
            file_name = file.get("metadata", {}).get("name", "Nom du fichier inconnu")
            file_url = f"https://gateway.pinata.cloud/ipfs/{file['ipfs_pin_hash']}"
            file_cid = file.get('ipfs_pin_hash',"No CID available")
            json_MF = self.download_zip_from_ipfs(file_cid)
            print(json_MF)
            if "address" in json_MF.keys() and json_MF["address"] == self.address:

                frame = customtkinter.CTkFrame(self.scrollable_frame)
                frame.pack(side="top", pady=10)

                # Ajouter un label pour chaque fichier dans le Scrollable Frame
                #label = customtkinter.CTkLabel(frame, text=file_cid, anchor="w", width=400)
                #label.pack(padx=10, pady=5,side='left')

                entry = customtkinter.CTkEntry(frame, width=300)
                entry.insert(0,file_cid)
                entry.pack(padx=5, pady=5,side='left')

                # Ajouter un bouton pour ouvrir l'URL du fichier
                button = customtkinter.CTkButton(frame, text="Download Folder", command=lambda url=file_url: self.open_file(url))
                button.pack(pady=5,padx=5,side='left')
            else:
                pass

    def get_medical_files_from_pinata(self):
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')
        url =  "https://api.pinata.cloud/data/pinList"
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}',
        }


        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            files_data = response.json()
            files = files_data.get('rows', [])
            print("files in pinata: ",files_data)

            # Ajouter les fichiers dans le Scrollable Frame
            self.display_files_in_scrollable_frame(files)
        else:
            print("Erreur lors de la récupération des fichiers depuis Pinata.")

    def display_files_in_scrollable_frame(self, files):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file in files:
            file_name = file.get("metadata", {}).get("name", "Nom du fichier inconnu")
            file_url = f"https://gateway.pinata.cloud/ipfs/{file['ipfs_pin_hash']}"
            file_cid = file.get('ipfs_pin_hash',"No CID available")
            json_MF = self.download_zip_from_ipfs(file_cid)
            if "address_doctor" in json_MF.keys() and json_MF["address_doctor"] == self.address:

                # Ajouter un label pour chaque fichier dans le Scrollable Frame
                label = customtkinter.CTkLabel(self.scrollable_frame, text=file_name, anchor="w", width=400)
                label.pack(padx=10, pady=5)

                # Ajouter un bouton pour ouvrir l'URL du fichier
                button = customtkinter.CTkButton(self.scrollable_frame, text="Download Folder", command=lambda url=file_url: self.open_file(url))
                button.pack(pady=5)
            else:
                pass

    def open_file(self, url):
        import webbrowser
        webbrowser.open(url)
        print(f"Ouverture du fichier : {url}")

    def signout(self):
        self.frame1.destroy()
        self.frame2.destroy()
        self.frame3.destroy()
        self.frame1 = customtkinter.CTkFrame(master=self, width=200, height=1200)
        self.frame1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.frame2 = customtkinter.CTkFrame(master=self, width=500, height=1200)
        self.frame2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.create_interface()

    def get_balance(self):
        balance_wei = web3.eth.get_balance(self.address)  # Solde en Wei
        balance_ether = web3.from_wei(balance_wei, 'ether')  # Convertir en Ether
        return balance_ether


    # Fonction pour mettre à jour le label avec le solde
    def update_balance_label(self):
        balance = self.get_balance()  # Obtenez le solde actuel
        self.balance_label.configure(text=f"Balance: {balance} ETH".format() )

        # Mettre à jour l'interface toutes les 10 secondes
        self.frame1.after(10000, self.update_balance_label)

    def revoke_medical_folder_window(self):
        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Revoke Doctor")
        self.create_window.geometry("500x400")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=300, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Section Information Médicales
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Revoke Doctor",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_CID = customtkinter.CTkLabel(scrollable_frame, text="CID folder")
        label_CID.pack(pady=5)
        entry_CID = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_CID.pack(pady=5)

        label_doc_adress = customtkinter.CTkLabel(scrollable_frame, text="Revoked doctor adress")
        label_doc_adress.pack(pady=5)
        entry_doc_adress = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doc_adress.pack(pady=5)

        label_ppk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_ppk.pack(pady=5)
        entry_ppk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_ppk.pack(pady=5)

        # Bouton de soumission
        submit_button = customtkinter.CTkButton(
            self.create_window, width=400, fg_color="red",
            text="Revoke doctor",
            command=lambda: self.revoke_to_medical_folder(
                cid=entry_CID.get(),
                patient_private_key=entry_ppk.get(), address_patient=self.address,
                new_doctor_adress=entry_doc_adress.get(),
            )
        )
        submit_button.pack(pady=5)

    def revoke_to_medical_folder(self,cid,patient_private_key,address_patient,new_doctor_adress):
        # Construction de la transaction
        transaction = self.patient_contract.functions.revokeFromMedicalFolder(
            address_patient, cid, new_doctor_adress
        ).build_transaction({
            'from': address_patient,
            'nonce': web3.eth.get_transaction_count(address_patient),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        })

        # Signature de la transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=patient_private_key)

        # Envoi de la transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction envoyée avec succès. Hash: {web3.to_hex(tx_hash)}")

        self.create_window.destroy()
        return web3.to_hex(tx_hash)




    def autorise_medical_folder_window(self):
        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Autorise Doctor")
        self.create_window.geometry("500x400")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=300, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Section Information Médicales
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Autorise Doctor",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_CID = customtkinter.CTkLabel(scrollable_frame, text="CID folder")
        label_CID.pack(pady=5)
        entry_CID = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_CID.pack(pady=5)

        label_doc_adress = customtkinter.CTkLabel(scrollable_frame, text="New Autorised doctor adress")
        label_doc_adress.pack(pady=5)
        entry_doc_adress = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doc_adress.pack(pady=5)

        label_ppk = customtkinter.CTkLabel(scrollable_frame, text="Your private key")
        label_ppk.pack(pady=5)
        entry_ppk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_ppk.pack(pady=5)

        # Bouton de soumission
        submit_button = customtkinter.CTkButton(
            self.create_window, width=400, fg_color="#64B5A0",
            text="Autorise doctor",
            command=lambda: self.autorise_to_medical_folder(
                cid=entry_CID.get(),
                patient_private_key=entry_ppk.get(), address_patient=self.address,
                new_doctor_adress=entry_doc_adress.get(),
            )
        )
        submit_button.pack(pady=5)

    def autorise_to_medical_folder(self,cid,patient_private_key,address_patient,new_doctor_adress):
        # modifier l'addresse de docteur dans le dossier chisie


        # Construction de la transaction
        transaction = self.patient_contract.functions.authorizeToMedicalFolder(
            address_patient, cid, new_doctor_adress
        ).build_transaction({
            'from': address_patient,
            'nonce': web3.eth.get_transaction_count(address_patient),
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
        })

        # Signature de la transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=patient_private_key)

        # Envoi de la transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction envoyée avec succès. Hash: {web3.to_hex(tx_hash)}")

        #self.delete_old_file_from_pinata(cid)
        self.create_window.destroy()
        return web3.to_hex(tx_hash)
        #pass




    def open_create_medical_folder_window(self):
                """Ouvre une nouvelle fenêtre pour créer un dossier médical"""

                self.create_window = customtkinter.CTkToplevel(self)
                self.create_window.title("Create Medical Folder")
                self.create_window.geometry("500x600")
                scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window,height=500,width=500)
                scrollable_frame.pack(padx=20,pady=5)
                # Section Information Médicales
                label_info = customtkinter.CTkLabel(scrollable_frame, text="Information Médicales",
                                                    font=("Arial", 20, "bold"))
                label_info.pack(pady=10)

                label_address = customtkinter.CTkLabel(scrollable_frame, text="Adresse du patient")
                label_address.pack(pady=5)
                entry_address = customtkinter.CTkEntry(scrollable_frame,width=400)
                entry_address.pack(pady=5)

                label_pk = customtkinter.CTkLabel(scrollable_frame, text="Votre clé privé")
                label_pk.pack(pady=5)
                entry_pk = customtkinter.CTkEntry(scrollable_frame, width=400)
                entry_pk.pack(pady=5)

                label_name = customtkinter.CTkLabel(scrollable_frame, text="Nom du patient")
                label_name.pack(pady=5)
                entry_name = customtkinter.CTkEntry(scrollable_frame,width=400)
                entry_name.pack(pady=5)

                label_doctor = customtkinter.CTkLabel(scrollable_frame, text="Nom du médecin actuel")
                label_doctor.pack(pady=5)
                entry_doctor = customtkinter.CTkEntry(scrollable_frame,width=400)
                entry_doctor.pack(pady=5)

                # Section Antécédents Médicaux
                label_antecedents = customtkinter.CTkLabel(scrollable_frame, text="Antécédents Médicaux",
                                                           font=("Arial", 20, "bold"))
                label_antecedents.pack(pady=10)

                label_familiaux = customtkinter.CTkLabel(scrollable_frame, text="Antécédents familiaux")
                label_familiaux.pack(pady=5)
                entry_familiaux = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
                entry_familiaux.pack(pady=5)

                label_personnels = customtkinter.CTkLabel(scrollable_frame, text="Antécédents personnels")
                label_personnels.pack(pady=5)
                entry_personnels = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
                entry_personnels.pack(pady=5)

                # Section Consultation Médicale Actuelle
                label_consultation = customtkinter.CTkLabel(scrollable_frame, text="Consultation Médicale Actuelle",
                                                            font=("Arial", 20, "bold"))
                label_consultation.pack(pady=10)

                label_motif = customtkinter.CTkLabel(scrollable_frame, text="Motif de consultation")
                label_motif.pack(pady=5)
                entry_motif = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
                entry_motif.pack(pady=5)

                label_etat = customtkinter.CTkLabel(scrollable_frame, text="État du patient")
                label_etat.pack(pady=5)
                entry_etat = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
                entry_etat.pack(pady=5)

                label_date = customtkinter.CTkLabel(scrollable_frame, text="Date de consultation")
                label_date.pack(pady=5)
                entry_date = customtkinter.CTkEntry(scrollable_frame,width=400)
                entry_date.pack(pady=5)

                # Section Traitement en Cours
                label_treatment = customtkinter.CTkLabel(scrollable_frame, text="Traitement en Cours",
                                                         font=("Arial", 20, "bold"))
                label_treatment.pack(pady=10)

                label_medications = customtkinter.CTkLabel(scrollable_frame, text="Médicament en cours",width=400)
                label_medications.pack(pady=5)
                entry_medications = customtkinter.CTkTextbox(scrollable_frame, height=50,width=400)
                entry_medications.pack(pady=5)

                # Section Documents Annexes
                label_documents = customtkinter.CTkLabel(scrollable_frame, text="Documents Annexes",
                                                         font=("Arial", 20, "bold"))
                label_documents.pack(pady=10)

                select_button = customtkinter.CTkButton(scrollable_frame, text="Sélectionner des documents",
                                                        command=self.select_documents)
                select_button.pack(pady=5)

                self.file_listbox = customtkinter.CTkTextbox(scrollable_frame, height=100,width=400)
                self.file_listbox.pack(pady=5)

                # Bouton de soumission
                submit_button = customtkinter.CTkButton(
                    self.create_window,width=400,fg_color="#64B5A0",
                    text="Créer le dossier médical",
                    command=lambda: self.submit_medical_folder(
                        address=entry_address.get(),
                        doctor_private_key=entry_pk.get(),address_doctor=self.address,
                        name=entry_name.get(),
                        doctor=entry_doctor.get(),
                        familiaux=entry_familiaux.get("1.0", "end").strip(),
                        personnels=entry_personnels.get("1.0", "end").strip(),
                        motif=entry_motif.get("1.0", "end").strip(),
                        etat=entry_etat.get("1.0", "end").strip(),
                        date=entry_date.get(),
                        medications=entry_medications.get("1.0", "end").strip()
                    )
                )
                submit_button.pack(pady=5)


    def submit_medical_folder(self, **kwargs):
        # Afficher les données collectées
        print("Données collectées pour le dossier médical :", kwargs)

        patient_address = kwargs.get('address')

        # Récupérer la clé privée du docteur
        doctor_private_key = kwargs.get('doctor_private_key')
        # Convertir les autres données en JSON (sans la clé privée)
        kwargs_without_private_key = {key: value for key, value in kwargs.items() if key != 'doctor_private_key'}
        json_data = json.dumps(kwargs_without_private_key, indent=4, ensure_ascii=False)
        print(json_data)
        # Créer un fichier JSON (sans la clé privée)
        json_file_path = "dossier_medical.json"
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)

        print("\nFichier JSON généré :\n", json_data)

        # Ajouter les fichiers sélectionnés à un dossier temporaire
        temp_dir = self.create_temp_directory(self.file_listbox.get("1.0", "end-1c").splitlines(), json_file_path)

        # Envoyer le dossier temporaire à Pinata et obtenir le hash
        ipfs_hash = upload_directory_to_pinata(temp_dir)

        # Fermer la fenêtre de création du dossier médical
        self.create_window.destroy()

        # Afficher le hash IPFS dans la console
        print(f"Le dossier médical a été téléchargé avec succès sur IPFS. Hash : {ipfs_hash}")

        # Ajouter le hash IPFS à la blockchain
        self.add_record_to_blockchain(doctor_private_key,patient_address, ipfs_hash)

        message = "Medical folder created Successfully!!"
        self.show_message(message)

    def add_record_to_blockchain(self,doctor_private_key, patient_address, ipfs_hash):

        # Créer la transaction pour appeler addRecordForPatient
        transaction = self.doctor_contract.functions.addRecordForPatient(
            patient_address, ipfs_hash
        ).build_transaction({
            'gas': 2000000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': web3.eth.get_transaction_count(self.address),
        })

        #return transaction

        # Signer la transaction avec la clé privée
        signed_transaction = web3.eth.account.sign_transaction(transaction, doctor_private_key)

        print(signed_transaction)

        # Envoyer la transaction et obtenir le hash de la transaction
        #transaction_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

        print(f"Transaction envoyée : {transaction_hash.hex()}")

        # Attendre la confirmation de la transaction
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
        if receipt['status'] == 1:
            print("Le dossier médical a été enregistré avec succès sur la blockchain.")
        else:
            print("Erreur lors de l'enregistrement du dossier médical sur la blockchain.")


    def create_temp_directory(self, file_paths, json_file_path):
        import tempfile
        import shutil
        """Crée un dossier temporaire contenant les fichiers et le fichier JSON."""
        temp_dir = tempfile.mkdtemp()  # Crée un dossier temporaire

        # Copier chaque fichier sélectionné dans le dossier temporaire
        for file_path in file_paths:
            if os.path.exists(file_path):  # Vérifie que le fichier existe
                shutil.copy(file_path, temp_dir)
            else:
                print(f"Le fichier {file_path} n'existe pas.")

        # Copier le fichier JSON dans le dossier temporaire
        shutil.copy(json_file_path, temp_dir)

        print(f"Dossier temporaire créé à : {temp_dir}")
        return temp_dir

    def create_zip_from_directory(self, directory_path):
        """Crée un fichier ZIP à partir d'un dossier."""
        zip_file_path = f"{directory_path}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, directory_path))

        print(f"Le dossier a été compressé en: {zip_file_path}")
        return zip_file_path

    def select_documents(self):
        from tkinter import filedialog
        # Ouvrir la boîte de dialogue de sélection de fichiers
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner des fichiers",
            filetypes=[("Tous les fichiers", "*.*"), ("Fichiers PDF", "*.pdf"), ("Fichiers images", "*.jpg *.png *.jpeg")]
        )

        if file_paths:
            self.selected_files.extend(file_paths)  # Ajouter les fichiers sélectionnés à la liste

            # Afficher les noms de fichiers dans la liste
            self.file_listbox.delete("1.0", "end")  # Effacer la liste précédente
            for file in self.selected_files:
                self.file_listbox.insert("end", f"{file}\n")

#######################################################################################################################

    def open_update_window(self):
        """Ouvre une nouvelle fenêtre pour mettre à jour un dossier médical existant."""
        self.update_window = customtkinter.CTkToplevel(self)
        self.update_window.title("Update Medical Folder")
        self.update_window.geometry("500x200")

        label_cid = customtkinter.CTkLabel(self.update_window, text="CID of your folder")
        label_cid.pack(pady=10)
        entry_cid = customtkinter.CTkEntry(self.update_window, width=400)
        entry_cid.pack(pady=10)

        submit_cid_button = customtkinter.CTkButton(self.update_window, text="Upload Folder",
                                          command=lambda: self.load_existing_folder(entry_cid.get()))
        submit_cid_button.pack(pady=10)

    def load_existing_folder(self, cid):
        """Charge le dossier médical existant depuis IPFS à l'aide du CID."""
        # Télécharger le fichier ZIP depuis IPFS
        json_MF = self.download_zip_from_ipfs(cid)

        print(json_MF)

        # Extraire les informations du ZIP et pré-remplir le formulaire
        self.extract_and_fill_form(json_MF)

        # Afficher un bouton de soumission pour valider les modifications
        #submit_button = customtkinter.CTkButton(self.update_window, text="Mettre à jour le dossier",
        #                              command=lambda: self.submit_update(folder_path))
        #submit_button.pack(pady=10)


    def download_zip_from_ipfs(self, cid):
        import io
        """Télécharge et extrait le fichier ZIP depuis IPFS via la passerelle Pinata en mémoire."""

        # URL pour accéder au fichier ZIP sur IPFS
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"

        # Faire la requête pour obtenir le fichier ZIP
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            print(f"Fichier ZIP téléchargé avec succès depuis IPFS.")

            # Charger le fichier ZIP dans la mémoire en utilisant BytesIO
            zip_data = io.BytesIO(response.content)

            # Extraire le contenu du ZIP à partir de la mémoire
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                # Liste des fichiers dans le ZIP
                zip_file_list = zip_ref.namelist()

                # Dictionnaire pour stocker les fichiers JSON extraits en mémoire
                extracted_json = None

                # Extraire chaque fichier dans le dictionnaire
                for file_name in zip_file_list:
                    if file_name.endswith('.json'):  # Vérifier si c'est un fichier JSON
                        with zip_ref.open(file_name) as file:
                            file_content = file.read()

                            # Charger le contenu JSON et le retourner
                            try:
                                extracted_json = json.loads(file_content)
                                print(f"Fichier JSON {file_name} chargé avec succès.")
                            except json.JSONDecodeError:
                                print(f"Erreur lors du décodage du fichier JSON: {file_name}")

            # Vérifier si un fichier JSON a été extrait, sinon retourner None
            if extracted_json is not None:
                return extracted_json
            else:
                print("Aucun fichier JSON trouvé dans l'archive.")
                return None
        else:
            print(f"Erreur lors du téléchargement de {url}. Statut : {response.status_code}")
            return None

    def extract_and_fill_form(self, medical_data_json):
        """Extraire et remplir le formulaire avec les données du dossier médical."""

        # Charger les données JSON (en supposant que 'medical_data_json' est déjà un dict ou un json chargé)
        if isinstance(medical_data_json, str):
            # Si c'est une chaîne, charger en tant que JSON
            medical_data = json.loads(medical_data_json)
        else:
            medical_data = medical_data_json

        self.create_window = customtkinter.CTkToplevel(self)
        self.create_window.title("Update Medical Folder")
        self.create_window.geometry("500x600")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.create_window, height=500, width=500)
        scrollable_frame.pack(padx=20, pady=5)
        # Section Information Médicales
        label_info = customtkinter.CTkLabel(scrollable_frame, text="Information Médicales",
                                            font=("Arial", 20, "bold"))
        label_info.pack(pady=10)

        label_address = customtkinter.CTkLabel(scrollable_frame, text="Adresse du patient")
        label_address.pack(pady=5)
        entry_address = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_address.pack(pady=5)

        label_pk = customtkinter.CTkLabel(scrollable_frame, text="Votre clé privé")
        label_pk.pack(pady=5)
        entry_pk = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_pk.pack(pady=5)

        label_name = customtkinter.CTkLabel(scrollable_frame, text="Nom du patient")
        label_name.pack(pady=5)
        entry_name = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_name.insert(0, medical_data.get('patient_name', ''))
        entry_name.pack(pady=5)

        label_doctor = customtkinter.CTkLabel(scrollable_frame, text="Nom du médecin actuel")
        label_doctor.pack(pady=5)
        entry_doctor = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_doctor.pack(pady=5)

        # Section Antécédents Médicaux
        label_antecedents = customtkinter.CTkLabel(scrollable_frame, text="Antécédents Médicaux",
                                                   font=("Arial", 20, "bold"))
        label_antecedents.pack(pady=10)

        label_familiaux = customtkinter.CTkLabel(scrollable_frame, text="Antécédents familiaux")
        label_familiaux.pack(pady=5)
        entry_familiaux = customtkinter.CTkTextbox(scrollable_frame, height=50, width=400)
        entry_familiaux.pack(pady=5)

        label_personnels = customtkinter.CTkLabel(scrollable_frame, text="Antécédents personnels")
        label_personnels.pack(pady=5)
        entry_personnels = customtkinter.CTkTextbox(scrollable_frame, height=50, width=400)
        entry_personnels.pack(pady=5)

        # Section Consultation Médicale Actuelle
        label_consultation = customtkinter.CTkLabel(scrollable_frame, text="Consultation Médicale Actuelle",
                                                    font=("Arial", 20, "bold"))
        label_consultation.pack(pady=10)

        label_motif = customtkinter.CTkLabel(scrollable_frame, text="Motif de consultation")
        label_motif.pack(pady=5)
        entry_motif = customtkinter.CTkTextbox(scrollable_frame, height=50, width=400)
        entry_motif.pack(pady=5)

        label_etat = customtkinter.CTkLabel(scrollable_frame, text="État du patient")
        label_etat.pack(pady=5)
        entry_etat = customtkinter.CTkTextbox(scrollable_frame, height=50, width=400)
        entry_etat.pack(pady=5)

        label_date = customtkinter.CTkLabel(scrollable_frame, text="Date de consultation")
        label_date.pack(pady=5)
        entry_date = customtkinter.CTkEntry(scrollable_frame, width=400)
        entry_date.pack(pady=5)

        # Section Traitement en Cours
        label_treatment = customtkinter.CTkLabel(scrollable_frame, text="Traitement en Cours",
                                                 font=("Arial", 20, "bold"))
        label_treatment.pack(pady=10)

        label_medications = customtkinter.CTkLabel(scrollable_frame, text="Médicament en cours", width=400)
        label_medications.pack(pady=5)
        entry_medications = customtkinter.CTkTextbox(scrollable_frame, height=50, width=400)
        entry_medications.pack(pady=5)

        # Section Documents Annexes
        label_documents = customtkinter.CTkLabel(scrollable_frame, text="Documents Annexes",
                                                 font=("Arial", 20, "bold"))
        label_documents.pack(pady=10)

        select_button = customtkinter.CTkButton(scrollable_frame, text="Sélectionner des documents",
                                                command=self.select_documents)
        select_button.pack(pady=5)

        self.file_listbox = customtkinter.CTkTextbox(scrollable_frame, height=100, width=400)
        self.file_listbox.pack(pady=5)



        # Remplir les champs du formulaire avec les données du dossier médical

        entry_address.insert(0, medical_data.get('address', ''))
        #entry_pk.insert(0, medical_data.get('doctor_private_key', ''))
        entry_name.insert(0, medical_data.get('name', ''))
        entry_doctor.insert(0, medical_data.get('doctor', ''))

        # Antécédents médicaux
        entry_familiaux.insert("1.0", medical_data.get('familiaux', ''))
        entry_personnels.insert("1.0", medical_data.get('personnels', ''))

        # Consultation médicale actuelle
        entry_motif.insert("1.0", medical_data.get('motif', ''))
        entry_etat.insert("1.0", medical_data.get('etat', ''))
        entry_date.insert(0, medical_data.get('date', ''))

        # Traitement en cours
        entry_medications.insert("1.0", medical_data.get('medications', ''))

        # Documents annexes
        # Si des documents ont été ajoutés dans le dossier JSON, les afficher dans la liste
        if 'documents' in medical_data:
            for doc in medical_data['documents']:
                self.file_listbox.insert("end", doc)

        # Bouton de soumission
        submit_button = customtkinter.CTkButton(
                self.create_window, width=400, fg_color="#64B5A0",
                    text="Créer le dossier médical",
                    command=lambda: self.submit_medical_folder(
                        address=entry_address.get(),
                        doctor_private_key=entry_pk.get(),address_doctor=self.address,
                        name=entry_name.get(),
                        doctor=entry_doctor.get(),
                        familiaux=entry_familiaux.get("1.0", "end").strip(),
                        personnels=entry_personnels.get("1.0", "end").strip(),
                        motif=entry_motif.get("1.0", "end").strip(),
                        etat=entry_etat.get("1.0", "end").strip(),
                        date=entry_date.get(),
                        medications=entry_medications.get("1.0", "end").strip()
                    )
                )
        submit_button.pack(pady=5)
        self.update_window.destroy()
        print("Formulaire rempli avec succès.")

    def submit_update(self, folder_path):
        """Soumet les modifications et crée un nouveau fichier ZIP mis à jour."""
        new_zip_path = self.create_zip_from_folder(folder_path)

        # Télécharger le nouveau fichier ZIP sur Pinata
        new_cid = upload_directory_to_pinata(new_zip_path)

        # Supprimer l'ancien fichier ZIP de Pinata
        self.delete_old_file_from_pinata(folder_path)

        # Mettre à jour la blockchain avec le nouveau CID
        #self.update_blockchain(new_cid)

    def delete_old_file_from_pinata(self, cid):
        """Supprimer l'ancien fichier sur Pinata avec un token JWT."""
        url = f"https://api.pinata.cloud/pinning/unpin/{cid}"

        # Récupérer le token JWT de l'environnement
        PINATA_JWT_TOKEN = os.getenv('PINATA_JWT_TOKEN')

        # Définir les en-têtes avec le token d'autorisation Bearer
        headers = {
            'Authorization': f'Bearer {PINATA_JWT_TOKEN}'
        }

        # Effectuer la requête DELETE pour supprimer l'ancien fichier
        response = requests.request("DELETE", url, headers=headers)

        # Vérifier la réponse
        if response.status_code == 200:
            print("Ancien fichier supprimé avec succès de Pinata.")
        else:
            print(f"Erreur lors de la suppression de l'ancien fichier : {response.status_code}, {response.text}")

    def create_zip_from_folder(self, folder_path, zip_file_path="updated_medical_folder.zip"):
        """Crée un fichier ZIP à partir d'un dossier contenant des fichiers modifiés."""
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        return zip_file_path


    def show_message(self, message):
        # Ensure self.toplevel_window is initialized
        if not hasattr(self,
                       'toplevel_window') or self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # Create a new instance of ToplevelWindow and pass the message
            self.toplevel_window = ToplevelWindow(msg=message)
        else:
            # If the window exists, bring it to the front
            self.toplevel_window.focus()




if __name__ == "__main__":
    app = App()
    app.mainloop()
