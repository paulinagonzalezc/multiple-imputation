-- Query3.sql
-- Given schema Data(patientID, hospitalID, age, cholesterol, tomography)
-- imputes the missing data in the `cholesterol` field 
-- of a patient with with the smallest value of
-- patient's with an age in the same five year bracket, i.e., 0-4, 5-9, 10-14, etc.
-- For example, given relation instance:
-- {(0,0,19,0,0), (1,0,24,42,12), (2,1,24,NULL,100), (3,2,20,10,87)}
-- this query should transform it into the following instance:
-- {(0,0,19,0,0), (1,0,24,42,12), (2,1,24,10,100), (3,2,20,10,87)}

-- REPLACE THIS LINE WITH YOUR QUERY AND SUBMIT THIS FILE.
UPDATE PatientData pd1
JOIN (
    SELECT 
        FLOOR(age/5)*5 AS age_bracket,
        MIN(cholesterol) as min_cholesterol
    FROM PatientData
    WHERE cholesterol IS NOT NULL
    GROUP BY age_bracket
) pd2
ON FLOOR(pd1.age/5)*5 = pd2.age_bracket
SET pd1.cholesterol = pd2.min_cholesterol
WHERE pd1.cholesterol IS NULL;
