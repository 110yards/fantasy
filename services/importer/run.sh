#!/bin/bash

uvicorn app.main:app --reload --reload-dir app --port 8002 --env-file .env
