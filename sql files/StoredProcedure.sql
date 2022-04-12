use dtbank

DELIMITER //

CREATE PROCEDURE StoredProcedure( measure varchar(30), min real, max real )
BEGIN
	select R.drugbank_id, R.uniprot_id from Reaction_Related R, Uniprot U where U.uniprot_id=R.uniprot_id and R.measure=measure and R.affinity_NM >= min and R.affinity_NM <= max;
END //

DELIMITER ;
