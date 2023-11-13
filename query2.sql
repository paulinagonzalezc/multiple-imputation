-- Query2.sql
-- Given schema Data(patientID, hospitalID, age, cholesterol, tomography)
-- imputes the missing data in the `cholesterol` field 
-- of a hospital with the average of all entries
-- from the same hospital, where the age is the same as that of
-- the patient whose cholesterol is being imputed
-- For example, given relation instance:
-- {(0,0,15,0,0), (1,0,24,42,12), (2,0,24,NULL,100), (3,0,24,10,87)}
-- this query should transform it into the following instance:
-- {(0,0,15,0,0), (1,0,24,42,12), (2,0,24,26,100), (3,0,24,10,87)}

-- REPLACE THIS LINE WITH YOUR QUERY AND SUBMIT THIS FILE.
UPDATE PatientData pd
JOIN (
    SELECT hospitalID, age, AVG(cholesterol) AS avg_cholesterol
    FROM PatientData pd
    WHERE cholesterol IS NOT NULL
    GROUP BY hospitalID, age
) d2
ON pd.hospitalID  = d2.hospitalID AND pd.age = d2.age
SET pd.cholesterol = d2.avg_cholesterol
WHERE pd.cholesterol IS NULL;
