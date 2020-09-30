import ROOT
def createPDF(file_list,outputfilename, rphi=True):
    leg = ROOT.TLegend(0.35,0.75,0.75,0.88,"","brNDC")
    leg.SetBorderSize(1)
    leg.SetTextSize(0.05)
    leg.SetLineColor(10)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(10)
    leg.SetFillStyle(1001)
    c1 = ROOT.TCanvas("c1","",600,800)
    c1.Divide(2,2)
    ic = 0
    mycanvas = ""

    for ifile in file_list:
        ic=ic+1
        myfile = ROOT.TFile(ifile)        
        if rphi:
            mycanvas = myfile.Get("cResVsEta_1")
        else:
            mycanvas = myfile.Get("cResVsEta_2")
        myhisto1 = mycanvas.GetPrimitive("h_resRPhivsEta_qlow")
        myhisto2 = mycanvas.GetPrimitive("h_resRPhivsEta_qhigh") 
        if not rphi:
            myhisto1 = mycanvas.GetPrimitive("h_resZvsEta_qlow")
            myhisto2 = mycanvas.GetPrimitive("h_resZvsEta_qhigh")  
        myhisto1.SetTitle(myhisto1.GetTitle()+" "+ifile.split("/")[0].split("plots_")[1])               
        myhisto2.SetTitle(myhisto2.GetTitle()+" "+ifile.split("/")[0].split("plots_")[1])   
        myhisto1.GetYaxis().SetRangeUser(0,20)            
        myhisto2.GetYaxis().SetRangeUser(0,20)
        if not rphi:
            myhisto1.GetYaxis().SetRangeUser(0,60)            
            myhisto2.GetYaxis().SetRangeUser(0,60)          
        c1.cd(ic)
        if ic == 1:
            leg.AddEntry(myhisto1,"primaries Q/#LTQ#GT<1","lpf")                        
            leg.AddEntry(myhisto2,"primaries 1<Q/#LTQ#GT<1.5","lpf")
        myhisto1.Draw("same")
        myhisto2.Draw("same")
        leg.Draw()
 

    c1.SaveAs(outputfilename)

ROOT.gROOT.SetBatch()
cases = ["T23","T23_ALL","T23_RMS","T23_ALL_RMS"]
files_rphi = []
files_rz = []
for icase in cases:
    dir = "plots_"+icase
    files_rphi.append(dir+"/rmsVsEta_rphi.root")
    files_rz.append(dir+"/rmsVsEta_rz.root")
outputfilename = "plots_muons_T23"
createPDF(files_rphi,outputfilename+"_rphi.pdf")
createPDF(files_rz,outputfilename+"_rz.pdf",False)

cases = ["T23_Layer2","T23_Layer2_ALL","T23_Layer2_RMS","T23_Layer2_ALL_RMS"]
files_rphi = []
files_rz = []
for icase in cases:
    dir = "plots_"+icase
    files_rphi.append(dir+"/rmsVsEta_rphi.root")
    files_rz.append(dir+"/rmsVsEta_rz.root")
outputfilename = "plots_muons_T23_Layer2"    
createPDF(files_rphi,outputfilename+"_rphi.pdf")
createPDF(files_rz,outputfilename+"_rz.pdf",False)

cases = ["plots_muon_T22_gaussfit_L1_S2_nEv_2000000","plots_muon_T21_gaussfit_L1_S2_nEv_2000000","plots_muon_T23_gaussfit_L1_S2_nEv_2000000"]
files_rphi = []
files_rz = []
for icase in cases:
    dir = icase
    files_rphi.append(dir+"/rmsVsEta_rphi.root")
    files_rz.append(dir+"/rmsVsEta_rz.root")
outputfilename = "plots_muons_allGeometries_endcap"
createPDF(files_rphi,outputfilename+"_rphi.pdf")
createPDF(files_rz,outputfilename+"_rz.pdf",False)


