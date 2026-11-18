#!/bin/bash
#SBATCH -p short
#SBATCH --mem=4G
#SBATCH -J py8ttrad
#SBATCH --array=1-10
#SBATCH -t 12:00:00
#SBATCH -o py8ttrad_%a.log
# Needs HEPBENCH_DATA set (exported to the job).
# Writes HepMC3 ASCII through a named pipe into gzip (no uncompressed file on disk).
source /cvmfs/sft.cern.ch/lcg/views/LCG_110a/x86_64-el9-gcc14-opt/setup.sh
B=${HEPBENCH_DATA:?set HEPBENCH_DATA}/samples
N=$SLURM_ARRAY_TASK_ID
OUT=$B/pythia8_ttbar_radup/pythia8_ttbar_radup_$(printf %02d $N).hepmc.gz
FIFO=${TMPDIR:-/tmp}/py8_$SLURM_JOB_ID_$N.fifo; mkfifo $FIFO
gzip -c < $FIFO > $OUT &
GZ=$!
START=$(date +%s)
$B/pythia8_ttbar_radup_main $((1000+N)) 5000 $FIFO
RC=$?
wait $GZ; rm -f $FIFO
echo "walltime_s $(( $(date +%s)-START )) rc $RC"
