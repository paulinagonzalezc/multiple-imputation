# Test cases for the Impute class.
# Only some of the mocked objects (and therefore expected output) are
# provided in advance of grading and these correspond to easy test cases.
# Your implementation should anticipate ways in which these mocks
# or tests could be more complex, as well as design mocks
# for some disclosed but not written test cases.
import unittest
import time
import timeout_decorator
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from PatientImputation import Impute


# Straight-forward case: single value median
class TestCase01(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_median_age(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 1, 1],
                "age": [15.0, np.nan, np.nan, 20.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [2],
                "age": [20.0],
                "cholesterol": [np.nan],
                "tomography": [100.0],
            }
        )

        assert_frame_equal(expected_output_frame, patient_imputer.impute_age(1))


# no values known = no change
class TestCase02(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_median_age(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 1, 1, 1],
                "age": [15.0, np.nan, np.nan, np.nan],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": list(),
                "age": list(),
                "cholesterol": list(),
                "tomography": list(),
            }
        )

        self.assertTrue(patient_imputer.impute_age(1).empty)


# compute median of two values with two hospitals to impute
class TestCase03(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_median_age(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3, 4, 5],
                "hospitalID": [2, 2, 2, 1, 1, 1],
                "age": [15.0, np.nan, 17.0, np.nan, 20.0, 20.2],
                "cholesterol": [0.0, 42.0, np.nan, 10.0, 15.0, np.nan],
                "tomography": [0.0, 12.0, 100.0, np.nan, np.nan, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [3],
                "age": [20.1],
                "cholesterol": [10.0],
                "tomography": [np.nan],
            }
        )

        assert_frame_equal(expected_output_frame, patient_imputer.impute_age(1))


# compute median of three values
class TestCase04(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_median_age(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [1, 1, 1, 1],
                "age": [15.0, 16.1, 35.0, np.nan],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [3],
                "age": [16.1],
                "cholesterol": [10.0],
                "tomography": [np.nan],
            }
        )

        assert_frame_equal(expected_output_frame, patient_imputer.impute_age(1))


# Straight-forward case: two value mean
class TestCase06(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_average_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 0, 0],
                "age": [15.0, 24.0, 24.0, 24.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [2],
                "age": [24.0],
                "cholesterol": [26.0],
                "tomography": [100.0],
            }
        )

        assert_frame_equal(
            expected_output_frame, patient_imputer.impute_cholesterol_single_hospital(0)
        )


# null case: nobody matches the same age
class TestCase07(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_average_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 0, 1],
                "age": [15.0, 24.0, 26.0, 26.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0],
            }
        )
        patient_imputer = Impute(input_frame)

        self.assertTrue(patient_imputer.impute_cholesterol_single_hospital(0).empty)


# multiple imputation case: three values to impute
class TestCase08(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_average_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3, 4],
                "hospitalID": [10, 10, 10, 10, 10],
                "age": [15.0, 15.0, 24.0, 24.0, 24.0],
                "cholesterol": [0.0, np.nan, np.nan, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [1, 2, 3],
                "age": [15.0, 24.0, 24.0],
                "cholesterol": [0.0, 10.0, 10.0],
                "tomography": [12.0, 100.0, 87.0],
            }
        )

        assert_frame_equal(
            expected_output_frame,
            patient_imputer.impute_cholesterol_single_hospital(10),
        )


# Straight-forward case: two value age bracket
class TestCase11(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_age_bracket_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 0, 0],
                "age": [19.0, 24.0, 24.0, 20.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [2],
                "hospitalID": [0],
                "age": [24.0],
                "cholesterol": [10.0],
                "tomography": [100.0],
            }
        )

        actual_output_frame = patient_imputer.impute_cholesterol()
        actual_output_frame["cholesterol"].round(0)

        assert_frame_equal(expected_output_frame, actual_output_frame)


# null case: nobody else in age bracket
class TestCase12(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_age_bracket_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 1, 2],
                "age": [19.0, 30.0, 25.0, 35.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0],
            }
        )
        patient_imputer = Impute(input_frame)

        self.assertTrue(patient_imputer.impute_cholesterol().empty)


