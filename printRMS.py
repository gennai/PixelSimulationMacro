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


    h_x = input_root_file.Get("NRows/residualsX/h_resRPhivsNRows_qall")      
    rmsX    = array.array('d')    
    for ii in range(h_x.GetNbinsX()):
        rmsX.append(h_x.GetBinContent(ii+1)/CmToMicron)

    lst = rmsX.tolist()
    print(','.join(' {}'.format('%6.4f'% lst[k]) for k in xrange(len(lst))))

    h_y = input_root_file.Get("NCols/residualsY/h_resZvsNCols_qall")      
    rmsY    = array.array('d')    
    for ii in range(h_y.GetNbinsX()):
        rmsY.append(h_y.GetBinContent(ii+1)/CmToMicron)

    lst = rmsY.tolist()
    print(','.join(' {}'.format('%6.4f'% lst[k]) for k in xrange(len(lst))))

##################################
if __name__ == "__main__":        
    main()


