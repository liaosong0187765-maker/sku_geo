#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-src}"

python -m unittest discover -s tests
python -m compileall -q src
python -m creator_passport generate examples/source_passport.json --out generated/demo
python -m creator_passport publish --out generated/demo --platform x --url https://x.com/example/status/123
python -m creator_passport monitor --out generated/demo --response-file examples/monitor_response_missing_citation.txt
python -m creator_passport check generated/demo

echo "verify.sh passed"
