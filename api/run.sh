#!/bin/bash

uvicorn api.app.main:app --reload --reload-dir api --reload-dir yards_py --port 8000 --env-file ./api/.env