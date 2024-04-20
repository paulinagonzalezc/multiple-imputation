Data Wrangling

# Multiple Imputation for Medical Data

## Overview
This project implements a simplified version of multiple imputation to handle incomplete medical data from multiple sources. The focus is on probabilistically imputing missing data to enable further statistical analysis.

<img width="635" alt="image" src="https://github.com/paulinagonzalezc/multiple-imputation/assets/90674847/a878543b-6d89-4b28-97e7-1ce3ae1a7c4d">

## Project Description
I tackled the challenge of disparate and incomplete data in the Georgia Coverdell Acute Stroke Registry (GCASR) by imputing missing values using SQL and Python/pandas. The project facilitated the first step in multiple imputation, preparing the data for subsequent statistical methods like linear regression.

## Features
* SQL scripts to impute missing medical data across ten hospital tables.
* Python/pandas functions to mirror SQL data manipulation on dataframes.
* Linear regression application to estimate missing computed tomography times based on existing cholesterol levels.

<img width="759" alt="image" src="https://github.com/paulinagonzalezc/multiple-imputation/assets/90674847/b88bd6f0-366f-416e-beff-d5ca29f22f14">

### Imputation Strategies
* Age: Missing ages were filled with the median age from the respective hospital's data.
* Cholesterol Level: Missing values were replaced by the average cholesterol level for matching ages or the smallest value within a similar age bracket.
* Computed Tomography Time: Imputed using a one-dimensional linear regression trained on non-missing cholesterol levels.

## Tools Used
* MySQL for relational database management.
* Python with Pandas for dataframe manipulation.

## Results
The data was successfully wrangled into a format suitable for machine learning and statistical analysis, with missing values imputed as per the specifications.
