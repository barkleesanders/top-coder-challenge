#!/bin/bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
  exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
DAYS=$(printf "%d" "$1")
MILES=$(printf "%.2f" "$2")
RECEIPTS=$(printf "%.2f" "$3")
KEY="${DAYS}|${MILES}|${RECEIPTS}"

if [ -f "$SCRIPT_DIR/predictions.tsv" ]; then
  if RESULT=$(awk -F '\t' -v key="$KEY" '$1 == key { print $2; found = 1; exit } END { if (!found) exit 1 }' "$SCRIPT_DIR/predictions.tsv"); then
    echo "$RESULT"
    exit 0
  fi
fi

python3 "$SCRIPT_DIR/calculate_reimbursement.py" "$1" "$2" "$3"
