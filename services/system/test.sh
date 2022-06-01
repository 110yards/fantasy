#!/bin/bash

flake8 app tests --count --show-source --statistics
pytest tests/unit --disable-warnings
pytest tests/integration --disable-warnings