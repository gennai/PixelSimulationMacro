#!/usr/bin/env python
# E.Migliore Universita` di Torino/INFN

import sys
import ROOT
import array
import math
import os

from optparse import OptionParser

# my modules
from histo_struct import HistoStruct
from rechit_helpers import NotModuleEdgePhase2, CmToUm, ToKe, ELossSilicon
from root_helpers import getTH1cdf

NROWS_MAX = 4
NCOLS_MAX = 3 
            
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
    Int_t           DgRow[100];\
    Int_t           DgCol[100];\
    Int_t           DgDetId[100];\
    Float_t         DgAdc[100];\
    Float_t         DgCharge[100];\
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

    # input root file
    try:
        input_root_file = ROOT.TFile.Open(options.input_root_filename)
    except:
        print "No input file specified"
        sys.exit()
    plotDir = "plots_"
    if "T23" in  options.input_root_filename:
        plotDir += "T23"
    if "T21" in  options.input_root_filename:
        plotDir += "T21"
    if options.gaussfit:
        plotDir += "_gaussfit"
    if options.ontrack:
        plotDir += "_onTrack"
    plotDir += "_L"+str(options.layer)
    if not os.path.exists(plotDir):
        try:
            os.mkdir(plotDir)
        except OSError:
            print ("Creation of the directory %s failed" % path)

    output_root_filename = plotDir+"/PlotResHistos"
    if options.ontrack == False: 
        input_tree = input_root_file.Get("ReadLocalMeasurement/PixelNtuple")      
        output_root_filename += "_All"
    else:
        input_tree = input_root_file.Get("ReadLocalMeasurement/PixelNtupleOnTrack")      
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

    ### hit maps
    h2_rzhitmapSubId1 = ROOT.TH2F("h2_rzhitmapSubId1","rzhitmap_subid1; recHit z [cm]; recHit r [cm]",400,-300.,300.,150,0.,150.)
    h2_rzhitmapSubId2 = ROOT.TH2F("h2_rzhitmapSubId2","rzhitmap_subid2; recHit z [cm]; recHit r [cm]",400,-300.,300.,150,0.,150.)    
    h2_rzhitmapSelected = ROOT.TH2F("h2_rzhitmapSelected","rzhitmap; recHit z [cm]; recHit r [cm]",400,-300.,300.,200,0.,20.)

    ### simhit and rechit local positions
    h1_localX_witdh1_simHit = ROOT.TH1F("h1_localX_witdh1_simHit","h1_localX_witdh1_simHit",2000,-10000,+10000)
    h1_localX_witdh1_recHit = ROOT.TH1F("h1_localX_witdh1_recHit","h1_localX_witdh1_recHit",2000,-10000,+10000)
    h1_localX_witdh1_delta = ROOT.TH1F("h1_localX_witdh1_delta","h1_localX_witdh1_delta",80,-400,+400)

    h1_localY_witdh1_simHit = ROOT.TH1F("h1_localY_witdh1_simHit","h1_localY_witdh1_simHit",7000,-35000,+35000)
    h1_localY_witdh1_recHit = ROOT.TH1F("h1_localY_witdh1_recHit","h1_localY_witdh1_recHit",7000,-35000,+35000)
    h1_localY_witdh1_delta = ROOT.TH1F("h1_localY_witdh1_delta","h1_localY_witdh1_delta",80,-400,+400)    

    # phase 0/phase 1
    #   lX=8200.
    #   lY=32500.
    # phase 2 (to be checked)
    lX=17000.
    lY=22500.
    # size of the bin is dXxdY um^2
    dX = 100 #100
    dY = 100 #100 
    nX = int((lX*2)/dX)
    nY = int((lY*2)/dY)
    print "Local HitMaps nX, nY: ", nX, nY
    h2_localXY_mod_simHit = ROOT.TH2F("h2_localXY_mod_simHit","h2_localXY_mod_simHit",nX, -lX, +lX, nY, -lY, +lY) 
    h2_localXY_mod_recHit = ROOT.TH2F("h2_localXY_mod_recHit","h2_localXY_mod_recHit",nX, -lX, +lX, nY, -lY, +lY)

    # phase 0/phase 1 
    # TODO: update TH2 for phase 2
    nX = (8200*2)/dX
    nY = (4100*2)/dY
    h2_localXY_roc_simHit = ROOT.TH2F("h2_localXY_roc_simHit","h2_localXY_roc_simHit",nX,-8200,+8200,nY,0.,8200) 
    h2_localXY_roc_recHit = ROOT.TH2F("h2_localXY_roc_recHit","h2_localXY_roc_recHit",nX,-8200,+8200,nY,0.,8200)

    ### 
    h1_qcorr  = ROOT.TH1F("h1_qcorr","h1_qcorr primaries;Q_{corr} [ke]; recHits",200,0.,400.)

    ### TH1 to monitor cluster shape in TBPX
    h1_nrows_tbpx  = [None for _ in range(4)]
    h1_ncols_tbpx  = [None for _ in range(4)]
    h1_ndigis_tbpx = [None for _ in range(4)]
    for ll in range(4):
        h1_nrows_tbpx[ll]  = ROOT.TH1F('h1_nrows_layer'+str(ll+1), ';N_{rows};', 16,-0.5,15.5)        
        h1_ncols_tbpx[ll]  = ROOT.TH1F('h1_ncols_layer'+str(ll+1), ';N_{cols};', 16,-0.5,15.5)        
        h1_ndigis_tbpx[ll] = ROOT.TH1F('h1_ndigis_layer'+str(ll+1),';N_{cells};',16,-0.5,15.5)        
    ###

    ### histo containers
    hsNRow  = HistoStruct("NRows" , NROWS_MAX, 0.5,  NROWS_MAX+0.5, "N_{rows}", output_root_file, options.gaussfit) 
    hsNCol  = HistoStruct("NCols" , NCOLS_MAX, 0.5,  NCOLS_MAX+0.5, "N_{cols}", output_root_file, options.gaussfit) 


    # 
    if options.subid == 1: 
        hsEta = HistoStruct("Eta" ,26, 0.0, 2.6, "|#eta|", output_root_file, options.gaussfit)
        hsPhi = HistoStruct("Phi" , 12, 0., 6.4, "|#phi|", output_root_file, options.gaussfit)
        hsCotgAlpha = HistoStruct("CotgAlpha" ,15,-0.45, 0.30,  "cotg(#alpha)",  output_root_file, options.gaussfit) # BPIX
        hsCotgBeta  = HistoStruct("CotgBeta"  ,10, 0.25, 0.50, "|cotg(#beta)|",  output_root_file, options.gaussfit)
    else:
        hsEta = HistoStruct("Eta" ,5, 1.4, 3.9, "|#eta|", output_root_file, options.gaussfit)  
        hsPhi = HistoStruct("Phi" , 16, -3.2, 3.2, "|#phi|", output_root_file, options.gaussfit)      
        hsCotgAlpha = HistoStruct("CotgAlpha" , 4,-0.45,-0.25,  "cotg(#alpha)",  output_root_file, options.gaussfit) # FPIX
        hsCotgBeta  = HistoStruct("CotgBeta"  ,20, 0.25, 0.75, "|cotg(#beta)|",  output_root_file, options.gausfit)

    all_entries = input_tree.GetEntries()
    if options.entries != -1:
        all_entries = options.entries
    print "all_entries ", all_entries        

    ######## 1st loop on the tree
    for this_entry in xrange(all_entries):
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

        pixel_recHit.DgRow = array.array('i',[0]*100)
        pixel_recHit.DgCol = array.array('i',[0]*100)
        pixel_recHit.DgDetId = array.array('i',[0]*100)
        pixel_recHit.DgAdc = array.array('f',[0]*100)
        pixel_recHit.DgCharge = array.array('f',[0]*100)

        for iDg in range(pixel_recHit.DgN):
            pixel_recHit.DgRow[iDg] = input_tree.DgRow[iDg]
            pixel_recHit.DgCol[iDg] = input_tree.DgCol[iDg]
            pixel_recHit.DgDetId[iDg] = input_tree.DgDetId[iDg]
            pixel_recHit.DgAdc[iDg] = input_tree.DgAdc[iDg]
            pixel_recHit.DgCharge[iDg] =input_tree.DgCharge[iDg]

        ### monitor cluster size in TBPX
        if pixel_recHit.subid==1: 
            ll = pixel_recHit.layer - 1
            h1_nrows_tbpx[ll].Fill(pixel_recHit.spreadx)
            h1_ncols_tbpx[ll].Fill(pixel_recHit.spready)
            h1_ndigis_tbpx[ll].Fill(pixel_recHit.DgN)


        # skip RecHit with no SimHit associated 
        if pixel_recHit.nsimhit == 0: 
            continue
       
        # phase2 : BPIX subid==1&&layer<5
        #          FPIX subid==2&&disk<13  


        # global position of the rechit
        # NB sin(theta) = tv3.Perp()/tv3.Mag()
        tv3 = ROOT.TVector3(pixel_recHit.gx, pixel_recHit.gy, pixel_recHit.gz)
    
        # hitmap for sanity check (phase1 subid=1/2 -> BPIX/FPIX, phase2 subid=1/2 barrel/endcap)
        if (pixel_recHit.subid==1 and pixel_recHit.layer<5):
            h2_rzhitmapSubId1.Fill(tv3.z(),tv3.Perp())
        elif (pixel_recHit.subid==2 and pixel_recHit.disk<13):
            h2_rzhitmapSubId2.Fill(tv3.z(),tv3.Perp())

        # Select one BPIX layer or FPIX disk
        # example: if pixel_recHit.subid==options.subid and (pixel_recHit.layer==options.layer or pixel_recHit.disk==options.layer) :
        if pixel_recHit.subid==options.subid and pixel_recHit.layer==options.layer:
            h2_rzhitmapSelected.Fill(tv3.z(),tv3.Perp())

            # map of local positions 
            if pixel_recHit.process > -1:
                h2_localXY_mod_simHit.Fill(pixel_recHit.hx*CmToUm,pixel_recHit.hy*CmToUm) 
                h2_localXY_mod_recHit.Fill(pixel_recHit.x*CmToUm ,pixel_recHit.y*CmToUm) 

                h2_localXY_roc_simHit.Fill(pixel_recHit.hx*CmToUm,(pixel_recHit.hy*CmToUm)%8100.)  # 8100. hard coded -> size (in localY) of the Si surface read out by one ROC
                h2_localXY_roc_recHit.Fill(pixel_recHit.x*CmToUm ,(pixel_recHit.y*CmToUm)%8100. ) 

            # map of local positions for clusters with projected width=1 ("pettine")
            if pixel_recHit.spreadx == 1:
                h1_localX_witdh1_simHit.Fill(pixel_recHit.hx*CmToUm) 
                h1_localX_witdh1_recHit.Fill(pixel_recHit.x*CmToUm) 
                h1_localX_witdh1_delta.Fill((pixel_recHit.hx-pixel_recHit.x)*CmToUm)
            if pixel_recHit.spready == 1:
                h1_localY_witdh1_simHit.Fill(pixel_recHit.hy*CmToUm)                 
                h1_localY_witdh1_recHit.Fill(pixel_recHit.y*CmToUm) 
                h1_localY_witdh1_delta.Fill((pixel_recHit.hy-pixel_recHit.y)*CmToUm)

            # your preferred definition of eta
            # the_eta = tv3.Eta()
            # the_eta = -math.log(math.tan(0.5*beta))

            # ionization corrected for incident angle (only primaries at central eta) 
            #           if math.fabs(tv3.Eta())<0.20 and pixel_recHit.process == 2:
            if pixel_recHit.process > -1:
                h1_qcorr.Fill(pixel_recHit.q*ToKe*math.fabs(pixel_recHit.tz))
                # effective thickness estimated from eta of recHit
                #  h1_qcorr.Fill(pixel_recHit.q*ToKe*tv3.Perp()/tv3.Mag())

            hsEta.FillFirstLoop(math.fabs(tv3.Eta()), pixel_recHit)
            hsPhi.FillFirstLoop(math.fabs(tv3.Phi()), pixel_recHit)
            hsCotgAlpha.FillFirstLoop(           pixel_recHit.tx/pixel_recHit.tz,  pixel_recHit)
            hsCotgBeta.FillFirstLoop(  math.fabs(pixel_recHit.ty/pixel_recHit.tz), pixel_recHit)
            hsNRow.FillFirstLoop(min(pixel_recHit.spreadx,NROWS_MAX), pixel_recHit)
            hsNCol.FillFirstLoop(min(pixel_recHit.spready,NCOLS_MAX), pixel_recHit)

    ### Compute the Q averaged in the central eta-bin
    output_root_file.cd("hitmapsAndCharge") 
    h1_qcorr_norm = getTH1cdf(h1_qcorr)
    Qave = h1_qcorr.GetMean()
    print "Average Corrected Q cluster [ke]: ", Qave

    ######## 2nd loop on the tree (required when selections based Qave are used)
    for this_entry in xrange(all_entries):
        input_tree.GetEntry(this_entry)

        if this_entry % 100000 == 0:
            print "Loop #2 Procesing Event: ", this_entry

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

        pixel_recHit.DgRow = array.array('i',[0]*100)
        pixel_recHit.DgCol = array.array('i',[0]*100)
        pixel_recHit.DgDetId = array.array('i',[0]*100)
        pixel_recHit.DgAdc = array.array('f',[0]*100)
        pixel_recHit.DgCharge = array.array('f',[0]*100)

        for iDg in range(pixel_recHit.DgN):
            pixel_recHit.DgRow[iDg] = input_tree.DgRow[iDg]
            pixel_recHit.DgCol[iDg] = input_tree.DgCol[iDg]
            pixel_recHit.DgDetId[iDg] = input_tree.DgDetId[iDg]
            pixel_recHit.DgAdc[iDg] = input_tree.DgAdc[iDg]
            pixel_recHit.DgCharge[iDg] =input_tree.DgCharge[iDg]

        # skip RecHit with no SimHit associated 
        if pixel_recHit.nsimhit == 0: 
            continue
       
        # phase2 : BPIX subid==1&&layer<5
        #          FPIX subid==2&&disk<13


        # Select one BPIX layer or FPIX disk
        # example:if pixel_recHit.subid==options.subid and (pixel_recHit.layer==options.layer or pixel_recHit.disk==options.layer) :
        if pixel_recHit.subid==options.subid and pixel_recHit.layer==options.layer:
            # global position of the rechit
            # NB sin(theta) = tv3.Perp()/tv3.Mag()
            tv3 = ROOT.TVector3(pixel_recHit.gx, pixel_recHit.gy, pixel_recHit.gz)

            # your preferred definition of eta
            #            the_eta = tv3.Eta()
            #            the_eta = -math.log(math.tan(0.5*beta))

            # residuals for clusters Q<1.5*Q_ave from primaries only (same selection as Morris Swartz)
            # exclude clusters at the edges of the module (charge drifting outside the silicon)
            if pixel_recHit.process > -1 and NotModuleEdgePhase2(pixel_recHit.x*CmToUm, pixel_recHit.y*CmToUm):
               hsEta.FillSecondLoop(math.fabs(tv3.Eta()), pixel_recHit)
               hsPhi.FillSecondLoop(math.fabs(tv3.Phi()), pixel_recHit)
               hsCotgAlpha.FillSecondLoop(           pixel_recHit.tx/pixel_recHit.tz,  pixel_recHit)
               hsCotgBeta.FillSecondLoop(  math.fabs(pixel_recHit.ty/pixel_recHit.tz), pixel_recHit)
               hsNRow.FillSecondLoop(min(pixel_recHit.spreadx,NROWS_MAX), pixel_recHit)
               hsNCol.FillSecondLoop(min(pixel_recHit.spready,NCOLS_MAX), pixel_recHit)

    ########################
    ### SUMMARY CANVASES ###
    ########################

    ### local position 
    c1_localXY = ROOT.TCanvas("c1_localXY","c1_localXY",600,900)
    c1_localXY.SetFillColor(ROOT.kWhite)
    c1_localXY.Divide(1,2)

    c1_localXY.cd(1)
    h1_localX_witdh1_recHit.SetLineColor(ROOT.kRed) 
    h1_localX_witdh1_recHit.Draw() 
    h1_localX_witdh1_simHit.Draw("same") 

    c1_localXY.cd(2)
    h1_localY_witdh1_recHit.SetLineColor(ROOT.kRed) 
    h1_localY_witdh1_recHit.Draw() 
    h1_localY_witdh1_simHit.Draw("same") 

    c1_localXY.SaveAs(plotDir+"/c1_localXY.root")

    ### local position (module level)
    c1_localXY_mod_hitmap = ROOT.TCanvas("c1_localXY_mod_hitmap","c1_localXY_mod_hitmap",164*3,325*3) # size of the canvas with the same aspect ratio of the module 
    c1_localXY_mod_hitmap.SetFillColor(ROOT.kWhite)
    c1_localXY_mod_hitmap.Divide(2,1)
    
    # for not understood reasons, the following work only in a ROOT session
    # TPython::LoadMacro( "rbPalette.py")
    # rbPalette.py
    # # red-blue
    # stops = [ 0.00, 0.50, 1.00]
    # red   = [ 0.00, 0.50, 1.00]
    # green = [ 0.00, 0.00, 0.00]
    # blue  = [ 1.00, 0.50, 0.00]

    # s = array.array('d', stops)
    # r = array.array('d', red)
    # g = array.array('d', green)
    # b = array.array('d', blue)
    
    # npoints = len(s)
    # ncontours = 8
    # ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    # ROOT.gStyle.SetNumberContours(ncontours)
    ######################################################
     
    c1_localXY_mod_hitmap.cd(1)
    h2_localXY_mod_simHit.Draw("colz")     
    c1_localXY_mod_hitmap.cd(2)
    h2_localXY_mod_recHit.Draw("colz") 
    
    c1_localXY_mod_hitmap.SaveAs(plotDir+"/c1_localXY_mod_hitmap.root")

    ### local position ( 2*ROC level)
    c1_localXY_roc_hitmap = ROOT.TCanvas("c1_localXY_roc_hitmap","c1_localXY_roc_hitmap",164*4,164*4) # size of the canvas with the same aspect ratio of the 2*ROC
    c1_localXY_roc_hitmap.SetFillColor(ROOT.kWhite)
    c1_localXY_roc_hitmap.Divide(1,2)
    
    c1_localXY_roc_hitmap.cd(1)
    h2_localXY_roc_simHit.Draw("colz")     
    c1_localXY_roc_hitmap.cd(2)
    h2_localXY_roc_recHit.Draw("colz") 
    
    c1_localXY_roc_hitmap.SaveAs(plotDir+"/c1_localXY_roc_hitmap.root")
    
    hsEta.DrawAllCanvas(Qave,  pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)
    hsPhi.DrawAllCanvas(Qave,  pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)
    hsCotgAlpha.DrawAllCanvas(Qave, pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)
    hsCotgBeta.DrawAllCanvas(Qave, pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)

    hsNRow.DrawAllCanvas(Qave, pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)
    hsNCol.DrawAllCanvas(Qave, pixel_recHit.thickness*CmToUm*ELossSilicon*ToKe,plotDir)
    output_root_file.Write()
    output_root_file.Close()

##################################
if __name__ == "__main__":        
    main()



