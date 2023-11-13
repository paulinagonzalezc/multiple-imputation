import pandas as pd
import math
from sqlalchemy import Table, create_engine
from sqlalchemy import create_engine, Column, Integer, Float, MetaData, Table
from sqlalchemy import and_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import os

# MySQL database configuration
host = "localhost:3306"
database = "db"
user = "user"
password = "password"

# Create a MySQL engine using SQLAlchemy
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
Session = sessionmaker(bind=engine)
session = Session()

# Step 3: Define a Model Class
Base = declarative_base()
table_name = "PatientData"  # Replace with the name of the table you want to drop


class Patient(Base):
    __tablename__ = table_name

    patientID = Column(Integer, primary_key=True)
    hospitalID = Column(Integer, primary_key=True)
    age = Column(Float, nullable=True)
    cholesterol = Column(Float, nullable=True)
    tomography = Column(Float, nullable=True)


# Step 3: Reflect the Database (optional but useful to define tables)
metadata = MetaData()
metadata.reflect(bind=engine)

# Drop a Specific Table

table_to_drop = Table(table_name, metadata, autoload=True, autoload_with=engine)
table_to_drop.drop(engine)

Base.metadata.create_all(engine)

folder_path = "files"


def updatePatient(patientID, hospitalID, new_record):
    print("Updating")
    patient = (
        session.query(Patient)
        .filter(and_(Patient.patientID == patientID, Patient.hospitalID == hospitalID))
        .first()
    )
    # updated_patient = {
    #     "patientID": new_record.patientID if patient.patientID == None else patient.patientID,
    #     "hospitalID": new_record.hospitalID if patient.hospitalID == None else patient.hospitalID,
    #     "age": new_record.age if patient.age == None else patient.age,
    #     "cholesterol": new_record.cholesterol if patient.cholesterol == None else patient.cholesterol,
    #     "tomography": new_record.tomography if patient.tomography == None else patient.tomography,
    # }
    if patient.age == None:
        patient.age = new_record.age
    if patient.cholesterol == None:
        patient.cholesterol = new_record.cholesterol
    if patient.tomography == None:
        patient.tomography = new_record.tomography

    session.commit()


def insertRecords(filepath):
    data = pd.read_csv(filepath)
    df = pd.DataFrame(data)
    # Extract the hospital number from the file name
    hospital_number = int(filepath[-5])

    rows = df.values.tolist()
    i = 0
    while i < len(rows):
        record = rows[i]
        patientID = record[0]
        age = record[1]
        cholesterol = record[2]
        hospitalID = hospital_number
        tomography = record[3]

        # Step 5: Create a New Record
        new_record = Patient(
            patientID=patientID,
            hospitalID=hospitalID,
            age=None if math.isnan(age) else age,
            cholesterol=None if math.isnan(cholesterol) else cholesterol,
            tomography=None if math.isnan(tomography) else tomography,
        )

        # Use the filter method to apply conditions on both properties
        records = (
            session.query(Patient)
            .filter(Patient.hospitalID == hospitalID, Patient.patientID == patientID)
            .all()
        )

        if len(records) > 0:
            for result in records:
                updatePatient(result.patientID, result.hospitalID, new_record)
        else:
            session.add(new_record)
        # Check if there are duplicate records (two or more)

        i = i + 1

    # Step 6: Add and Commit
    session.commit()


# Check if the folder exists
if os.path.exists(folder_path) and os.path.isdir(folder_path):
    # List all files in the folder
    file_list = os.listdir(folder_path)

    # Iterate through file names
    for file_name in file_list:
        # Print each file name
        print(f"Inserting {file_name}")
        insertRecords(f"files/{file_name}")

else:
    print(f"The folder '{folder_path}' does not exist or is not a directory.")
# MySQL database configuration
