#!/usr/bin/env python
# histoprint.py available at https://root.cern.ch/phpBB3/download/file.php?id=7592
import ROOT as r
import os,string,copy



#r.gROOT.Macro( os.path.expanduser( '~/macros/rootlogon.C' ) )

def isroot(s):
    """Returns true or false if the string is the name of a .root file."""
    try:
        if s.find('.root')!=-1:
            return True
        else:
            return False
    except AttributeError:
        print 'Call isroot(s) with a string s.'

def gethistoname(key):
    """From a ROOT TKey, this returns the actual name of the histogram associated with the key. """
    keystr = str(key)
    try:
        first = keystr.find('"',0,-1)
        second = keystr.find('"',first+1,-1)
        if first==-1 or second==-1:
            raise ValueError("Could not find double quotes in key name.")
        else:
            return keystr[first+1:second]
    except AttributeError:
        print 'Call gethistoname(key) with a key, or something which can be str()ed'

def closefiles(rootfiles):
    """Closes all files in the list."""
    for rootfile in rootfiles.keys():
        rootfiles[rootfile].Close()
    del(rootfiles)
    print "Don't forget to delete your histograms, they are now bad pointers!"
        
def colourize(histos_dict,stat=False):
    """Takes a dict of histograms as input, makes them all different colours.  If stat is true, it will also colourize the statsbox of the histos."""
    colours = [r.kBlue,r.kRed,r.kBlack,r.kGreen,r.kMagenta,r.kOrange,r.kCyan,r.kGray]
    l = len(colours)
    try: 
        runs = histos_dict.keys()
        runs.sort()
        i = 0
        for run in runs:
            histkeys = histos_dict[run].keys()
            histkeys.sort()
            for histkey in histkeys:
                histos_dict[run][histkey].SetLineColor(colours[i])
                histos_dict[run][histkey].SetMarkerColor(colours[i])
                if stat:
                    statbox = getstatbox(histos_dict[run][histkey])
                    statbox.SetTextColor(colours[i])
                i+=1
                i = i%l
    except AttributeError:
        try:
            i = 0
            histkeys = histos_dict.keys()
            histkeys.sort()
            for histkey in histkeys:
                histos_dict[histkey].SetLineColor(colours[i])
                histos_dict[histkey].SetMarkerColor(colours[i])
                if stat:
                    statbox = getstatbox(histos_dict[histkey])
                    statbox.SetTextColor(colours[i])
                i+=1
                i = i%l
        except AttributeError:
            print "colourize wants the big histos dict, or a dict of just histograms directly."
            raise

def slice_runs(histos,histo):
    """Takes a big dict-of-dict of histograms like the kind returned from loadhists and returns a simpler dict of histograms with the same name.  The names of the histograms are changed to be the run/sim from whence they came, to identify them later."""
    try:
        d = dict((run,histos[run][histo]) for run in histos)
    except KeyError:
        d = {}
        for run in histos:
            try:
                d[run] = histos[run][histo]
            except KeyError:
                continue
    for k in d:
        d[k].SetName(k)
    return d

def slice_histos(histos,run):
    """Simply slices a histos dict-of-dict of histograms by the run key."""
    d = histos[run]
    return d

def slice_keystring(histos,keystring):
    """Takes a dict of histograms (note, not a dict-of-dicts of histograms) and returns a dict with the histogtams whose keys contain the keystring and ONLY NUMBERS otherwise.  E.g. hists = slice_keystring(histos,'hNClusters') will return hNClusters0, but not hNClustersTrue.  Actually this function doesn't need them to be histograms, it simply returns a dict of the values whose keys match the string, so you can use it for other stuff."""
    d = {}
    histokeys = histos.keys()
    for histokey in histokeys:
        if histokey.find(keystring) != -1:
            stripkey = histokey.replace(keystring,'',1)
            if stripkey.isdigit():
                d[histokey] = histos[histokey]
    return d

def findleqsquare(n):
    """Finds the largest integer whose square is less than or equal to n."""
    for i in range(1,n):
        if i*i > n:
            return i-1
    return 1

