import streamlit as st
import pandas as pd
import random
import subprocess
import sys
from datetime import datetime

# ------------------------------
# Install Faker if missing
# ------------------------------
try:
    from faker import Faker
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
    from faker import Faker

# ------------------------------
# App Title & Description
# ------------------------------
st.title("📊 Synthetic EHR Data Simulation: OMOP Person & Condition Tables")
st.write("""
This interactive app simulates Electronic Health Record (EHR)-like data
and transforms it to the OMOP Common Data Model (CDM) person and condition_occurrence tables.
All data is **fake** and safe for educational purposes.
""")

# ------------------------------
# Initialize Faker
# ------------------------------
fake = Faker()
Faker.seed(123)
random.seed(123)

# ------------------------------
# Step 1: Generate Fake Patients
# ------------------------------
def generate_fake_patients(n=10):
    races = ['White', 'Black', 'Asian', 'Other']
    ethnicities = ['Not Hispanic or Latino', 'Hispanic or Latino']
    data = []
    for i in range(n):
        gender = random.choice(['Male', 'Female'])
        race = random.choice(races)
        ethnicity = random.choice(ethnicities)
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90)
        data.append({
            "person_source_value": fake.unique.uuid4(),
            "full_name": fake.name_male() if gender == 'Male' else fake.name_female(),
            "gender": gender,
            "birthdate": birthdate,
            "address": fake.address(),
            "phone": fake.phone_number(),
            "email": fake.email(),
            "race": race,
            "ethnicity": ethnicity
        })
    df = pd.DataFrame(data)
    df["birthdate"] = pd.to_datetime(df["birthdate"])
    return df

num_patients = st.slider("Select number of patients to generate", 5, 50, 10)
original_data = generate_fake_patients(num_patients)
st.write("### Sample Fake Patients Data")
st.dataframe(original_data.head())

# ------------------------------
# Step 2: Mapping Functions for OMOP Concepts
# ------------------------------
def map_gender(gender):
    return {'Male': 8507, 'Female': 8532}.get(gender, 0)

def map_race(race):
    return {'White': 8527, 'Black': 8516, 'Asian': 8515, 'Other': 8529}.get(race, 0)

def map_ethnicity(ethnicity):
    return {'Not Hispanic or Latino': 38070399, 'Hispanic or Latino': 38003563}.get(ethnicity, 0)

# ------------------------------
# Step 3: Convert to OMOP Person Table
# ------------------------------
def convert_to_omop_person(df):
    return pd.DataFrame({
        "person_id": range(1, len(df) + 1),
        "gender_concept_id": df["gender"].map(map_gender),
        "year_of_birth": df["birthdate"].dt.year,
        "month_of_birth": df["birthdate"].dt.month,
        "day_of_birth": df["birthdate"].dt.day,
        "birth_datetime": df["birthdate"],
        "race_concept_id": df["race"].map(map_race),
        "ethnicity_concept_id": df["ethnicity"].map(map_ethnicity),
        "location_id": None,
        "provider_id": None,
        "care_site_id": None,
        "person_source_value": df["person_source_value"],
        "gender_source_value": df["gender"],
        "gender_source_concept_id": 0,
        "race_source_value": df["race"],
        "race_source_concept_id": 0,
        "ethnicity_source_value": df["ethnicity"],
        "ethnicity_source_concept_id": 0
    })

omop_person = convert_to_omop_person(original_data)
st.write("### OMOP Person Table")
st.dataframe(omop_person.head())

# ------------------------------
# Step 4: Simulate Condition Occurrence Table
# ------------------------------
icd_to_omop = {"E11.9": 201826, "I10": 320128, "J45.909": 317009, "F32.9": 440383}
icd_codes = list(icd_to_omop.keys())

def generate_full_condition_occurrence(person_df):
    conditions = []
    for i, person in person_df.iterrows():
        num_conditions = random.randint(1, 3)
        for _ in range(num_conditions):
            icd = random.choice(icd_codes)
            start_date = fake.date_between(start_date='-5y', end_date='-6m')
            end_date = fake.date_between(start_date=start_date, end_date='today')
            conditions.append({
                "condition_occurrence_id": len(conditions) + 1,
                "person_id": person['person_id'],
                "condition_concept_id": icd_to_omop[icd],
                "condition_start_date": start_date,
                "condition_start_datetime": pd.to_datetime(start_date),
                "condition_end_date": end_date,
                "condition_end_datetime": pd.to_datetime(end_date),
                "condition_type_concept_id": 32020,
                "stop_reason": None,
                "provider_id": None,
                "visit_occurrence_id": None,
                "visit_detail_id": None,
                "condition_source_value": icd,
                "condition_source_concept_id": 0,
                "condition_status_concept_id": 0
            })
    return pd.DataFrame(conditions)

condition_occurrence = generate_full_condition_occurrence(omop_person)
st.write("### Simulated Condition Occurrence Table")
st.dataframe(condition_occurrence.head())

# ------------------------------
# Step 5: Discussion Prompts
# ------------------------------
st.write("""
#### Discussion Prompts

* Why is it important to standardize diagnosis codes?
* How might real-world ETL handle ICD-9, ICD-10, and SNOMED mappings?
* What tools can help map source codes to OMOP concepts (e.g., Usagi)?
""")
