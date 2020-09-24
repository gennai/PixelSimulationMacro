#!/usr/bin/env python
# TPython::LoadMacro( "OverlayHistos.py" );
# TODO: transform input args to list

import os.path
import ROOT
import histoprint as HP

class h1Struct:
    """" simple struct to hold h1, ROOT.kColor """
    def __init__(self, h1, color):
        self.h1 = h1
        self.kColor = color

        h1.SetLineColor(self.kColor)
        h1.SetMarkerColor(self.kColor)

    # getters
    def getTH1(self):
        return self.h1
    def getkColor(self):
        return self.kColor
    def getLabel(self):
        return self.label

    def gaus_fit(self, range_left=None, range_right=None):    
        """ gaussian fit within a range (if specified) """
        if range_left == None or range_right == None:
            mean_tmp = self.h1.GetMean()
            stddev_tmp = self.h1.GetRMS()
            g1 = ROOT.TF1("g1","gaus",mean_tmp-1.5*stddev_tmp,mean_tmp+1.5*stddev_tmp)  
            g1.SetLineColor(self.kColor)
            self.h1.Fit(g1,'R')
        else:
            g1 = ROOT.TF1("g1","gaus",range_left,range_right)    
            g1.SetLineColor(self.kColor)
            self.h1.Fit(g1,'R')
            
    
def DrawOverlayTH1F(h1SA, h1SB, h1SC, range_left=None, range_right=None):
                    
    c1 = ROOT.TCanvas("c1","c1",600,700)        
    #c1.SetLogy()
    boxpos = ()
    first = True
    ll = []
    ll.append(h1SA.getTH1().GetMaximum())
    ll.append(h1SB.getTH1().GetMaximum())
    # ll.append(h1SC.getTH1().GetMaximum())
    h1_max = max(ll)
    h1_list = [h1SA, h1SB]#, h1SC]
    for h1S in h1_list:
        #HP.normalize(h)
        if first:
            h1S.getTH1().SetMaximum(1.05*h1_max)
            h1S.getTH1().Draw()

            if range_left == None or range_right == None:
                pass
            else: 
                h1S.getTH1().GetXaxis().SetRangeUser(range_left, range_right)
                
            ROOT.gPad.Update()
            statbox = HP.getstatbox(h1S.getTH1())
            Ox1,Oy1,Ox2,Oy2 = HP.findstatcoords(statbox)
            # move stat box to the upper left corner
            # HP.movestatbox(statbox,0.05,Oy1,0.05+(Ox2-Ox1),Oy2)
            # move stat box to the upper right corner
            HP.movestatbox(statbox,0.95-(Ox2-Ox1),Oy1,0.95,Oy2)
            Ox1,Oy1,Ox2,Oy2 = HP.findstatcoords(statbox)
            boxpos = (1,1)
            first = False
        else:
            h1S.getTH1().Draw('sames')

            if range_left == None or range_right == None:
                pass
            else: 
                h1S.getTH1().GetXaxis().SetRangeUser(range_left, range_right)                

            ROOT.gPad.Update()
            statbox = HP.getstatbox(h1S.getTH1())
            HP.movestatbox(statbox,Ox1,y1-(y2-y1),Ox2,y2-(y2-y1))
            boxpos = (1,boxpos[1]+1)

            ROOT.gPad.Modified()
            
        x1,y1,x2,y2 = HP.findstatcoords(statbox)
        HP.colourize_statbox(h1S.getTH1())
        ROOT.gPad.Modified()
        ROOT.gPad.Update()


    # leg = ROOT.TLegend(0.20,0.60,0.70,0.70)
    # leg.AddEntry(h1A,'4bit ElectronPerAdc=600e AdcFullScale=16', 'L')
    # leg.AddEntry(h1B,'8bit ElectronPerAdc=135e AdcFullScale=255','L')
    # leg.Draw("same")
    
    #    c1.SaveAs(os.path.join('TMP',h1SA.getTH1().GetName()+'.pdf'))
    c1.SaveAs(os.path.join('TTbar_14TeV',h1SA.getTH1().GetName()+'.pdf'))