def gooddimensions(n):
    """Returns good histogram layout for a split canvas."""
    width = findleqsquare(n)
    for height in range(0,n+1):
        if height*width >= n:
            return width,height
    raise ValueError('Could not find good dimensions.')

def findstatcoords(statbox):
    """Finds the coordinates of the given statbox."""
    x2 = statbox.GetX2NDC()
    y2 = statbox.GetY2NDC()
    x1 = statbox.GetX1NDC()
    y1 = statbox.GetY1NDC()
    return (x1,y1,x2,y2)

def getstatbox(histo):
    """Gets the statbox object from the histo."""
    lof = histo.GetListOfFunctions()
    statbox = lof.FindObject('stats')
    try:
        statbox.GetName();
        return statbox
    except ReferenceError:
        print 'getstatbox failed, remember that a histogram only gets a stat box once it is drawn.'
        raise

def movestatbox(statbox,x1,y1,x2,y2):
    """Moves the statbox to a new location.  Uses the NDC coordinates where the canvas is 1 wide and tall, (0,0) is the bottom left."""
    statbox.SetX1NDC(x1)
    statbox.SetX2NDC(x2)
    statbox.SetY1NDC(y1)
    statbox.SetY2NDC(y2)
    
def biggest(histos):
    """When multiple histos are draw, ideally the tallest one is drawn first, with he others using the same axes.  This function returns the key of the tallest histogram.  The input histos should be a dict of histograms."""
    return max(histos,key=lambda hist: histos[hist].GetMaximum())
    
def draw_tiled(histos_in,title=None,makelegend=True):
    """Draws multiple histos in a split canvas.  The arrangement is determined by gooddimensions().  The input should be a dict of histograms, pre-coloured if necessary.  The title argument sets the canvas title, histogram keys are used to label the individual pads."""
    histos = copy.deepcopy(histos_in)
    c1 = r.TCanvas()
    c1.Divide(*gooddimensions(len(histos)+int(makelegend))) # int(makelegend) makes the legend take up a histogram slot.
    if title:
        c1.SetTitle(title)
    count = 1
    if makelegend:
        legend = r.TLegend(0.1,0.1,0.9,0.9)
    histkeys = histos.keys()
    histkeys.sort()
    for histkey in histkeys:
        c1.cd(count)
        if makelegend:
            legend.AddEntry(histos[histkey],histkey,'l')
        histos[histkey].Draw()
        count+=1
    if makelegend:
        c1.cd(count)
        legend.Draw()
    r.gPad.Update()
    raw_input('Push enter to continue.')

def leftordown(boxpos,width,height):
    """Given a maximum width or height, returns whether the next statbox should be left of the current one, or on the next line."""
    bp1 = (boxpos[0]+1,boxpos[1]+1)
    if bp1[0] <= width:
        return 'left'
    elif bp1[1] <= height:
        return 'down'
    else:
        raise IndexError('bp1 exceeds gooddimensions!')

def draw_stacked(histos_in,title=None):
    """Draws multiple histos on the same pad, stacked on top of each other."""

    #OptStat is set by "ksiourmen"
    #kurtosis, skewness, integral, n_overflows, n_underflows,
    #rms, mean, n_entries, name
    #k,s,r,m can be 0, 1 or 2 (to get error)
    #all others can be 0 or 1
    #do not include leading 0s, else get hexed.
    oldstyle = r.gStyle.GetOptStat()
    #r.gStyle.SetOptStat(1201) #RMS, Mean with error, and name
    r.gStyle.SetOptStat(110011) # both overflows, n_entries, name.
    oldH = r.gStyle.GetStatH()
    r.gStyle.SetStatH(0.10)

    histos = copy.deepcopy(histos_in)
    width,height = gooddimensions(len(histos))

    c1 = r.TCanvas()
    if title:
        c1.SetTitle(title)
    count = 1

    bigkey = biggest(histos)
    histos_keys = histos.keys()
    histos_keys.sort()
    histos_keys.remove(bigkey)
    histos_keys.insert(0,bigkey)

    boxpos = ()
    first = True
    for h in histos_keys:
        if first:
            histos[h].Draw()
            r.gPad.Update()
            statbox = getstatbox(histos[h])
            Ox1,Oy1,Ox2,Oy2 = findstatcoords(statbox)
            boxpos = (1,1)
            first = False
        else:
            histos[h].Draw('sames')
            r.gPad.Update()
            go = leftordown(boxpos,width,height)
            statbox = getstatbox(histos[h])
            if go == 'left':
                movestatbox(statbox,x1-(x2-x1),y1,x2-(x2-x1),y2)
                boxpos = (boxpos[0]+1,boxpos[1])
            elif go == 'down':
                movestatbox(statbox,Ox1,y1-(y2-y1),Ox2,y2-(y2-y1))
                boxpos = (1,boxpos[1]+1)
            r.gPad.Modified()

        x1,y1,x2,y2 = findstatcoords(statbox)
        colourize_statbox(histos[h])
        r.gPad.Modified()
        r.gPad.Update()
        count += 1
    r.gPad.Update()
    raw_input('Push enter to continue.')
    r.gStyle.SetOptStat(oldstyle)
    r.gStyle.SetStatH(oldH)

