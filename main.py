# -------------------------------
# 📦 Import Required Libraries
# -------------------------------
from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

# -------------------------------
# 🚀 Initialize FastAPI App
# -------------------------------
app = FastAPI()


# -------------------------------
# 🧬 Pydantic Model: Patient
# -------------------------------
class Patient(BaseModel):
    """
    Represents a Patient with personal and medical information.
    Automatically computes BMI and health verdict using @computed_field.
    """

    id: Annotated[str, Field(..., description='ID of the patient', example='P006')]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kilograms")]

    # Computed field for BMI
    @computed_field
    def bmi(self) -> float:
        """Calculates Body Mass Index (BMI) using formula: BMI = weight / (height^2)"""
        try:
            bmi = round(self.weight / (self.height ** 2), 2)
        except Exception:
            bmi = 0.0
        return bmi

    # Computed field for health verdict based on BMI
    @computed_field
    def verdict(self) -> str:
        """Returns a health verdict string based on BMI (Underweight, Normal, Overweight, Obese)."""
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        return "Obese"


# -------------------------------
# ✏️ Model for Updating a Patient
# -------------------------------
class PatientUpdate(BaseModel):
    """
    Used for partial updates of patient records.
    All fields are optional.
    """
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


# -------------------------------
# 🧾 Utility Functions for Data I/O
# -------------------------------

def load_data():
    """
    Loads patient data from 'patients.json' file.
    Returns a dictionary of patient records.
    """
    try:
        with open('patients.json', 'r') as f:
            data = json.load(f)
            # Ensure we return a dict
            if isinstance(data, dict):
                return data
            return {}
    except FileNotFoundError:
        # If file doesn't exist, create an empty DB and return {}
        with open('patients.json', 'w') as f:
            json.dump({}, f)
        return {}
    except json.JSONDecodeError:
        # If file is corrupt, warn and return empty dict (do not crash import)
        return {}


def save_data(data):
    """
    Saves the updated patient data dictionary into 'patients.json' file.
    """
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=2)


# -------------------------------
# 🌐 Basic API Routes
# -------------------------------

@app.get("/")
def hello():
    """Root endpoint to confirm API is running."""
    return {'message': "Patients Management System API"}


@app.get("/about")
def about():
    """Provides basic information about this API."""
    return {'message': "A fully functional API to manage your patient records"}


@app.get('/view')
def view():
    """Fetches and returns all patient records."""
    data = load_data()
    return data


# -------------------------------
# 🔍 Get a Specific Patient by ID
# -------------------------------
@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient in the DB", example="P001")):
    """
    Retrieve details of a specific patient using their unique ID.
    Raises 404 error if patient not found.
    """
    data = load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code=404, detail='Patient not found')


# -------------------------------
# 📊 Sort Patients by a Field
# -------------------------------
@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort on the basis of weight, height or bmi"),
    order: str = Query("asc", description="Sort order: asc (ascending) or desc (descending)")
):
    """
    Sorts all patient records by a given attribute (weight, height, or BMI).
    Allows choosing ascending or descending order.
    """
    valid_fields = ['weight', 'height', 'bmi']

    # Validate sort field
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field! Choose from {valid_fields}')

    # Validate order type
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order! Choose either asc or desc')

    data = load_data()
    sort_order = True if order == 'desc' else False  # reverse=True for descending

    # Sort the data based on the chosen field
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


# -------------------------------
# ➕ Create a New Patient Record
# -------------------------------
@app.post('/create')
def create_patient(patient: Patient):
    """
    Adds a new patient record to the database.
    Prevents duplicate entries based on patient ID.
    """
    data = load_data()

    # Check for duplicate patient ID
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # Add the new patient (excluding ID inside nested dict)
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)  # Save updated data back to file

    return JSONResponse(status_code=201, content={'message': 'Patient created successfully'})


# -------------------------------
# 🛠️ Update an Existing Patient
# -------------------------------
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    """
    Updates an existing patient's information.
    Automatically recalculates BMI and verdict after update.
    """
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    # Merge updated fields into existing record
    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    # Convert updated record into Pydantic model to recompute BMI & verdict
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    # model_dump will include computed fields (bmi, verdict). Exclude id because it's the dict key.
    new_record = patient_pydantic_obj.model_dump(exclude={'id'})

    # Replace updated record with the serialized pydantic model (computed fields preserved)
    data[patient_id] = new_record

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Patient updated successfully'})


# -------------------------------
# ❌ Delete a Patient Record
# -------------------------------
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    """
    Deletes a patient record from the database using patient ID.
    Raises 404 if the patient does not exist.
    """
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Patient deleted successfully'})
