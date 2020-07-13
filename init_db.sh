#!/bin/bash
FILE=src/development.db
if test -f "$FILE"; then
  rm -rf "$FILE"
fi
python3 src/models.py
python3 src/populate_db.py
echo "Database has been initialized and populated."
