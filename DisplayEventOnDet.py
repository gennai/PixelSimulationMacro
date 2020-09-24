#!/usr/bin/env python
# E.Migliore Universita` di Torino/INFN

import sys
import ROOT
import array
import math

import tempfile
from os import path, system
from optparse import OptionParser

# my modules
from rechit_helpers import NotModuleEdgePhase2, CmToUm, ToKe, ELossSilicon
from set_palette import set_palette

EOS_PATH='root://eoscms.cern.ch//eos/cms/store/group/upgrade/Tracker/simulation/PhaseII/InnerTracker/sandbox'

PITCH_X =  25
PITCH_Y = 100
    
def display_detid(the_evt, the_detid, ndigis, px, py, pcharge):

    """ 
    visualization of the current cluster
    - first coordinate is local-y (=ROC column)
    - first coordinate is local-x (=ROC row)
    
    [ col0,row2 ][ col1,row2 ][ col2,row2 ]....
    [ col0,row1 ][ col1,row1 ][ col2,row2 ]....
    [ col0,row0 ][ col1,row0 ][ col2,row0 ]....
    
    """
    minPixelRow = min(py)
    maxPixelRow = max(py)
    minPixelCol = min(px)
    maxPixelCol = max(px)
            
    # Obtain boundaries in index units (e.g. int)
    xmin = minPixelCol-1.5
    xmax = maxPixelCol+1.5
    nx = int(xmax-xmin)
    
    ymin = minPixelRow-1.5
    ymax = maxPixelRow+1.5
    ny = int(ymax-ymin)
    
    h2Name = 'h2Display_'+str(the_evt)+'_'+str(the_detid)
    cName  = 'cDisplay_'+str(the_evt)+'_'+str(the_detid)
    h2Display = ROOT.TH2Poly()
    h2Display.SetName(h2Name)
    h2Display.SetTitle(h2Name)
    
    # prepare the polyline 
    r1 = xmin
    r2 = r1 + 1.

    while (r2 <= xmax):    
        c1 = ymin
        c2 = c1

        while (c2 <= ymax):
            h2Display.AddBin(c1, r1, c2, r2)                
            c1 = c2 
            c2 = c1 + 1.

        r1 = r2
        r2 = r1 + 1.

    # fill with the pixel digis
    # pix is a '(row, col, charge)' tuple
    for idg in range(ndigis):   
        h2Display.Fill(py[idg], px[idg], pcharge[idg])
        
    scale = 2
    cDisplay = ROOT.TCanvas() #cName, cName, ny*PITCH_Y, nx*PITCH_X )
    cDisplay.cd()
#        cDisplay.SetGrid()
    set_palette('cividis')    
    h2Display.SetStats(ROOT.kFALSE)
    #    h2Display.Draw('TEXT')
    h2Display.Draw('COLZ')
    h2Display.SetMarkerSize(2)
 #       h2Display.GetXaxis().SetNdivisions(ny,ROOT.kFALSE)
    h2Display.GetXaxis().SetTitle('ROC col')
    h2Display.GetXaxis().SetRangeUser(ymin, ymax)
#        h2Display.GetYaxis().SetNdivisions(nx,ROOT.kFALSE)
    h2Display.GetYaxis().SetTitle('ROC row')
    h2Display.GetYaxis().SetRangeUser(xmin, xmax)
            
    h2Display.GetZaxis().SetRangeUser(0.,10000.)

    recHit = [None for _ in range(ndigis)]
    for idg in range(ndigis):   
        if math.fabs(pcharge[idg]-7000.) < 1000.:
            recHit[idg] = ROOT.TMarker(py[idg], px[idg], ROOT.kFullCircle)
            recHit[idg].SetMarkerSize(1.)        
            recHit[idg].SetMarkerColor(ROOT.kRed)
            recHit[idg].Draw("Psame")

    # leg = ROOT.TLegend(0.1, 0.1, 0.4, 0.2)
    # leg.SetTextSize(0.04)
    # text_simHit = 'SimHit %7.1f %7.1f' % (sim_x*100000., sim_y*100000)
    # text_recHit = 'RecHit %7.1f %7.1f' % (rec_x*100000., rec_y*100000)
    # leg.AddEntry(simHit, text_simHit, "p")
    # leg.AddEntry(recHit, text_recHit, "p")
    # leg.Draw("same")

    cDisplay.SaveAs(path.join(tempfile.gettempdir(),cName+'.pdf'))
    del recHit[:] 

