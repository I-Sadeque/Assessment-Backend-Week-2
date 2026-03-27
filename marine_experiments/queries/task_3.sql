-- returns the a table of data that shows the average score for each species in each test
SELECT 
    et.type_name, 
    sp.species_name, 
    ROUND(AVG(e.score), 1) AS average_score
FROM experiment e
JOIN experiment_type et ON e.experiment_type_id = et.experiment_type_id
JOIN subject s ON e.subject_id = s.subject_id
JOIN species sp ON s.species_id = sp.species_id
GROUP BY et.type_name, sp.species_name
HAVING AVG(e.score) > 5
ORDER BY average_score DESC;