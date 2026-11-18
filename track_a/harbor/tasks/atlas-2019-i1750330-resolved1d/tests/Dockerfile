FROM hepstore/rivet:4.1.2
COPY closure.py /tests/closure.py
COPY reference /tests/reference
COPY herwig7_ttbar_80ev.hepmc.gz /tests/herwig7_ttbar_80ev.hepmc.gz
COPY samples.json /tests/samples.json
COPY test.sh /tests/test.sh
RUN chmod +x /tests/test.sh
