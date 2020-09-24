#!/usr/bin/env python

import sys
import ROOT
import array
from optparse import OptionParser

CmToMicron = 10000.
###############
def main():
###############

    parser = OptionParser()
    parser.add_option("-f", "--file",  
                      action="store", type="string", dest="input_root_filename",
                      help="input root file")
    (options, args) = parser.parse_args()

    # input root file
    try:
        input_root_file = ROOT.TFile.Open(options.input_root_filename)
    except:
        print "No input file specified"
        sys.exit()


    h_x = input_root_file.Get("NRows/h_NRows")      
    norm_x = h_x.GetEntries()
    h_x.Scale(1/norm_x)
    h_x.GetYaxis().SetRangeUser(0.,1.)

    h_y = input_root_file.Get("NCols/h_NCols")      
    norm_y = h_y.GetEntries()
    h_y.Scale(1/norm_y)
    h_y.GetYaxis().SetRangeUser(0.,1.)


    c1 = ROOT.TCanvas('c1','c1',600,300)
    c1.Divide(2,1)
    c1.cd(1)
    h_x.Draw()
    c1.cd(2)
    h_y.Draw()
    c1.SaveAs('c1_ClusterSpread_BPIX.pdf')

##################################
if __name__ == "__main__":        
    main()


