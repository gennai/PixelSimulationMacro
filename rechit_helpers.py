#!/usr/bin/env python

import math

# conversion factors
CmToUm = 10000.       # length -> from cm to um
ToKe = 0.001          # charge -> from e to ke
ELossSilicon = 78.    # 78 e-h pairs/um in Silicon
TanThetaL = 0.106*3.8 # Lorentz Angle
##################################################


#######################################
def NotModuleEdge(x_local, y_local):
######################################
    """ x_local, y_local in um - tuned for phase 1 """

    accept = True
    if math.fabs(x_local)>7900. or math.fabs(y_local)>31150.:  # or alternativley if math.fabs(x_local)>7750. or math.fabs(y_local)>31150.:  #
        accept = False

    return accept

#######################################
def NotModuleEdgePhase2(layer, row,col,spreadx,spready):
# TODO: reimplement this function to add a cut on x_local with edges defined based on layer/ring
######################################
    """ x_local, y_local in um - to be tuned for phase2 """
    #metterci il check se c'e' un pixl column vicino a 0 o al max, e' piu' facile. E farlo solo nel barrel?
    accept = True
    maxSizeY = 867
    maxSizeX = 336
    if layer > 2: 
        maxSizeY = 676
    edgex_min = row - spreadx*0.5
    edgey_min = col - spready*0.5
    edgex_max = row + spreadx*0.5
    edgey_max = col + spready*0.5
    if abs(edgex_min) < 5 or abs(edgey_min) < 5:
        accept = False
    if abs(edgex_max -maxSizeX) < 5 or abs(edgey_max-maxSizeY) < 5:
        accept = False
    #return accept
    return True


##############################################################
def NotDeltaCandidate(cos_alpha, pitch_x, spread_x, cos_beta, pitch_y, spread_y, thickness):
#############################################################
    """ flag delta ray candidates comparing expected and measured width of the cluster USED IT WITH CARE!"""
    
    is_delta = False
    the_alpha = math.acos(cos_alpha) 
    the_beta = math.acos(cos_beta) 
    # expected widths of the cluster in units of the pitch
    w_x = thickness*(math.tan(0.5*math.pi-the_alpha)+TanThetaL)/(pitch_x*CmToUm)
    w_y = thickness*(math.tan(0.5*math.pi-the_beta))/(pitch_y*CmToUm)                


    if (w_x-spread_x < -1.8) or (w_x-spread_x > 0.2) or (w_y-spread_y < -2.01):
        is_delta = True
    
    return not is_delta

