--collects all the animals that are preditors and multiplies there scores by 1.2
SELECT 
    sp.species_name, 
    e.experiment_id, 
    sp.is_predator, 
    CASE 
        WHEN sp.is_predator = TRUE THEN e.score * 1.2
        ELSE e.score 
    END AS score
FROM experiment e
JOIN subject s ON e.subject_id = s.subject_id
JOIN species sp ON s.species_id = sp.species_id
ORDER BY score DESC;