#####################
def declare_struct():
#####################
# ROOT defined struct(s) present in the input tree
    ROOT.gROOT.ProcessLine("struct evt_t {\
    Int_t           run;\
    Int_t           evtnum;\
    };" )

    ROOT.gROOT.ProcessLine("struct pixel_recHit_t {\
    Int_t       pdgid;\
    Int_t     process;\
    Float_t         q;\
    Float_t         x;\
    Float_t         y;\
    Float_t         xx;\
    Float_t         xy;\
    Float_t         yy;\
    Float_t         row;\
    Float_t         col;\
    Float_t         hrow;\
    Float_t         hcol;\
    Float_t         gx;\
    Float_t         gy;\
    Float_t         gz;\
    Int_t           subid;\
    Int_t           module;\
    Int_t           layer;\
    Int_t           ladder;\
    Int_t           disk;\
    Int_t           blade;\
    Int_t           panel;\
    Int_t           side;\
    Int_t           nsimhit;\
    Int_t           spreadx;\
    Int_t           spready;\
    Int_t           nRowsInDet;\
    Int_t           nColsInDet;\
    Float_t         pitchx;\
    Float_t         pitchy;\
    Float_t         thickness;\
    Float_t         cotAlphaFromDet;\
    Float_t         cotBetaFromDet;\
    Float_t         hx;\
    Float_t         hy;\
    Float_t         tx;\
    Float_t         ty;\
    Float_t         tz;\
    Float_t         theta;\
    Float_t         phi;\
    Int_t           DgN;\
    Int_t           DgRow[150];\
    Int_t           DgCol[150];\
    Int_t           DgDetId[150];\
    Float_t         DgAdc[150];\
    Float_t         DgCharge[150];\
    };" )


###############
def main():
###############
    ROOT.gSystem.Load('libRooFit')

    parser = OptionParser()
    parser.add_option("-f", "--file",  
                      action="store", type="string", dest="input_root_filename",
                      help="input root file")
    parser.add_option("-o", "--on-track",
                      action="store_true", dest="ontrack", default=False,
                      help="use on track clusters (default is all clusters)")
    parser.add_option("-g", "--gauss",
                      action="store_true", dest="gaussfit", default=False,
                      help="gaussian fit of residuals (default is RMS)")
    parser.add_option("-e", "--entries",
                      action="store", type="int", dest="entries", default=-1,
                      help="number of entries")
    parser.add_option("-L", "--layer",
                      action="store", type="int", dest="layer", default=-1,
                      help="Pixel Layer")
    parser.add_option("-S", "--subid",
                      action="store", type="int", dest="subid", default=1,
                      help="phase1: BPIX (subid=1) or FPIX (subid=2)")
    
    (options, args) = parser.parse_args()

# do not pop-up canvases as they are drawn
    ROOT.gROOT.SetBatch(ROOT.kTRUE) 

    # input root fil
    print path.join(EOS_PATH,options.input_root_filename)
    try:
        input_root_file = ROOT.TFile.Open(path.join(EOS_PATH,options.input_root_filename))
    except:
        print "No input file specified"
        sys.exit()
        
    output_root_filename = "PlotResHistos"
    if options.ontrack == False: 
        input_tree = input_root_file.Get("ReadLocalMeasurement/PixelNtuple")      
        output_root_filename += "_All"
    else:
        input_tree = input_root_file.Get("ReadLocalMeasurement/Pixel2Ntuple")      
        output_root_filename += "_OnTrack"

    if options.gaussfit == False: 
        output_root_filename += "_RMS"
    else:
        output_root_filename += "_Sigma"

    output_root_filename += ".root"

    input_tree.Print()
        
    # import the ROOT defined struct(s) in pyROOT
    declare_struct()
    from ROOT import evt_t, pixel_recHit_t

    # define the pyROOT classes and assign the address
    evt = evt_t()
    pixel_recHit = pixel_recHit_t()
    input_tree.SetBranchAddress("evt",ROOT.AddressOf(evt,"run"))        

    output_root_file = ROOT.TFile(output_root_filename,"RECREATE")

    ### HIT POSITIONS
    output_root_file.mkdir("hitmapsAndCharge") 
    output_root_file.cd("hitmapsAndCharge") 

    h1_DgCharge_RecHit= ROOT.TH1F("h1_DgCharge_RecHit","h1_DgCharge_RecHit",360,0,36000)

    ###
    ndigis_on_det = 0 
    px = array.array('d')
    py = array.array('d')
    pcharge = array.array('d')
    
    DgDetIdOld = 0
    evtnumOld = 0
    first = True
    debug = False
  
    ###
    all_entries = input_tree.GetEntries()
    if options.entries != -1:
        all_entries = options.entries
    print "all_entries ", all_entries        

    do_plot = False
    ######## 1st loop on the tree
    for this_entry in xrange(50000): #all_entries):
        input_tree.GetEntry(this_entry)
        if this_entry % 100000 == 0:
            print "Loop #1 Procesing Event: ", this_entry

