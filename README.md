# API_Parqueadero_30

Api de servicios para aplicación web parqueadero la 30

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