#!/bin/bash
#SBATCH -p short
#SBATCH --mem=4G
#SBATCH -J hw7tt
#SBATCH --array=1-10
#SBATCH -t 12:00:00
#SBATCH -o hw7tt_%a.log
# Needs HEPBENCH_DATA set (exported to the job) and LHC.run made once with:
#   cd $W; Herwig read --repo=$D/HerwigDefaults.rpo -i $D herwig7_ttbar.in
# HepMC output goes through a FIFO into gzip (no uncompressed file on disk).
source /cvmfs/sft.cern.ch/lcg/views/LCG_110a/x86_64-el9-gcc14-opt/setup.sh
W=${HEPBENCH_DATA:?set HEPBENCH_DATA}/samples/herwig7_ttbar
N=$SLURM_ARRAY_TASK_ID; T=$(printf %02d $N)
mkdir -p $W/job$T && cd $W/job$T
# Herwig names its output after the seed (LHC-S<seed>-j<tag>.hepmc), so the FIFO
# must carry the same name; a mismatch leaves gzip waiting forever.
FIFO=LHC-S$((2000+N))-j$T.hepmc
mkfifo $FIFO
gzip -c < $FIFO > $W/herwig7_ttbar_$T.hepmc.gz &
GZ=$!
START=$(date +%s)
Herwig run ../LHC.run -s $((2000+N)) -N 5000 -t j$T > run.stdout 2>&1
RC=$?
wait $GZ
echo "walltime_s $(( $(date +%s)-START )) rc $RC"
rm -f $FIFO LHC-S$((2000+N))-j$T.log   # log is large
