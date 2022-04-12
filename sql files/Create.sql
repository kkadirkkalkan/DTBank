use dtbank;


CREATE TABLE Institution (
	institution_name CHAR(100),
    score	INTEGER,
	PRIMARY KEY(institution_name)
);

CREATE TABLE User_Work (
	username	CHAR(100),
	name		CHAR(100),
	institution_name CHAR(100) NOT NULL,
    password	CHAR(100) NOT NULL,
	PRIMARY KEY(username,institution_name),
	FOREIGN KEY(institution_name) REFERENCES Institution(institution_name)
);

CREATE TABLE Database_Manager (

	username	CHAR(100) UNIQUE NOT NULL,
	password	CHAR(100),
	count	INTEGER ,
	PRIMARY KEY(count)
);

CREATE TABLE Drug (
	drugbank_id	CHAR(30),
	drug_name	CHAR(100),
	description	TEXT,
	smiles	TEXT,
	PRIMARY KEY(drugbank_id)
);
CREATE TABLE UniProt (
	uniprot_id	CHAR(30),
	sequence	TEXT,
	target_name	CHAR(100),
	PRIMARY KEY(uniprot_id)
);
CREATE TABLE Article_Institution(
	doi	CHAR(100),
	institution_name	CHAR(100) NOT NULL,
	FOREIGN KEY(institution_name) REFERENCES Institution(institution_name),
	PRIMARY KEY(doi)
);
CREATE TABLE Article_Author(
	doi CHAR(100),
	username CHAR(100) NOT NULL,
	FOREIGN KEY(doi) REFERENCES Article_Institution(doi),
	FOREIGN KEY(username) REFERENCES User_Work(username),
	PRIMARY KEY(doi, username)
);

CREATE TABLE Reaction_Related (
	reaction_id	CHAR(30),
	affinity_NM	CHAR(30),
	measure	CHAR(30),
	drugbank_id CHAR(30) NOT NULL,
	doi	CHAR(100) NOT NULL,
	uniprot_id	CHAR(30) NOT NULL,
	FOREIGN KEY(uniprot_id) REFERENCES UniProt(uniprot_id),
	FOREIGN KEY(drugbank_id) REFERENCES Drug(drugbank_id),
	FOREIGN KEY(doi) REFERENCES Article_Institution(doi),
	PRIMARY KEY(reaction_id)
);
CREATE TABLE Sider_Has (
	umls_cui	CHAR(30),
	side_effect_name	CHAR(100) NOT NULL,
	drugbank_id	CHAR(30) NOT NULL,
	FOREIGN KEY(drugbank_id) REFERENCES Drug(drugbank_id),
	PRIMARY KEY(umls_cui,drugbank_id)
);

CREATE TABLE Interaction_with (
	drugbank_id_1	CHAR(30),
	drugbank_id_2	CHAR(30),
	FOREIGN KEY(drugbank_id_1) REFERENCES Drug(drugbank_id) ,
	FOREIGN KEY(drugbank_id_2) REFERENCES Drug(drugbank_id) ,
	PRIMARY KEY(drugbank_id_1, drugbank_id_2 )
);
