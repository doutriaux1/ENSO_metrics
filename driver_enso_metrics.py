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

#debug = True
debug = False

def tree(): return defaultdict(tree)

#########################################################
# SAMPLE COMMAND LINE EXECUTION USING ARGUMENTS BELOW
#########################################################
# python enso_bellenger_compute.py 
# -mp /work/cmip5/piControl/atm/mo/ts/cmip5.MODS.piControl.r1i1p1.mo.atm.Amon.ts.ver-1.latestX.xml
# -op /clim_obs/obs/ocn/mo/tos/UKMETOFFICE-HadISST-v1-1/130122_HadISST_sst.nc
# --mns ACCESS1-0 ACCESS1-3
# --var ts
# --varobs sst (varobs needed only when varname is different to model in obs)
# --outpd /work/lee1043/cdat/pmp/enso/test
# --outpj /work/lee1043/cdat/pmp/enso/test 
# --outnj output.json 
#########################################################

P = PMPParser() # Includes all default options

P.add_argument("--mp", "--modpath",
               type=str,
               dest='modpath',
               required=True,
               help="Explicit path to model monthly PR or TS time series")
P.add_argument("--op", "--obspath",
               type=str,
               dest='obspath',
               default='',
               help="Explicit path to obs monthly PR or TS time series")
P.add_argument('--mns', '--modnames',
               type=str,
               nargs='+',
               dest='modnames',
               required=True,
               help='Models to apply')
P.add_argument("--var", "--variable",
               type=str,
               dest='variable',
               default='ts',
               help="Variable: 'pr' or 'ts (default)'")
P.add_argument("--varobs", "--variableobs",
               type=str,
               dest='variableobs',
               default='',
               help="Variable name in observation (default: same as var)")
P.add_argument("--outpj", "--outpathjsons",
               type=str,
               dest='outpathjsons',
               default='.',
               help="Output path for jsons")
P.add_argument("--outnj", "--outnamejson",
               type=str,
               dest='jsonname',
               default='enso_bellenger.json',
               help="Output path for jsons")
P.add_argument("--outpd", "--outpathdata",
               type=str,
               dest='outpathdata',
               default='.',
               help="Output path for data")
P.add_argument("-e", "--experiment",
               type=str,
               dest='experiment',
               default='historical',
               help="AMIP, historical or picontrol")
P.add_argument("-c", "--MIP",
               type=str,
               dest='mip',
               default='CMIP5',
               help="put options here")
P.add_argument("-p", "--parameters",
               type=str,
               dest='parameters',
               default='',
               help="")

args = P.parse_args(sys.argv[1:])

modpath = args.modpath
obspath = args.obspath
mods = args.modnames
var = args.variable
varobs = args.variableobs
if varobs == '': varobs = var
outpathjsons = args.outpathjsons
outfilejson = args.jsonname
outpathdata = args.outpathdata
exp = args.experiment

##########################################################
libfiles = ['monthly_variability_statistics.py',
            'slice_tstep.py']

for lib in libfiles:
  execfile(os.path.join('./lib/',lib))

##########################################################

# Setup where to output resulting ---
try:
    jout = outpathjsons
    os.mkdir(jout)
except BaseException:
    pass

# Insert observation at the beginning of the loop ---
models = copy.copy(args.modnames)
if obspath != '':
    models.insert(0,'obs')

metrics = ['EnsoAmpl', 'EnsoMu']

# Dictionary to save result ---
# Use tree structure dictionary to avoid declearing everytime
enso_stat_dic = tree()

#=================================================
# Loop for Observation and Models 
#-------------------------------------------------
for mod in models:
    print ' ----- ', mod,' ---------------------'
  
    if mod == 'obs':
        file_path = obspath
        varname = varobs
        mods_key = 'OBSERVATION'
    else:
        file_path = modpath.replace('MODS', mod)
        varname = var
        mods_key = 'MODELS'
  
    try:
        #f = cdms2.open(file_path)   ### Major difference between Eric's code and this driver: where to open the file?! in driver? in lib?
        enso_stat_dic[mods_key][mod]['input_data'] = file_path
    
        if debug: print file_path 
      
        for metric in metrics:
            tmp_dict = EnsoAmpl(sstfile, sstname, ninobox)  ####### Temporay for placeholding!!!!!
        
            # Record returned metric dictionary to mother dictionay for json ---
            enso_stat_dic[mods_key][mod][metric]['entire'] = tmp_dict
        
            # Multiple centuries (only for models) ---   ###### Below part would be available once after we decide where to open file...
            if mod != 'obs':
                ntstep = len(reg_timeseries) # Assume input has monthly interval
                if debug:
                    itstep = 24 # 2-yrs
                else:
                    itstep = 1200 # 100-yrs
          
                for t in tstep_range(0, ntstep, itstep):
                    etstep = t+itstep
                    if etstep <= ntstep:
                        if debug: print t, etstep
                        reg_timeseries_cut = reg_timeseries[t:etstep] 
                        std = interannual_variabilty_std_annual_cycle_removed(reg_timeseries_cut)
                        std_NDJ = interannual_variability_seasonal_std_mean_removed(reg_timeseries_cut,'NDJ')
                        std_MAM = interannual_variability_seasonal_std_mean_removed(reg_timeseries_cut,'MAM')
                        tkey=str((t/12)+1)+'-'+str((etstep)/12)+'yrs'
                        enso_stat_dic[mods_key][mod][reg]['std'][tkey] = std
                        enso_stat_dic[mods_key][mod][reg]['std_NDJ'][tkey] = std_NDJ
                        enso_stat_dic[mods_key][mod][reg]['std_MAM'][tkey] = std_MAM
                        enso_stat_dic[mods_key][mod][reg]['seasonality'][tkey] = std_NDJ/std_MAM ## Fig. 3b of Bellenger et al. 2014
            
                enso_stat_dic[mods_key][mod]['entire_yrs'] = ntstep/12
        f.close()
    
    except:
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
    json_structure=["model", "index", "statistic", "period_chunk"],
    indent=4,
    separators=(
        ',',
        ': '),
    sort_keys=True)

sys.exit('done')
