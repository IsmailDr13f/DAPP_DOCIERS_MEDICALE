// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ContractPatient.sol";
import "./ContractDoctor.sol";

contract Manager {
    address public admin;

    // Références vers les contrats des Patients et Docteurs
    Patient public patientContract;
    Doctor public doctorContract;

    // Structure pour enregistrer les actions effectuées
    struct AuditLog {
        address actor;
        string action;
        uint timestamp;
    }

    // Mappage pour garder une trace des actions effectuées sur chaque dossier médical
    mapping(address => AuditLog[]) public patientAuditLogs;
    mapping(address => AuditLog[]) public doctorAuditLogs;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Seul l'admin peut effectuer cette action.");
        _;
    }

    constructor(address _patientContract, address _doctorContract) {
        admin = msg.sender;
        patientContract = Patient(_patientContract);
        doctorContract = Doctor(_doctorContract);
    }

    function registerPatient(address _patientAddress, string memory _name) public onlyAdmin {
        patientContract.registerPatient(_patientAddress, _name);
        
        // Enregistrement de l'action dans l'audit
        patientAuditLogs[_patientAddress].push(AuditLog({
            actor: msg.sender,
            action: "Enregistrement du patient",
            timestamp: block.timestamp
        }));
    }

    function registerDoctor(address _doctorAddress, string memory _name) public onlyAdmin {
        doctorContract.registerDoctor(_doctorAddress, _name);

        // Enregistrement de l'action dans l'audit
        doctorAuditLogs[_doctorAddress].push(AuditLog({
            actor: msg.sender,
            action: "Enregistrement du docteur",
            timestamp: block.timestamp
        }));
    }

    // Fonction pour obtenir l'historique des actions d'un patient
    function getPatientAuditLogs(address _patientAddress) public view returns (AuditLog[] memory) {
        return patientAuditLogs[_patientAddress];
    }

    // Fonction pour obtenir l'historique des actions d'un docteur
    function getDoctorAuditLogs(address _doctorAddress) public view returns (AuditLog[] memory) {
        return doctorAuditLogs[_doctorAddress];
    }
}
