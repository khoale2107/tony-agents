#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec python3 ab_tracker.py "$@"
