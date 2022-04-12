CREATE TRIGGER removeDrugfromReaction
BEFORE DELETE ON Drug
FOR EACH ROW
DELETE FROM Reaction_Related
WHERE Reaction_Related.drugbank_id = OLD.drugbank_id;

CREATE TRIGGER removeDrugfromInteraction
BEFORE DELETE ON Drug
FOR EACH ROW
DELETE FROM Interaction_with
WHERE Interaction_with.drugbank_id_1 = OLD.drugbank_id OR Interaction_with.drugbank_id_2 = OLD.drugbank_id;

CREATE TRIGGER removeDrugfromSider
BEFORE DELETE ON Drug
FOR EACH ROW
DELETE FROM Sider_Has
WHERE Sider_Has.drugbank_id = OLD.drugbank_id;

CREATE TRIGGER removeProteinfromReaction
BEFORE DELETE ON UniProt
FOR EACH ROW
DELETE FROM Reaction_Related
WHERE Reaction_Related.uniprot_id = OLD.uniprot_id;

CREATE TRIGGER addArticleScore
AFTER INSERT ON Article_Institution
FOR EACH ROW
UPDATE Institution
SET Institution.score = Institution.score+5
WHERE Institution.institution_name  = NEW.institution_name;

CREATE TRIGGER addUserScore
AFTER INSERT ON Article_Author
FOR EACH ROW
UPDATE Institution
INNER JOIN Article_Institution ON Article_Institution.institution_name=Institution.institution_name
SET Institution.score = Institution.score+2
WHERE Article_Institution.doi  = NEW.doi;

CREATE TRIGGER deleteUserScore
AFTER DELETE ON Article_Author
FOR EACH ROW
UPDATE Institution
INNER JOIN Article_Institution ON Article_Institution.institution_name=Institution.institution_name
SET Institution.score = Institution.score-2
WHERE Article_Institution.doi  = OLD.doi;