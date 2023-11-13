# Collection of methods to impute missing hospital data provided by file
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np


# Class that imputes estimated values for cells of a pandas DataFrame
# that are unknown, i.e., that are set to np.nan
class Impute:
    # Constructs a new Impute class with a given DataFrame called input_data
    # The DataFrame should have five attributes:
    # patientID, hospitalID, age, cholesterol, tomography
    def __init__(self, input_data):
        self.input_data = input_data

    # Given a hospital id, imputes the age of all patients
    # at that hospital who currently have np.nan for age
    # as the median of all patients at that hospital whose age is known.
    # Returns a DataFrame consisting of all patients whose age has changed.
    def impute_age(self, hospitalID):
        # Implement me!
        # Get the median age of patients with known age at the given hospitalID
        median_age = self.input_data.loc[
            (self.input_data["hospitalID"] == hospitalID)
            & (~self.input_data["age"].isnull()),
            "age",
        ].median()

        # Check if median age is NaN - if so, return an empty DataFrame
        if pd.isna(median_age):
            return pd.DataFrame(
                columns=["patientID", "age", "cholesterol", "tomography"]
            )

        # extracts the rows from input_data that match the boolean
        # .copy() at the end. This creates a new DataFrame that's a copy of the extracted rows
        changed_rows = self.input_data.loc[
            (self.input_data["hospitalID"] == hospitalID)
            & (self.input_data["age"].isnull())
        ].copy()

        # Impute the missing ages
        self.input_data.loc[
            (self.input_data["hospitalID"] == hospitalID)
            & (self.input_data["age"].isnull()),
            "age",
        ] = median_age

        # Return the changed rows# Directly update the 'changed_rows' DataFrame with the imputed age values.
        changed_rows["age"] = median_age

        # Return the 'changed_rows' DataFrame to see which rows had the age imputed.
        return changed_rows[
            ["patientID", "age", "cholesterol", "tomography"]
        ].reset_index(drop=True)

    # Given a hospital id, imputes the cholesterol level of all patients
    # at that hospital who currently have np.nan for cholesterol
    # as the average of all patients at that hospital with the same age.
    # Returns a DataFrame consisting of all patients whose cholesterol has changed.
    def impute_cholesterol_single_hospital(self, hospitalID):
        # Implement me!
        # 1.- Group patients by age within the specified hospital ID.
        # Filter patients from the specified hospital.
        hospital_patients = self.input_data[self.input_data["hospitalID"] == hospitalID]

        # Calculate the average cholesterol for each age in the hospital.
        average_cholesterol_per_age = hospital_patients.groupby("age")[
            "cholesterol"
        ].mean()

        # Find patients with missing cholesterol values.
        patients_with_nan_cholesterol = hospital_patients["cholesterol"].isnull()

        # Loop through each patient in the specified hospital.
        for idx, patient in hospital_patients[patients_with_nan_cholesterol].iterrows():
            # Find the average cholesterol for the age of the current patient.
            age = patient["age"]
            if pd.notnull(age):  # Check if the age is not NaN
                average_cholesterol = average_cholesterol_per_age.get(age, np.nan)
                # Update the cholesterol value if the average cholesterol is not NaN.
                if pd.notnull(average_cholesterol):
                    self.input_data.loc[idx, "cholesterol"] = average_cholesterol

        # Return the changed rows.
        changed_rows = self.input_data.loc[
            (self.input_data["hospitalID"] == hospitalID)
            & (self.input_data["cholesterol"].notnull())
            & patients_with_nan_cholesterol
        ]
        return changed_rows[
            ["patientID", "age", "cholesterol", "tomography"]
        ].reset_index(drop=True)

    # Imputes the cholesterol level of all patients at all hospitals
    # who currently have np.nan for cholesterol using as the lowest
    # known value of all patients whose age is in the same five-year bracket.
    # Returns a DataFrame consisting of all patients whose cholesterol has changed.
    def impute_cholesterol(self):
        # Implement me!
        # Create a new column for the five-year age brackets
        self.input_data["age_bracket"] = (self.input_data["age"] // 5) * 5

        # Find the minimum cholesterol for each age bracket across all hospitals
        min_cholesterol_per_bracket = (
            self.input_data.groupby("age_bracket")["cholesterol"].min().to_dict()
        )

        # Create a mask for rows with NaN cholesterol values
        nan_cholesterol_mask = self.input_data["cholesterol"].isnull()

        # Impute cholesterol for patients with missing values
        self.input_data.loc[nan_cholesterol_mask, "cholesterol"] = self.input_data.loc[
            nan_cholesterol_mask
        ].apply(
            lambda row: min_cholesterol_per_bracket.get(row["age_bracket"], np.nan),
            axis=1,
        )

        # Find the rows that have been changed
        changed_rows = self.input_data.loc[
            nan_cholesterol_mask & self.input_data["cholesterol"].notnull()
        ]

        # Remove the age bracket column as it's no longer needed
        changed_rows = changed_rows.drop("age_bracket", axis=1)

        # Return the rows with imputed cholesterol levels
        return changed_rows[
            ["patientID", "hospitalID", "age", "cholesterol", "tomography"]
        ].reset_index(drop=True)

    # Imputes the time to tomography of all patients at all hospitals
    # who currently have np.nan for tomography by interpolating the values
    # with linear regression trained over the cholesterol level as the independent variable.
    # Returns a DataFrame consisting of all patients whose tomography has changed.
    def impute_tomography(self):
        # Implement me!
        if self.input_data["cholesterol"].isnull().all():
            return pd.DataFrame()

        # Store original data for comparison

        original_data = self.input_data.copy()
        # Begin sanitization
        cols_to_sanitize = ["cholesterol", "tomography"]

        def get_majority_value(series):
            mode_val = series.mode()
            if len(mode_val) > 1 or len(series) == 1:
                return series  # Return the series unchanged
            else:
                return mode_val.iloc[0]

        majority_values = self.input_data.groupby("patientID")[
            cols_to_sanitize
        ].transform(get_majority_value)
        self.input_data[cols_to_sanitize] = majority_values
        # End sanitization
        # Extract rows where both cholesterol and tomography are not NaN
        training_data = self.input_data.dropna(subset=["cholesterol", "tomography"])

        # Fit the model
        model = LinearRegression()
        model.fit(training_data[["cholesterol"]], training_data["tomography"])

        # Predict tomography where it's NaN and cholesterol is not NaN
        to_predict = self.input_data.loc[
            self.input_data["tomography"].isnull()
            & self.input_data["cholesterol"].notnull(),
            ["cholesterol"],
        ]

        # Check if there is any data to predict
        if not to_predict.empty:
            predicted_tomography = model.predict(to_predict)

            # Update the original dataframe
            self.input_data.loc[to_predict.index, "tomography"] = predicted_tomography

        # Get rows that were changed during sanitization
        # changed_rows_sanitization = self.input_data[
        #     original_data[cols_to_sanitize] != self.input_data[cols_to_sanitize]
        # ].dropna(subset=cols_to_sanitize)

        # Determine rows changed during sanitization
        # changed_mask = (
        #     original_data[cols_to_sanitize] != self.input_data[cols_to_sanitize]
        # ).any(axis=1)
        changed_mask = (
            ~original_data[cols_to_sanitize].isna()
            & (original_data[cols_to_sanitize] != self.input_data[cols_to_sanitize])
        ).any(axis=1)
        changed_rows_sanitization = self.input_data[changed_mask]

        # Get rows where tomography was imputed
        changed_rows_imputation = self.input_data.loc[to_predict.index]

        # Combine the two sets of changed rows
        all_changed_rows = pd.concat(
            [changed_rows_sanitization, changed_rows_imputation]
        ).drop_duplicates()

        all_changed_rows["patientID"] = all_changed_rows["patientID"].astype(int)
        all_changed_rows["hospitalID"] = all_changed_rows["hospitalID"].astype(int)

        return all_changed_rows[
            ["patientID", "hospitalID", "age", "cholesterol", "tomography"]
        ].reset_index(drop=True)


# ---------------
# TESTS Debugging code


# def impute_tomography(data):
#     # Implement me!
#     # If all cholesterol values are NaN, return an empty dataframe
#     if data["cholesterol"].isnull().all():
#         return pd.DataFrame()
#     # Store original data for comparison
#     original_data = data.copy()
#     # Begin sanitization
#     cols_to_sanitize = ["cholesterol", "tomography"]

#     def get_majority_value(series):
#         mode_val = series.mode()
#         if len(mode_val) > 1 or len(series) == 1:
#             return series  # Return the series unchanged
#         else:
#             return mode_val.iloc[0]

#     majority_values = data.groupby("patientID")[cols_to_sanitize].transform(
#         get_majority_value
#     )
#     data[cols_to_sanitize] = majority_values

#     # End sanitization
#     # Extract rows where both cholesterol and tomography are not NaN
#     training_data = data.dropna(subset=["cholesterol", "tomography"])

#     # Fit the model
#     model = LinearRegression()
#     model.fit(training_data[["cholesterol"]], training_data["tomography"])

#     # Predict tomography where it's NaN and cholesterol is not NaN
#     to_predict = data.loc[
#         data["tomography"].isnull() & data["cholesterol"].notnull(),
#         ["cholesterol"],
#     ]
#     print("to_predict")
#     print(to_predict)

#     # Check if there is any data to predict
#     if not to_predict.empty:
#         predicted_tomography = model.predict(to_predict)

#         # Update the original dataframe
#         data.loc[to_predict.index, "tomography"] = predicted_tomography

#     # Get rows that were changed during sanitization
#     changed_rows_sanitization = data[
#         original_data[cols_to_sanitize] != data[cols_to_sanitize]
#     ].dropna(subset=cols_to_sanitize)

#     # Determine rows changed during sanitization
#     # changed_mask = (original_data[cols_to_sanitize] != data[cols_to_sanitize]).any(
#     #     axis=1
#     # )
#     changed_mask = (
#         ~original_data[cols_to_sanitize].isna()
#         & (original_data[cols_to_sanitize] != data[cols_to_sanitize])
#     ).any(axis=1)

#     changed_rows_sanitization = data[changed_mask]

#     # Get rows where tomography was imputed
#     changed_rows_imputation = data.loc[to_predict.index]

#     # Combine the two sets of changed rows
#     all_changed_rows = pd.concat(
#         [changed_rows_sanitization, changed_rows_imputation]
#     ).drop_duplicates()

#     all_changed_rows["patientID"] = all_changed_rows["patientID"].astype(int)
#     all_changed_rows["hospitalID"] = all_changed_rows["hospitalID"].astype(int)

#     return all_changed_rows[
#         ["patientID", "hospitalID", "age", "cholesterol", "tomography"]
#     ].reset_index(drop=True)


# input_frame = pd.DataFrame(
#     {
#         "patientID": [1, 2, 3, 4, 5],
#         "hospitalID": [10, 20, 30, 40, 50],
#         "age": [25, 35, 45, 55, 65],
#         "cholesterol": [200.0, 220.0, 230.0, 240.0, 250.0],
#         "tomography": [np.nan, np.nan, np.nan, np.nan, np.nan],
#     }
# )

# result = impute_tomography(input_frame)
# print(result)
# print(result.dtypes)

# expected_output_frame = pd.DataFrame(
#     {
#         "patientID": [1, 2, 3, 4, 5],
#         "hospitalID": [10, 20, 30, 40, 50],
#         "age": [25, 35, 45, 55, 65],
#         "cholesterol": [200.0, 220.0, 230.0, 240.0, 250.0],
#         "tomography": [300.0, 320.0, 340.0, 360.0, 380.0],
#     }
# )

# print(expected_output_frame.dtypes)
# print(expected_output_frame)

# # Check if the result matches the expected output
# if expected_output_frame.equals(result.reset_index(drop=True)):
#     print("The result matches the expected output.")
# else:
#     print("The result does not match the expected output.")
