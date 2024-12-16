# DAPP_DOCIERS_MEDICALE ![logo](https://github.com/user-attachments/assets/902091f0-2c7f-4dd2-927b-19ee6382ff4e)


Bienvenue dans le projet **DAPP_DOCIERS_MEDICALE**, une application décentralisée (DApp) pour la gestion des dossiers médicaux utilisant la blockchain Ethereum, Pinata (IPFS) pour le stockage décentralisé, Web3.py pour les interactions backend, et une interface graphique construite avec CustomTkinter.
![image](https://github.com/user-attachments/assets/bfcc81b6-4bde-4ed6-ba15-8dd75553a89a)

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- [Python](https://www.python.org/) (version 3.6 ou supérieure)
- [pip](https://pip.pypa.io/en/stable/) (gestionnaire de paquets Python)
- [Remix IDE](https://remix.ethereum.org/) (pour déployer et interagir avec les contrats intelligents)
- Un fournisseur Ethereum (comme [Ganache](https://archive.trufflesuite.com/ganache/) pour les tests locaux)
- Un compte Pinata avec une clé API JWT (pour le stockage des fichiers)
- [MetaMask](https://metamask.io/) (extension de navigateur pour interagir avec la blockchain)

## Installation

### 1. Cloner le dépôt GitHub

```bash
git clone https://github.com/IsmailDr13f/DAPP_DOCIERS_MEDICALE.git
cd DAPP_DOCIERS_MEDICALE
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet avec les informations suivantes :

```env
PINATA_JWT_TOKEN= Votre_Secret_JWT_Pinata
```

Remplacez `Votre_Secret_JWT_Pinata` par votre clés JWT obtenues depuis [Pinata](https://www.pinata.cloud/).

## Configuration et Déploiement

### 1. Déploiement des contrats intelligents

1. Ouvrez [Remix IDE](https://remix.ethereum.org/).
2. Importez les fichiers de contrat situés dans le répertoire `contracts` de ce projet.
3. Compilez les contrats en utilisant une version compatible de Solidity (indiquée en haut de chaque fichier de contrat).
4. Déployez les contrats sur un réseau Ethereum (local ou public) :
   - Pour un réseau local, utilisez [Ganache](https://trufflesuite.com/ganache/).
5. Notez l'adresse du contrat déployé, elle sera utilisée dans le code backend.

### 2. Configuration de l’interface graphique (CustomTkinter)

1. Lancez l'application graphique nommée **MEDICA** :
   ```bash
   python app_.py
   ```
2. Assurez-vous que les clés API Pinata et l'adresse du contrat déployé sont correctement configurées dans le fichier Python backend.

## Fonctionnalités principales

1. **Ajout de dossiers médicaux** :
   - Les utilisateurs peuvent télécharger des fichiers médicaux vers Pinata (IPFS).
   - Les hachages des fichiers sont enregistrés sur la blockchain.
   - ![image](https://github.com/user-attachments/assets/64d54239-1f8d-4203-a100-1bac2da3cacd)


2. **Autorisation des médecins** :
   - Les patients peuvent autoriser des médecins à accéder à des dossiers spécifiques via l’interface graphique.
   - ![image](https://github.com/user-attachments/assets/77ab7b54-938f-4e86-b06a-f4a7dea07a18)
   - ![image](https://github.com/user-attachments/assets/363fb1ca-b79c-4080-8a4d-5ed53d9fa97b)



3. **Révocation d’accès** :
   - Les patients peuvent révoquer l’accès des médecins à leurs dossiers.
   - ![image](https://github.com/user-attachments/assets/5734bb72-064b-4940-8b28-40a969437cd8)


## Structure du projet

```
DAPP_DOCIERS_MEDICALE/
|— contracts/            # Contrats Solidity (backend)
|— frontend/             # Code pour l'interface graphique MEDICA
|— requirements.txt      # Dépendances Python
|— README.md            # Documentation
```

## Déploiement sur un réseau public

1. **Choisissez un réseau** :
   - Testnet (Ropsten, Goerli, etc.) ou Mainnet.
2. **Ajoutez des fonds** :
   - Assurez-vous d’avoir suffisamment d’ETH pour couvrir les frais de gaz.
3. **Reconfigurez le backend** :
   - Mettez à jour l’adresse du contrat dans le script backend.
4. **Lancez l’application** :
   ```bash
   python app_.py
   ```

## Notes importantes

- Assurez-vous que vos clés privées et informations sensibles ne sont pas exposées publiquement.
- Testez l’application sur un réseau de test avant tout déploiement sur Mainnet.



Pour toute question ou suggestion, veuillez ouvrir une issue sur le dépôt GitHub ou Nous contacter directement.

---
Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus d'informations.

