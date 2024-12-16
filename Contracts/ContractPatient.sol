// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Patient {
    struct MedicalRecord {
        string recordHash;
        mapping(address => bool) authorizedDoctors; // Map of doctors authorized for this record
    }

    mapping(address => mapping(string => MedicalRecord)) private records; // Patient -> RecordHash -> MedicalRecord

    event AccessGranted(address indexed patientAddress, address indexed doctorAddress, string recordHash);
    event AccessRevoked(address indexed patientAddress, address indexed doctorAddress, string recordHash);

    modifier onlyPatient(address _patientAddress, address _caller) {
        require(_patientAddress == _caller, "Seul le patient peut effectuer cette action.");
        _;
    }

    // Autoriser un docteur pour un dossier médical spécifique
    function authorizeToMedicalFolder(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public onlyPatient(_patientAddress, msg.sender) {
        records[_patientAddress][_recordHash].recordHash = _recordHash;
        records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress] = true;
        emit AccessGranted(_patientAddress, _doctorAddress, _recordHash);
    }

    // Révoquer l'accès d'un docteur pour un dossier médical spécifique
    function revokeFromMedicalFolder(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public onlyPatient(_patientAddress, msg.sender) {
        require(
            records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress],
            "Le docteur n'a pas d'acces a ce dossier."
        );
        records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress] = false;
        emit AccessRevoked(_patientAddress, _doctorAddress, _recordHash);
    }

    // Vérifier si un docteur est autorisé pour un dossier médical spécifique
    function isDoctorAuthorized(
        address _patientAddress,
        string memory _recordHash,
        address _doctorAddress
    ) public view returns (bool) {
        return records[_patientAddress][_recordHash].authorizedDoctors[_doctorAddress];
    }
}
