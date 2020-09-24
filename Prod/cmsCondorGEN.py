#!/usr/bin/env python



import os, sys,  imp, re, pprint, string
from optparse import OptionParser

# cms specific
import FWCore.ParameterSet.Config as cms

import time
import datetime
import os
import sys
import shlex
import subprocess

def runCommand(commandLine):
    #sys.stdout.write("%s\n" % commandLine)
    args = shlex.split(commandLine)
    retVal = subprocess.Popen(args, stdout = subprocess.PIPE)
    return retVal



MYDIR=os.getcwd()
#folder = '/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Summer16_FlatPU28to62/HLTRates_v4p2_V2_1p25e34_MC_2017feb09J'

#get inputs
from optparse import OptionParser
parser=OptionParser()
parser.add_option("-n",dest="nTot",type="int",default=10000,help="NUMBER of total events produced",metavar="NUMBER")
parser.add_option("-q","--flavour",dest="jobFlavour",type="str",default="workday",help="job FLAVOUR",metavar="FLAVOUR")
parser.add_option("-g","--geometry",dest="geometry",type="str",default="T23",help="geometry",metavar="GEOMETRY")

opts, args = parser.parse_args()


help_text = '\n./cmsCondor.py <cfgFileName> <CMSSWrel> <remoteDir> -f <geometry> -n <nPerJob> -q <jobFlavour>'
help_text += '\n<cfgFileName> (mandatory) = name of your configuration file (e.g. hlt_config.py)'
help_text += '\n<CMSSWrel> (mandatory) = directory where the top of a CMSSW release is located'
help_text += '\n<remoteDir> (mandatory) = directory where the files will be transfered (e.g. on EOS)'
help_text += '\n<geometry> (mandatory) = pixel geometry'
help_text += '\n<nTot> (optional) = NUMBER of total events produced (default=10K)'
help_text += '\n<flavour> (optional) = job flavour (default=workday)\n'


cfgFileName = str(args[0])
cfgFileName = cfgFileName+"_"+opts.geometry+".py"
cmsEnv = str(args[1])
remoteDir = str(args[2])
geometry = opts.geometry
print 'config file = %s'%cfgFileName
print 'CMSSWrel = %s'%cmsEnv
print 'remote directory = %s'%remoteDir
print 'job flavour = %s'%opts.jobFlavour

#make directories for the jobs
try:
    os.system('rm -rf Jobs/'+geometry)
    os.system('mkdir Jobs')
except:
    print "err!"
    pass


sub_total = open("sub_total.jobb","w")

#copy MC datasets file here so it can be used

#retrieve MC datasets, query DAS, and make a list of input files

nEventsPerJob = 500
# load cfg script
handle = open(cfgFileName, 'r')
cfo = imp.load_source("pycfg", cfgFileName, handle)
process = cfo.process
handle.close()
process.maxEvents.input = cms.untracked.int32(nEventsPerJob)
# keep track of the original source
fullSource = process.source.clone()
    
    
nJobs = -1

nFiles = opts.nTot
nJobs = nFiles / nEventsPerJob
if (nJobs!=0 and (nFiles % opts.nTot) > 0) or nJobs==0:
    nJobs = nJobs + 1
        
#print "dataset: ", dataset
print "(approximate) number of jobs to be created: ", nJobs
        

jobCount=0
last_kFileMax=0
datasetJobDir='Jobs/'+geometry
datasetRemoteDir=remoteDir+'/'+geometry
os.system('mkdir '+datasetJobDir)
os.system('mkdir '+datasetRemoteDir)
print "Geometry: ", geometry
#make job scripts
keepGoing=True
i=0
while (keepGoing):
    #print 'total: %d/%d  ;  %.1f %% processed '%(j,my_sum,(100*float(j)/float(my_sum)))
    jobDir = MYDIR+"/"+datasetJobDir+'/Job_%s/'%str(i)
    os.system('mkdir %s'%jobDir)
    tmp_jobname="sub_%s.sh"%(str(i))
    tmp_job=open(jobDir+tmp_jobname,'w')
    tmp_job.write("#!/bin/sh\n")
    #tmp_job.write("ulimit -v 5000000\n")
    tmp_job.write("cd $TMPDIR\n")
    tmp_job.write("mkdir Job_%s\n"%str(i))
    tmp_job.write("cd Job_%s\n"%str(i))
    tmp_job.write("cd %s\n"%(cmsEnv))
    tmp_job.write("eval `scramv1 runtime -sh`\n")
    tmp_job.write("cd -\n")
    tmp_job.write("cp -f %s* .\n"%(jobDir))
    tmp_job.write("cmsRun run_cfg.py\n")
    tmp_job.write("echo 'sending the file back'\n")
    tmp_job.write("cp step1.root %s/step1_%s.root\n"%(datasetRemoteDir, str(i)))
    tmp_job.write("rm step1.root\n")
    tmp_job.close()
    os.system("chmod +x %s"%(jobDir+tmp_jobname))

    print "preparing job number %s"%str(jobCount)
    jobCount += 1

    kFileMin = i*nEventsPerJob
    kFileMax = (i+1)*nEventsPerJob
    tmp_cfgFile = open(jobDir+'/run_cfg.py','w')
    process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(jobCount*100)
    tmp_cfgFile.write(process.dumpPython())
    tmp_cfgFile.close()
    i+=1

    if (kFileMax > opts.nTot):
        keepGoing=False                

    
    
condor_str = "executable = $(filename)\n"

condor_str += "arguments = $Fp(filename) $(ClusterID) $(ProcId)\n"
condor_str += "output = $Fp(filename)hlt.stdout\n"
condor_str += "error = $Fp(filename)hlt.stderr\n"
condor_str += "log = $Fp(filename)hlt.log\n"
condor_str += '+JobFlavour = "%s"\n'%opts.jobFlavour
condor_str += "+AccountingGroup = \"group_u_CMS.CAF.PHYS\"\n"
condor_str += "queue filename matching ("+MYDIR+"/Jobs/"+geometry+"/Job_*/*.sh)"
condor_name = MYDIR+"/condor_cluster.sub"
condor_file = open(condor_name, "w")
condor_file.write(condor_str)
sub_total.write("condor_submit %s\n"%condor_name)
os.system("chmod +x sub_total.jobb")
