// pp -> ttbar, 13 TeV, alphaS(FSR/ISR)=0.140. Usage: ./main SEED NEVENTS OUT.hepmc (HepMC2 ASCII; gzip externally)
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"
using namespace Pythia8;
int main(int argc, char** argv) {
  int seed = atoi(argv[1]); int nev = atoi(argv[2]);
  Pythia pythia;
  pythia.readString("Beams:eCM = 13000");
  pythia.readString("Top:gg2ttbar = on");
  pythia.readString("Top:qqbar2ttbar = on");
  pythia.readString("SpaceShower:alphaSvalue = 0.140");
  pythia.readString("TimeShower:alphaSvalue = 0.140");
  pythia.readString("Random:setSeed = on");
  pythia.readString("Random:seed = " + to_string(seed));
  pythia.readString("Next:numberCount = 1000");
  if (!pythia.init()) return 1;
  Pythia8ToHepMC toHepMC(argv[3]);
  for (int i = 0; i < nev; ++i) {
    if (!pythia.next()) { if (pythia.info.atEndOfFile()) break; --i; continue; }
    toHepMC.writeNextEvent(pythia);
  }
  pythia.stat();
  return 0;
}
