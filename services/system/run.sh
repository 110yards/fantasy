#!/bin/bash

uvicorn services.system.app.main:app --reload --reload-dir services/system --reload-dir yards_py --port 8001 --env-file ./services/system/.env