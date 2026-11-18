#!/bin/bash
# Recover the Herwig outputs of the first production run: Herwig wrote plain LHC-S<seed>-jNN.hepmc
# files (the FIFO name did not match), so gzip them here, check them, and clean up.
#SBATCH -p short
#SBATCH --mem=1G
#SBATCH -J hw7gz
#SBATCH --array=1-10
#SBATCH -t 02:00:00
#SBATCH -o hw7gz_%a.log
set -euo pipefail
W=${HEPBENCH_DATA:?set HEPBENCH_DATA}/samples/herwig7_ttbar
T=$(printf %02d $SLURM_ARRAY_TASK_ID); SEED=$((2000+SLURM_ARRAY_TASK_ID))
F=$W/job$T/LHC-S$SEED-j$T.hepmc
NEV=$(grep -c '^E ' "$F"); END=$(tail -c 300 "$F" | grep -c END_EVENT_LISTING || true)
echo "file $F events $NEV end_marker $END"
[ "$NEV" -eq 5000 ] && [ "$END" -ge 1 ] || { echo "INCOMPLETE, keeping $F"; exit 1; }
gzip -c "$F" > $W/herwig7_ttbar_$T.hepmc.gz.part && mv $W/herwig7_ttbar_$T.hepmc.gz.part $W/herwig7_ttbar_$T.hepmc.gz
rm -f "$F" $W/job$T/LHC-S1-j$T.hepmc $W/herwig7_ttbar_$T.hepmc.gz.stale 2>/dev/null || true
echo "done $(stat -c %s $W/herwig7_ttbar_$T.hepmc.gz) bytes"
