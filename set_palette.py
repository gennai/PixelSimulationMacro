#!/usr/bin/env python

import ROOT
import array

###############################################
def set_palette(name='palette', ncontours=255):
###############################################
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""

    if name == "grey" or name == "greyscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    elif name == "redblue":
        stops = [ 0.00, 0.50, 1.00]
        red   = [ 0.00, 0.99, 1.00]
        green = [ 0.00, 0.99, 0.00]
        blue  = [ 1.00, 0.99, 0.00]
        # (define more palettes)
    elif name == "cividis":
        stops = [ 0.00, 0.50, 1.00]
        red   = [ 1.00, 0.55, 0.10]
        green = [ 1.00, 0.55, 0.10]
        blue  = [ 0.10, 0.45, 0.80]
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

    s = array.array('d', stops)
    r = array.array('d', red)
    g = array.array('d', green)
    b = array.array('d', blue)

    npoints = len(s)
    ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)

