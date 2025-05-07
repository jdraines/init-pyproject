#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Running tests in $SCRIPT_DIR"
pytest -vvv --cov-config=$SCRIPT_DIR/.coveragerc --cov=skaf --cov-report=term-missing $SCRIPT_DIR
