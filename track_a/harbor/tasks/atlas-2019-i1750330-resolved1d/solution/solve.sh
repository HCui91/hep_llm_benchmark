#!/bin/bash
# Oracle: install the official routine, renamed to BENCH_0001.
set -e
D="$(cd "$(dirname "$0")" && pwd)"
cp "$D"/BENCH_0001.cc "$D"/BENCH_0001.info "$D"/BENCH_0001.plot /app/
