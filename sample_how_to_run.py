#!/usr/bin/env python

import logging
LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)

import subprocess

### Commend could be either way:

cmd = """./driver_enso_metrics.py \
         -mp /work/cmip5/piControl/atm/mo/ts/cmip5.MODS.piControl.r1i1p1.mo.atm.Amon.ts.ver-1.latestX.xml \
         -op /clim_obs/obs/ocn/mo/tos/UKMETOFFICE-HadISST-v1-1/130122_HadISST_sst.nc \
         -mns ACCESS1-0 ACCESS1-3 \
         -v ts \
         -varobs sst \
         -outpd /work/lee1043/cdat/pmp/enso/test \
         -outpj /work/lee1043/cdat/pmp/enso/test \
         -outnj cmip5_enso_bellenger_ACCESS1-0_ACCESS1-3.json """

# or..

#cmd = """./driver_enso_metrics.py -p my_parameter.py"""

subprocess.Popen(cmd, shell=True)