def colourize_statbox(histo):
    """Takes a histogram (already drawn) and makes the statbox the same colour as the line or marker."""
    statbox = getstatbox(histo)
    
    marker_colour = histo.GetMarkerColor()
    line_colour = histo.GetLineColor()
    if not marker_colour == line_colour:
        raise ValueError('Marker and line colour not the same, check colourizing code.')
    
    statbox.SetTextColor(marker_colour)
    return 1

def hists_from_file(filepath):
    """Function used by loadhists to load the histograms from a single file located at filepath.  The return value is a tuple with the rootfile object and the dict of histograms from that file."""
    histos = {}
    rootfile = r.TFile(filepath)
    rootfile.cd()
    listofkeys = rootfile.GetListOfKeys()
    tit = r.TIter(listofkeys)
    tit.Reset()
    key = tit.Next()
    while key:
        histoname = gethistoname(key)
        histos[histoname] = rootfile.Get(histoname)
        key = tit.Next()
    return rootfile,histos

def loadhists(runs=None,rootnames=None,nocolour=False):
    """Loads histograms from files and returns two dicts.  The first has all the open ROOT files, the second has all the histograms.  runs should just be a list of numbers.  rootnames should be the base name of the root files to open, a list of the same length as runs.  This function will clear any previous dicts called histos and rootfiles.  The nocolour option can be used for sadness.  Call this function as rootfiles,histos = loadhists(blabla)."""
    histos = {}
    rootfiles = {}
    if len(runs) != len(rootnames):
        print "First two arguments must be lists of the same length"
        return
    for k,run in enumerate(runs):
        thiskey = "Run{0:0>4}".format(run)
        rootpath = os.path.join("/Users/jfcaron/Projects/TRIUMFBeamTest/rootfiles/Outputs",thiskey,rootnames[k])
        rootfiles[thiskey], histos[thiskey] = hists_from_file(rootpath)
        
    if not nocolour:
        colourize(histos)
    return rootfiles,histos
        
def listruns():
    """Lists root files available to load."""
    rootlist = []
    rundir = '/Users/jfcaron/Projects/TRIUMFBeamTest/rootfiles/Outputs'
    rawlist = os.listdir(rundir)
    rawlist = [os.path.join(rundir,d) for d in rawlist]
    dirlist = filter(os.path.isdir,rawlist)
    for adir in dirlist:
        print adir
        rawlist = os.listdir(adir)
        roots = [r for r in rawlist if r.endswith('.root')]
        print roots
        # try:
        #     rootlist.extend(filter(isroot,rawlist))
        # except TypeError:
        #     print adir,'has no root file.'
        #     pass
    return

#sims = range(40,44)
#runs = range(196,200)
#rootfiles,histos = loadhists(sims,runs)

#d = slice_runs(histos,'hNClusters3')

def normalize(histo,area=1):
    """Rescales a histogram to have a given area."""
    integral = histo.Integral()
    histo.Scale(area/integral)
    return
