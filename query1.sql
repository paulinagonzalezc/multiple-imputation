-- Query1.sql
-- imputes the missing data in the `age` field 
-- of a hospital with the median of all entries
-- from the same hospital, given schema:
-- Data(patientID, hospitalID, age, cholesterol, tomography).
-- For example, given relation instance:
-- {(0,0,15,0,0), (1,0,NULL,42,12), (2,1,NULL,NULL,100), (3,1,20,10,NULL)}
-- this query should transform it into the following instance:
--  {(0,0,15,0,0), (1,0,15,42,12), (2,1,20,NULL,100), (3,1,20,10,NULL)}

-- REPLACE THIS LINE WITH YOUR QUERY AND SUBMIT THIS FILE.

UPDATE PatientData pd
JOIN (
    SELECT 
        a.hospitalID,
        CASE
            WHEN COUNT(*) % 2 = 1 THEN
                MAX(IF(a.row_num = b.row_num, a.age, NULL))
            ELSE
                AVG(DISTINCT IF(a.row_num IN (b.row_num, b.row_num + 1), a.age, NULL))
        END AS MedianAge
    FROM
        (
            SELECT 
                hospitalID, age,
                @row_num := IF(@prev_hospital = hospitalID, @row_num + 1, 1) AS row_num,
                @prev_hospital := hospitalID
            FROM 
                PatientData,
                (SELECT @row_num := 0, @prev_hospital := NULL) AS init
            WHERE 
                age IS NOT NULL
            ORDER BY 
                hospitalID, age
        ) AS a
    JOIN 
        (
            SELECT hospitalID, CEIL(COUNT(*) / 2) AS row_num
            FROM PatientData
            WHERE age IS NOT NULL
            GROUP BY hospitalID
        ) AS b
    ON a.hospitalID = b.hospitalID
    GROUP BY 
        a.hospitalID
) AS medians
ON pd.hospitalID = medians.hospitalID
SET pd.age = medians.MedianAge
WHERE pd.age IS NULL;
