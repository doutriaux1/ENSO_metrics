#!/usr/bin/env python

import logging
LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)

import cdms2
import copy
import sys
import os
import string
import json
import pcmdi_metrics
from pcmdi_metrics.pcmdi.pmp_parser import PMPParser
import collections
from collections import defaultdict
from EnsoMetricsLib import EnsoAmpl, EnsoMu

debug = True
#debug = False

def tree(): return defaultdict(tree)

#########################################################

P = PMPParser() # Includes all default options

P.add_argument("-mp", "--modpath",
               type=str,
               dest='modpath',
               help="Directory path to model monthly field")
P.add_argument("-op", "--obspath",
               type=str,
               dest='obspath',
               help="Directory path to obs monthly field")
P.add_argument("-mns", "--modnames",
               type=str,
               dest='modnames',
               help="List of models to apply")
P.add_argument("-varobs", "--variableobs",
               type=str,
               dest='variableobs',
               help="Variable name in observation")
P.add_argument("-outpj", "--outpathjsons",
               type=str,
               dest='outpathjsons',
               help="Output path for jsons")
P.add_argument("-outnj", "--outnamejson",
               type=str,
               dest='outnamejson',
               help="Output path for jsons")
P.add_argument("-outpd", "--outpathdata",
               type=str,
               dest='outpathdata',
               help="Output path for data")
P.add_argument("-mx", "--metrics",
               type=str,
               dest='metrics',
               help="List of metrics")

param = P.get_parameter()

modpath = param.modpath
obspath = param.obspath
mods = param.modnames
var = param.variable
varobs = param.variableobs
if varobs == '': varobs = var
outpathjsons = param.outpathjsons
outfilejson = param.outnamejson
outpathdata = param.outpathdata
metrics = param.metrics

print modpath
print obspath
print mods
print var
print metrics

##########################################################
libfiles = ['monthly_variability_statistics.py',
            #'slice_tstep.py',
           ]

#for lib in libfiles:
#  execfile(os.path.join('.',lib))
##########################################################

# Setup where to output resulting ---
try:
    jout = outpathjsons
    os.mkdir(jout)
except BaseException:
    pass

# Insert observation at the beginning of the loop ---
models = copy.copy(param.modnames)
#if obspath != '':
#    models.insert(0,'obs')
#............... Let's think about OBS data later...

# Variable name and nino box
sstName = 'ts'
tauxName= 'tauu'
ninoBox = 'nino3'

# Dictionary to save result ---
enso_stat_dic = tree() # Use tree dictionary to avoid declearing everytime

#=================================================
# Loop for Observation and Models 
#-------------------------------------------------
for mod in models:
    print ' ----- ', mod,' ---------------------'
  
    #if mod == 'obs':
    #    file_path = obspath
    #    varname = varobs
    #    mods_key = 'OBSERVATION'
    #else:
    #    file_path = modpath.replace('MODS', mod)
    #    varname = var
    #    mods_key = 'MODELS'
    #............... Let's think about OBS data later...

    sstFile = (modpath.replace('MOD', mod)).replace('VAR',sstName) ## Will need land mask out at some point...!
    tauxFile = (modpath.replace('MOD', mod)).replace('VAR',tauxName)

    print sstFile
    print tauxFile
  
    #try:
    if 1:
        #f = cdms2.open(file_path)   ### Major difference between Eric's code and this driver: where to open the file?! in driver? in lib?
        #enso_stat_dic[mods_key][mod]['input_data'] = file_path
    
        #if debug: print file_path 
      
        for metric in metrics:

            print metric

            if metric == 'EnsoAmpl':
                tmp_dict = EnsoAmpl(sstFile, sstName, ninoBox)
                tmp_dict['input_data'] = [sstFile]
            elif metric == 'EnsoMu':
                tmp_dict = EnsoMu(sstFile, tauxFile, sstName, tauxName)
                tmp_dict['input_data'] = [sstFile, tauxFile]
        
            enso_stat_dic[mod][metric] = tmp_dict
        
    else:
    #except:
        print 'failed for ', mod
  
#=================================================
#  OUTPUT METRICS TO JSON FILE
#-------------------------------------------------
OUT = pcmdi_metrics.io.base.Base(os.path.abspath(jout), outfilejson)

disclaimer = open(
    os.path.join(
        sys.prefix,
        "share",
        "pmp",
        "disclaimer.txt")).read()

metrics_dictionary = collections.OrderedDict()
metrics_dictionary["DISCLAIMER"] = disclaimer
metrics_dictionary["REFERENCE"] = "The statistics in this file are based on Bellenger, H et al. Clim Dyn (2014) 42:1999-2018. doi:10.1007/s00382-013-1783-z"
metrics_dictionary["RESULTS"] = enso_stat_dic  # collections.OrderedDict()

OUT.var = var
OUT.write(
    metrics_dictionary,
    json_structure=["model", "metric", "item", "value or description"],
    indent=4,
    separators=(
        ',',
        ': '),
    sort_keys=True)

sys.exit('done')
