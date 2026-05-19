DROP PROCEDURE IF EXISTS inregistreaza_programare_completa;
-- PROC_END

CREATE PROCEDURE inregistreaza_programare_completa(
    IN p_id_pacient INT,
    IN p_id_medic INT,
    IN p_servicii_json JSON
)
BEGIN
    DECLARE v_id_programare INT;
    DECLARE v_id_consult INT;
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_len INT DEFAULT 0;
    DECLARE v_nume_serviciu VARCHAR(100);
    DECLARE v_pret_serviciu DECIMAL(10,2);

    -- 1. Inserăm în Programari
    INSERT INTO Programari(id_pacient, id_medic, data_programare)
    VALUES (p_id_pacient, p_id_medic, CURRENT_DATE);

    SET v_id_programare = LAST_INSERT_ID();

    -- 2. Inserăm în Consultatii (Folosind doar coloanele din schema ta: id_prog, Diagnostic)
    INSERT INTO Consultatii(id_prog, Diagnostic)
    VALUES (v_id_programare, 'Consultatie automata generata de sistem');

    SET v_id_consult = LAST_INSERT_ID();

    -- 3. Procesăm serviciile din JSON pentru Facturi
    SET v_len = JSON_LENGTH(p_servicii_json);

    WHILE v_i < v_len DO
        SET v_nume_serviciu = JSON_UNQUOTE(JSON_EXTRACT(p_servicii_json, CONCAT('$[', v_i, '].nume')));
        SET v_pret_serviciu = JSON_EXTRACT(p_servicii_json, CONCAT('$[', v_i, '].pret'));

        -- Inserăm în Facturi folosind v_id_consult
        INSERT INTO Facturi(id_consult, Suma, Data_platii)
        VALUES (v_id_consult, v_pret_serviciu, CURRENT_DATE);

        SET v_i = v_i + 1;
    END WHILE;

    SELECT v_id_consult AS id_noua_consultatie;
END;
-- PROC_END