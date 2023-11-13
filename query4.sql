-- Query3.sql
-- Given schema Data(patientID, hospitalID, age, cholesterol, tomography)
-- imputes the missing data in the `tomography` attribute using
-- one-dimensional linear regression on top of the `cholesterol` attribute 
-- For example, given relation instance:
-- {(0,0,19,0,0), (1,0,24,100,200), (2,1,24,NULL,100), (3,2,20,10,NULL)}
-- this query should transform it into the following instance:
-- {(0,0,19,0,0), (1,0,24,100,200), (2,1,24,NULL,100), (3,2,20,10,20)}

-- REPLACE THIS LINE WITH YOUR QUERY AND SUBMIT THIS FILE.
UPDATE PatientData pd
-- calculating the mean (average) of cholesterol and tomography for all rows where neither value is null.
JOIN (
    SELECT
        AVG(cholesterol) as mean_cholesterol, -- average cholesterol
        AVG(tomography) as mean_tomography -- average tomography
    FROM PatientData
    WHERE cholesterol IS NOT NULL AND tomography IS NOT NULL
) s ON 1=1 -- JOIN condition (1=1) a trick to always join every row in 'pd' with this subquery result
-- computing the 'b' coefficient for a simple linear regression.
JOIN (
    SELECT
        -- This formula calculates the 'b' coefficient of a simple linear regression.
        SUM((pd_inner.cholesterol - s.mean_cholesterol) * (pd_inner.tomography - s.mean_tomography)) / 
        SUM(POWER(pd_inner.cholesterol - s.mean_cholesterol, 2)) as b
    FROM PatientData pd_inner, (
        -- the same as the first subquery, 
        -- calculating the mean (average) of cholesterol and tomography for all rows where neither value is null.
        SELECT
            AVG(cholesterol) as mean_cholesterol,
            AVG(tomography) as mean_tomography
        FROM PatientData
        WHERE cholesterol IS NOT NULL AND tomography IS NOT NULL
    ) s
    WHERE pd_inner.cholesterol IS NOT NULL AND pd_inner.tomography IS NOT NULL
) r ON 1=1 
-- JOIN condition (1=1) is a trick to always join every row in 'pd' with this subquery result.
-- After calculating the mean values and the 'b' coefficient, 
-- we can then predict the missing tomography values using a linear regression formula.
-- This sets the tomography value for rows where it's missing (NULL) but where we have a cholesterol value.
SET pd.tomography = (s.mean_tomography - r.b * s.mean_cholesterol) + r.b * pd.cholesterol
WHERE pd.tomography IS NULL AND pd.cholesterol IS NOT NULL;

