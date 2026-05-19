CREATE DATABASE IF NOT EXISTS clinica_medicala;
USE clinica_medicala;

CREATE TABLE IF NOT EXISTS Medici (
    id_medic INT PRIMARY KEY AUTO_INCREMENT,
    nume VARCHAR(50),
    specializare VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Pacienti (
    id_pacient INT PRIMARY KEY AUTO_INCREMENT,
    nume VARCHAR(50),
    cnp CHAR(13) UNIQUE
);

CREATE TABLE IF NOT EXISTS Programari (
    id_programare INT PRIMARY KEY AUTO_INCREMENT,
    id_medic INT NOT NULL,
    id_pacient INT NOT NULL,
    data_programare DATETIME,
    FOREIGN KEY (id_medic) REFERENCES Medici(id_medic) ON DELETE CASCADE,
    FOREIGN KEY (id_pacient) REFERENCES Pacienti(id_pacient) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Consultatii (
    id_consult INT PRIMARY KEY AUTO_INCREMENT,
    id_prog INT NOT NULL UNIQUE,
    Diagnostic TEXT NOT NULL,
    Recomandari TEXT,
    -- CORECTIE AICI: am schimbat id_programari in id_programare pentru a se potrivi cu tabelul de mai sus
    FOREIGN KEY (id_prog) REFERENCES Programari(id_programare) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tratamente_Retete (
    id_reteta INT PRIMARY KEY AUTO_INCREMENT,
    id_consult INT NOT NULL,
    Medicament VARCHAR(100) NOT NULL,
    Dozaj VARCHAR(50),
    FOREIGN KEY (id_consult) REFERENCES Consultatii(id_consult) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Facturi (
    id_factura INT PRIMARY KEY AUTO_INCREMENT,
    id_consult INT NOT NULL,
    Suma DECIMAL(10, 2) NOT NULL,
    Data_platii DATE NOT NULL,
    FOREIGN KEY (id_consult) REFERENCES Consultatii(id_consult) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_pacient INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    detalii TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_pacient FOREIGN KEY (id_pacient) REFERENCES Pacienti(id_pacient) ON DELETE CASCADE
) ENGINE=InnoDB;