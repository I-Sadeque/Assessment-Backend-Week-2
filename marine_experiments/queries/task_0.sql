
--outputs all data points with the letter o in there name
SELECT 
    subject_id, 
    subject_name, 
    species_id, 
    date_of_birth
FROM subject
WHERE subject_name LIKE '%o%';