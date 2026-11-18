#!/bin/bash
# Grade /app/BENCH_0001.* against the reference routine.
mkdir -p /logs/verifier /tmp/cand
# The hepstore image keeps the YODA/Rivet Python bindings and libraries off the
# default paths.
export LD_LIBRARY_PATH=$(yoda-config --libdir):$(rivet-config --libdir):${LD_LIBRARY_PATH:-}
export PYTHONPATH=$(rivet-config --pythonpath):${PYTHONPATH:-}
rm -f /tmp/cand/*
for e in cc info plot; do
  [ -f /app/BENCH_0001.$e ] && cp /app/BENCH_0001.$e /tmp/cand/
done
python3 /tests/closure.py --reference /tests/reference --candidate /tmp/cand \
  --samples /tests/samples.json \
  --select '^d(0[2468]|[1-4][02468]|5[02])-x01-y01$' --nevents 80 \
  --workdir /tmp/grade --out /logs/verifier/report.json \
  --reward /logs/verifier/reward.json
rc=$?
[ -f /logs/verifier/reward.json ] || echo '{"pass_fraction": 0.0}' > /logs/verifier/reward.json
exit 0
