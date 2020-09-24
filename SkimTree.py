#!/usr/bin/env python
import ROOT
from optparse import OptionParser

###############
def main():
###############

# command line options
    parser = OptionParser()
    parser.add_option("-f", "--file",  
                      action="store", type="string", dest="input_root_filename",
                      help="input root file")

    (options, args) = parser.parse_args()

# input
    chain = ROOT.TChain("ReadLocalMeasurement/PixelNtuple")
    chain.Add(options.input_root_filename)
    chain.GetEntry(0)
    nentries = chain.GetEntries()
    print  "+++++ No. of entries in the input tree: ", nentries

    string_cut = "nsimhit>0 && subid==2 && TMath::Abs(pitchx-0.010)<0.0001"
    cut = '_FPIX_2x2'

# output
    output_root_filename = options.input_root_filename.split('.root')[0]+cut+'.root'
    print output_root_filename
    fileTreeOut = ROOT.TFile(output_root_filename,"RECREATE")

    fileTreeOut.cd()
    # adapted to the new TFileService structure of subdirs
    fileTreeOut.mkdir("ReadLocalMeasurement")            
    fileTreeOut.cd("ReadLocalMeasurement")            
    newtree = ROOT.TTree()
    newtree= chain.CopyTree(string_cut,"",nentries)
    newtree.AutoSave()

    nentries = newtree.GetEntries()
    print "+++++ No. of entries in the output tree: ", nentries 
    
    fileTreeOut.Write()
    fileTreeOut.Close()
    
##################################
if __name__ == "__main__":        
    main()
