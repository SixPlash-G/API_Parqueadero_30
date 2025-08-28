# API_Parqueadero_30

Service API for the web application **Parqueadero La 30**

This API allows you to manage users, clients, vehicles, parking lots, rates, entries, and payments.
It also includes an **ANPR (Automatic Number Plate Recognition)** module for automatic vehicle license plate detection.

## Setup

1. Create a virtual environment:
   - `python -m venv .venv`
2. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt`

## Run Application

Run in terminal `python -m uvicorn run:app`

## Maintaining

Generate requirements.txt: `pip freeze > requirements.txt`

### Reload Mode

Run in terminal `python -m uvicorn run:app --reload`

## Swagger

To open swagger go to `http://localhost:8000/docs` when the application is running.

## Run ANPR (Automatic Number Plate Recognition) locally

he project includes a license plate detection script (ANPR) located in the **src/plate_detection** folder..

1. Make sure the virtual environment is activated.
2. Run the script:
   - `python src\plate_detection\ANPR.py`

