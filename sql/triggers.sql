DROP TRIGGER IF EXISTS trg_facturi_before_insert;
-- TRIGGER_END

CREATE TRIGGER trg_facturi_before_insert
BEFORE INSERT ON Facturi
FOR EACH ROW
BEGIN
    IF NEW.Suma <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Suma facturii trebuie sa fie mai mare decat 0';
    END IF;
END;
-- TRIGGER_END

DROP TRIGGER IF EXISTS trg_pacienti_after_update;
-- TRIGGER_END

CREATE TRIGGER trg_pacienti_after_update
AFTER UPDATE ON Pacienti
FOR EACH ROW
BEGIN
    INSERT INTO user_log (id_pacient, action, detalii)
    VALUES (OLD.id_pacient, 'UPDATE_PACIENT', CONCAT('S-au modificat datele pentru pacientul cu CNP: ', OLD.cnp));
END;
-- TRIGGER_END