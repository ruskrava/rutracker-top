#!/usr/bin/env bash
set -e

OUT="AUDIT_PROJECT.md"
PORT=8009

echo "# AUDIT: rutracker-top" > "$OUT"
echo >> "$OUT"
echo "Generated: $(date)" >> "$OUT"
echo "Location: $(pwd)" >> "$OUT"
echo >> "$OUT"

echo "## 1. Project goals, rules, API contract (README)" >> "$OUT"
echo >> "$OUT"
sed -n '1,800p' README.md >> "$OUT" || echo "README.md NOT FOUND" >> "$OUT"
echo >> "$OUT"

echo "## 2. Execution environment" >> "$OUT"
echo '```' >> "$OUT"
whoami >> "$OUT"
pwd >> "$OUT"
uname -a >> "$OUT"
python3 --version 2>&1 || true >> "$OUT"
which python3 2>&1 || true >> "$OUT"
echo '```' >> "$OUT"
echo >> "$OUT"

echo "## 3. Git state" >> "$OUT"
echo '```' >> "$OUT"
git rev-parse --abbrev-ref HEAD >> "$OUT"
git rev-parse HEAD >> "$OUT"
git status >> "$OUT"
git remote -v >> "$OUT"
echo '```' >> "$OUT"
echo >> "$OUT"

echo "## 4. Project structure (depth 4)" >> "$OUT"
echo '```' >> "$OUT"
find . -maxdepth 4 ! -path "./.git/*" ! -path "./.venv/*" >> "$OUT"
echo '```' >> "$OUT"
echo >> "$OUT"
echo "## 5. Backend: app/api.py (FULL)" >> "$OUT"
sed -n '1,2000p' app/api.py >> "$OUT"
echo >> "$OUT"

echo "## 6. Backend: app/parser.py (FULL)" >> "$OUT"
sed -n '1,2000p' app/parser.py >> "$OUT"
echo >> "$OUT"

echo "## 7. UI: app/static/app.js (FULL)" >> "$OUT"
sed -n '1,2000p' app/static/app.js >> "$OUT"
echo >> "$OUT"

echo "## 8. UI: HTML files" >> "$OUT"
for f in app/static/*.html; do
  echo "### $f" >> "$OUT"
  sed -n '1,800p' "$f" >> "$OUT"
  echo >> "$OUT"
done

echo "## 9. Tests" >> "$OUT"
echo '```' >> "$OUT"
ls -l tests >> "$OUT"
echo '```' >> "$OUT"
echo >> "$OUT"

for f in tests/*.py; do
  echo "### $f" >> "$OUT"
  sed -n '1,800p' "$f" >> "$OUT"
  echo >> "$OUT"
done

echo "## 10. Docker" >> "$OUT"
echo "### Dockerfile" >> "$OUT"
sed -n '1,800p' Dockerfile >> "$OUT"
echo >> "$OUT"

echo "### docker-compose.yml" >> "$OUT"
sed -n '1,800p' docker-compose.yml >> "$OUT"
echo >> "$OUT"

echo "## 11. Persist & data" >> "$OUT"
echo '```' >> "$OUT"
ls -lh data >> "$OUT"
echo '```' >> "$OUT"
echo >> "$OUT"

echo "## END OF AUDIT" >> "$OUT"

echo
echo "Audit file created: $OUT"
echo "Serving on: http://<SERVER_IP>:$PORT/$OUT"
echo

python3 -m http.server "$PORT"
