#!/bin/bash
# Run the closure grader inside the LCG view (Rivet 4.1.2, YODA 2.1.2).
# Usage: run_closure.sh --reference DIR --candidate DIR --samples samples.json \
#                       --workdir DIR --out report.json [--nevents N] [--only S1 S2]
# The LCG setup script trips over `set -u`, so source it before the strict flags.
LCG_VIEW=${LCG_VIEW:-/cvmfs/sft.cern.ch/lcg/views/LCG_110a/x86_64-el9-gcc14-opt}
source "$LCG_VIEW/setup.sh" >/dev/null 2>&1
set -eo pipefail
exec python3 "$(dirname "$(readlink -f "$0")")/closure.py" "$@"
