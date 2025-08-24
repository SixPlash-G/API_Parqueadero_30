# API_Parqueadero_30

Api de servicios para aplicación web parqueadero la 30

## Setup

1. Create a virtual environment: `py -m venv .venv`
2. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the application: `py app.py`

## Maintaining

1. Generate requirements.txt: `pip freeze > requirements.txt`

## Run Application

Run in terminal `py -m uvicorn run:app`

### Reload Mode

Run in terminal `py -m uvicorn run:app --reload`
