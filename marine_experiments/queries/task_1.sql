--returns a subjects data and there species
SELECT 
    s.subject_id, 
    s.subject_name, 
    sp.species_name, 
    TO_CHAR(s.date_of_birth, 'YYYY-MM') AS date_of_birth
FROM subject s
JOIN species sp ON s.species_id = sp.species_id
ORDER BY s.date_of_birth DESC;