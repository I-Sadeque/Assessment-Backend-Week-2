--makes a list of subjects, there species, there test and the percentage score for them to 2dp
SELECT 
    e.experiment_id, 
    e.subject_id, 
    sp.species_name AS species, 
    TO_CHAR(e.experiment_date, 'YYYY-MM-DD') AS experiment_date, 
    et.type_name AS experiment_type, 
    ROUND((e.score / et.max_score) * 100, 2) || '%' AS score
FROM experiment e
JOIN subject s ON e.subject_id = s.subject_id
JOIN species sp ON s.species_id = sp.species_id
JOIN experiment_type et ON e.experiment_type_id = et.experiment_type_id
ORDER BY e.experiment_date DESC;