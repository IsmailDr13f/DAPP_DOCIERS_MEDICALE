// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractPatient.sol";

contract Doctor {
    struct DoctorData {
        address doctorAddress;
        string name;
        bool isRegistered;
    }

    mapping(address => DoctorData) public doctors; // Liste des docteurs enregistrés
    Patient public patientContract; // Référence au contrat Patient

    // Événements
    event DoctorRegistered(address indexed doctorAddress, string name);
    event RecordUpdated(
        address indexed patientAddress,
        string recordHash,
        address updatedBy,
        uint256 timestamp
    );

    // Modificateur : vérifie si l'appelant est un docteur enregistré
    modifier onlyRegisteredDoctor() {
        require(doctors[msg.sender].isRegistered, "Vous devez etre un docteur enregistre.");
        _;
    }

    // Constructeur : initialisation du contrat Patient
    constructor(address _patientContract) {
        require(_patientContract != address(0), "Adresse du contrat Patient invalide.");
        patientContract = Patient(_patientContract);
    }

    // Fonction pour enregistrer un docteur
    function registerDoctor(address _doctorAddress, string memory _name) public {
        require(_doctorAddress != address(0), "Adresse du docteur invalide.");
        require(!doctors[_doctorAddress].isRegistered, "Docteur deja enregistre.");

        doctors[_doctorAddress] = DoctorData({
            doctorAddress: _doctorAddress,
            name: _name,
            isRegistered: true
        });

        emit DoctorRegistered(_doctorAddress, _name);
    }

    // Fonction pour ajouter un dossier médical à un patient
    function addRecordForPatient(address _patientAddress, string memory _recordHash)
    public
    onlyRegisteredDoctor
{
    require(_patientAddress != address(0), "Adresse du patient invalide.");
    require(bytes(_recordHash).length > 0, "Hash du dossier medical invalide.");

    // Vérifie si le docteur est autorisé pour ce patient
    require(
        patientContract.isDoctorAuthorized(_patientAddress, msg.sender),
        "Acces non autorise pour ce patient."
    );

    // Appelle la fonction addMedicalRecord avec un seul argument (le hash du dossier)
    patientContract.addMedicalRecord(_recordHash);

    // Émet un événement pour signaler l'ajout du dossier médical
    emit RecordUpdated(_patientAddress, _recordHash, msg.sender, block.timestamp);
}

}