# To access the events in a tree no variables need to be assigned to the different branches. Instead the leaves are available as properties of the tree, returning the values of the present event. 
        pixel_recHit.pdgid      = input_tree.pdgid
        pixel_recHit.process    = input_tree.process
        pixel_recHit.q          = input_tree.q
        pixel_recHit.x          = input_tree.x
        pixel_recHit.y          = input_tree.y
        pixel_recHit.xx         = input_tree.xx
        pixel_recHit.xy         = input_tree.xy
        pixel_recHit.yy         = input_tree.yy
        pixel_recHit.row        = input_tree.row
        pixel_recHit.col        = input_tree.col
        pixel_recHit.hrow       = input_tree.hrow
        pixel_recHit.hcol       = input_tree.hcol
        pixel_recHit.gx         = input_tree.gx
        pixel_recHit.gy         = input_tree.gy
        pixel_recHit.gz         = input_tree.gz
        pixel_recHit.subid      = input_tree.subid
        pixel_recHit.module     = input_tree.module
        pixel_recHit.layer      = input_tree.layer
        pixel_recHit.ladder     = input_tree.ladder
        pixel_recHit.disk       = input_tree.disk
        pixel_recHit.blade      = input_tree.blade
        pixel_recHit.panel      = input_tree.panel
        pixel_recHit.side       = input_tree.side
        pixel_recHit.nsimhit    = input_tree.nsimhit
        pixel_recHit.spreadx    = input_tree.spreadx
        pixel_recHit.spready    = input_tree.spready
        pixel_recHit.pitchx     = input_tree.pitchx
        pixel_recHit.pitchy     = input_tree.pitchy
        pixel_recHit.thickness  = input_tree.thickness
        pixel_recHit.cotAlphaFromDet = input_tree.cotAlphaFromDet
        pixel_recHit.cotBetaFromDet  = input_tree.cotBetaFromDet
        pixel_recHit.nColsInDet = input_tree.nColsInDet
        pixel_recHit.nRowsInDet = input_tree.nRowsInDet
        pixel_recHit.hx         = input_tree.hx
        pixel_recHit.hy         = input_tree.hy
        pixel_recHit.tx         = input_tree.tx
        pixel_recHit.ty         = input_tree.ty
        pixel_recHit.tz         = input_tree.tz
        pixel_recHit.theta      = input_tree.theta
        pixel_recHit.phi        = input_tree.phi
        pixel_recHit.DgN        = input_tree.DgN

        pixel_recHit.DgRow = array.array('i',[0]*150)
        pixel_recHit.DgCol = array.array('i',[0]*150)
        pixel_recHit.DgDetId = array.array('i',[0]*150)
        pixel_recHit.DgAdc = array.array('f',[0]*150)
        pixel_recHit.DgCharge = array.array('f',[0]*150)

        for iDg in range(pixel_recHit.DgN):
            pixel_recHit.DgRow[iDg] = input_tree.DgRow[iDg]
            pixel_recHit.DgCol[iDg] = input_tree.DgCol[iDg]
            pixel_recHit.DgDetId[iDg] = input_tree.DgDetId[iDg]
            pixel_recHit.DgAdc[iDg] = input_tree.DgAdc[iDg]
            pixel_recHit.DgCharge[iDg] =input_tree.DgCharge[iDg]

        # skip RecHit with no SimHit associated 
        # if pixel_recHit.nsimhit == 0: 
        #     continue
       
        # Select one BPIX layer or FPIX disk
        # example: if pixel_recHit.subid==options.subid and (pixel_recHit.layer==options.layer or pixel_recHit.disk==options.layer) :
        if pixel_recHit.subid == 1\
                and pixel_recHit.layer == 1\
                and (pixel_recHit.ladder % 2) == 1\
                and pixel_recHit.module == 9:

            # first event
            if first:
                evtnumOld = evt.evtnum
                DgDetIdOld = pixel_recHit.DgDetId[0]
                first = False
            

            # fill the output tree when there is a new module (DetId) or a new event
            if ( pixel_recHit.DgDetId[0] != DgDetIdOld or evt.evtnum != evtnumOld ):
                if debug :
                    print "We have a new event or a new module (Evt, DetId): ", evtnumOld, DgDetIdOld
                    print  "Create a new entry  ",  ndigis_on_det 
                    
                # display this event                    
                if do_plot:
                    display_detid(evtnumOld, DgDetIdOld, ndigis_on_det, px, py, pcharge)
                    do_plot = False
                    del px[:]
                    del py[:]
                    del pcharge[:]
                evtnumOld  = evt.evtnum
                DgDetIdOld = pixel_recHit.DgDetId[0]
                ndigis_on_det = 0
            # end if pixel_recHit.DgDetId[0] != DgDetIdOld or evt.evtnum != evtnumOld 

            for iDg in range(pixel_recHit.DgN):                           
                h1_DgCharge_RecHit.Fill(pixel_recHit.DgCharge[iDg] * 1000.)
                px.insert(ndigis_on_det, pixel_recHit.DgRow[iDg])
                py.insert(ndigis_on_det, pixel_recHit.DgCol[iDg])
                pcharge.insert(ndigis_on_det, pixel_recHit.DgCharge[iDg] * 1000.)
                if math.fabs(pixel_recHit.DgCharge[iDg] * 1000. - 7000.) < 1000.: 
                    do_plot = True
                ndigis_on_det = ndigis_on_det + 1

    if debug :
        print "We have a new event or a new module (Evt, DetId): ", evtnumOld, DgDetIdOld
        print  "Create a new entry  ",  ndigis_on_det 


    if do_plot:
        display_detid(evtnumOld, DgDetIdOld, ndigis_on_det, px, py, pcharge)
    output_root_file.Write()
    output_root_file.Close()

##################################
if __name__ == "__main__":        
    main()



