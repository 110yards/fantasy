uvicorn services.api.app.main:app --reload --reload-dir services/api --reload-dir yards_py --port 8000 --env-file ./services/api/.env 