def main():
    
    ROOT.gStyle.SetOptStat(1)
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetOptTitle(0)

    ROOT.gStyle.SetStatFontSize(0.025)

    input_root_fileA = ROOT.TFile(os.path.join('TTbar_14TeV','PlotResHistos_All_RMS.default.root'),        'r')
    input_root_fileB = ROOT.TFile(os.path.join('TTbar_14TeV','PlotResHistos_All_RMS.postTDR.root'),        'r')
    input_root_fileC = None #ROOT.TFile('./PlotResHistos_All_RMS.postTDR_wrongLA.root','r')

    input_root_fileA.cd('NRows')
    for kA in ROOT.gDirectory.GetListOfKeys():
        if ROOT.gROOT.GetClass(kA.GetClassName()).InheritsFrom("TH1F"):
            h1name = kA.ReadObj().GetName()
            if h1name.find('h_NRows') != -1:
                h1SA = h1Struct(input_root_fileA.Get('NRows/'+h1name),ROOT.kBlue)
                h1SB = h1Struct(input_root_fileB.Get('NRows/'+h1name),ROOT.kGreen+1)
                h1SC = None # h1Struct(input_root_fileC.Get('NRows/'+h1name),ROOT.kRed)
                DrawOverlayTH1F(h1SA, h1SB, h1SC)

    input_root_fileA.cd('NRows/residualsX')
    for kA in ROOT.gDirectory.GetListOfKeys():
        if ROOT.gROOT.GetClass(kA.GetClassName()).InheritsFrom("TH1F"):
            h1name = kA.ReadObj().GetName()
            if h1name.find('resX_qall_NRowsBin0') != -1 or h1name.find('resX_qall_NRowsBin1') != -1 or  h1name.find('resX_qall_NRowsBin2') != -1:
                h1SA = h1Struct(input_root_fileA.Get('NRows/residualsX/'+h1name),ROOT.kBlue)
                h1SB = h1Struct(input_root_fileB.Get('NRows/residualsX/'+h1name),ROOT.kGreen+1)
                h1SC = None # h1Struct(input_root_fileC.Get('NRows/residualsX/'+h1name),ROOT.kRed)
                h1SA.gaus_fit()#-3.,+3.)
                h1SB.gaus_fit()#-3.,+3.)
                # h1SC.gaus_fit()#-3.,+3.)                    
                DrawOverlayTH1F(h1SA, h1SB, h1SC)


    input_root_fileA.cd('NCols')
    for kA in ROOT.gDirectory.GetListOfKeys():
        if ROOT.gROOT.GetClass(kA.GetClassName()).InheritsFrom("TH1F"):
            h1name = kA.ReadObj().GetName()
            if h1name.find('h_NCols') != -1:
                h1SA = h1Struct(input_root_fileA.Get('NCols/'+h1name),ROOT.kBlue)
                h1SB = h1Struct(input_root_fileB.Get('NCols/'+h1name),ROOT.kGreen+1)
                h1SC = None # h1Struct(input_root_fileC.Get('NCols/'+h1name),ROOT.kRed)
                DrawOverlayTH1F(h1SA, h1SB, h1SC)

    input_root_fileA.cd('NCols/residualsY')
    for kA in ROOT.gDirectory.GetListOfKeys():
        if ROOT.gROOT.GetClass(kA.GetClassName()).InheritsFrom("TH1F"):
            h1name = kA.ReadObj().GetName()
            if h1name.find('resY_qall_NColsBin0') != -1 or h1name.find('resY_qall_NColsBin1') != -1 or  h1name.find('resY_qall_NColsBin2') != -1:
                h1SA = h1Struct(input_root_fileA.Get('NCols/residualsY/'+h1name),ROOT.kBlue)
                h1SB = h1Struct(input_root_fileB.Get('NCols/residualsY/'+h1name),ROOT.kGreen+1)
                h1SC = None # h1Struct(input_root_fileC.Get('NCols/residualsY/'+h1name),ROOT.kRed)
                h1SA.gaus_fit()#-3.,+3.)
                h1SB.gaus_fit()#-3.,+3.)
                # h1SC.gaus_fit()#-3.,+3.)                    
                DrawOverlayTH1F(h1SA, h1SB, h1SC)


    input_root_fileA.cd('hitmapsAndCharge')
    for kA in ROOT.gDirectory.GetListOfKeys():
        if ROOT.gROOT.GetClass(kA.GetClassName()).InheritsFrom("TH1F"):
            h1name = kA.ReadObj().GetName()
            if h1name.find('h1_nrows_layer1') != -1 or h1name.find('h1_ncols_layer1') != -1 or h1name.find('h1_ndigis_layer1') != -1\
                    or h1name.find('h1_nrows_layer2') != -1 or h1name.find('h1_ncols_layer2') != -1 or h1name.find('h1_ndigis_layer2') != -1\
                    or h1name.find('h1_nrows_layer3') != -1 or h1name.find('h1_ncols_layer3') != -1 or h1name.find('h1_ndigis_layer3') != -1\
                    or h1name.find('h1_nrows_layer4') != -1 or h1name.find('h1_ncols_layer4') != -1 or h1name.find('h1_ndigis_layer4') != -1:
                h1SA = h1Struct(input_root_fileA.Get('hitmapsAndCharge/'+h1name),ROOT.kBlue)
                h1SB = h1Struct(input_root_fileB.Get('hitmapsAndCharge/'+h1name),ROOT.kGreen+1)
                h1SC = None # h1Struct(input_root_fileC.Get('hitmapsAndCharge/'+h1name),ROOT.kRed)
                DrawOverlayTH1F(h1SA, h1SB, h1SC)


                    
##################################
if __name__ == "__main__":        
    main()




    