# Straight-forward case: from different hospitals
class TestCase13(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_age_bracket_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 1, 2],
                "age": [19.0, 24.0, 24.0, 20.0],
                "cholesterol": [0.0, 42.0, np.nan, 10.0],
                "tomography": [0.0, 12.0, 100.0, 87.0],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [2],
                "hospitalID": [1],
                "age": [24.0],
                "cholesterol": [10.0],
                "tomography": [100.0],
            }
        )

        assert_frame_equal(expected_output_frame, patient_imputer.impute_cholesterol())


# Multiple imputation same age bracket
class TestCase14(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_age_bracket_cholesterol(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3, 4],
                "hospitalID": [0, 0, 1, 2, 4],
                "age": [19.0, 24.0, 23.0, 20.0, 20.0],
                "cholesterol": [0.0, np.nan, np.nan, 10.0, 25.0],
                "tomography": [0.0, 12.0, 100.0, 87.0, 42.0],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [1, 2],
                "hospitalID": [0, 1],
                "age": [24.0, 23.0],
                "cholesterol": [10.0, 10.0],
                "tomography": [12.0, 100.0],
            }
        )

        assert_frame_equal(expected_output_frame, patient_imputer.impute_cholesterol())


# simple case: interpolate between two values
class TestCase16(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_tomography(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 3],
                "hospitalID": [0, 0, 2],
                "age": [19.0, 24.0, 20.0],
                "cholesterol": [0.0, 100.0, 10.0],
                "tomography": [0.0, 200.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [3],
                "hospitalID": [2],
                "age": [20.0],
                "cholesterol": [10.0],
                "tomography": [20.0],
            }
        )

        actual_output_frame = patient_imputer.impute_tomography()
        actual_output_frame["tomography"].round(0)

        assert_frame_equal(expected_output_frame, actual_output_frame)


# Not all y-values are known
class TestCase17(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_tomography(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 1, 2],
                "age": [19.0, 24.0, 24.0, 20.0],
                "cholesterol": [0.0, 100.0, np.nan, 10.0],
                "tomography": [0.0, 200.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [3],
                "hospitalID": [2],
                "age": [20.0],
                "cholesterol": [10.0],
                "tomography": [20.0],
            }
        )

        actual_output_frame = patient_imputer.impute_tomography()
        actual_output_frame["tomography"].round(0)

        assert_frame_equal(expected_output_frame, actual_output_frame)


# No x-values are known
class TestCase18(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_tomography(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [0, 1, 2, 3],
                "hospitalID": [0, 0, 1, 2],
                "age": [19.0, 24.0, 24.0, 20.0],
                "cholesterol": [np.nan, np.nan, np.nan, np.nan],
                "tomography": [0.0, 200.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        self.assertTrue(patient_imputer.impute_tomography().empty)


# Sanitisation required first
class TestCase19(unittest.TestCase):
    @timeout_decorator.timeout(15)
    def test_tomography(self):
        input_frame = pd.DataFrame(
            {
                "patientID": [1, 1, 1, 2, 3],
                "hospitalID": [4, 0, 1, 1, 2],
                "age": [np.nan, 19.0, 24.0, np.nan, 20.0],
                "cholesterol": [0.0, 0.0, 42.0, 100.0, 20.0],
                "tomography": [0.0, 200.0, 0.0, 100.0, np.nan],
            }
        )
        patient_imputer = Impute(input_frame)

        expected_output_frame = pd.DataFrame(
            {
                "patientID": [1, 1, 3],
                "hospitalID": [0, 1, 2],
                "age": [19.0, 24.0, 20.0],
                "cholesterol": [0.0, 0.0, 20.0],
                "tomography": [0.0, 0.0, 20.0],
            }
        )

        actual_output_frame = patient_imputer.impute_tomography()
        actual_output_frame["age"].round(0)
        actual_output_frame["cholesterol"].round(0)
        actual_output_frame["tomography"].round(0)

        assert_frame_equal(expected_output_frame, actual_output_frame)


# Run all unit tests above.
unittest.main(argv=[""], verbosity=2, exit=False)
