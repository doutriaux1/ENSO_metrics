# Directory path for observation
obspath = "/clim_obs/obs/ocn/mo/tos/UKMETOFFICE-HadISST-v1-1/130122_HadISST_sst.nc"

# Directory path for models
modpath = "/work/cmip5/piControl/atm/mo/VAR/cmip5.MOD.historical.r1i1p1.mo.atm.Amon.VAR.ver-1.latestX.xml"
modnames = "IPSL-CM5A-LR" #"ACCESS1-0 ACCESS1-3"

# Variables
variable = "ts"
variableobs = "sst"

# Output
outpathdata = "/work/lee1043/cdat/pmp/enso/test"
outpathjsons = "/work/lee1043/cdat/pmp/enso/test"
outnamejson = "test.json"

# Metrics
#metrics = ['EnsoAmpl', 'EnsoMu']
metrics = ['EnsoAmpl']

# Variable name and nino box
sstName = 'ts'
tauxName= 'tauu'
ninoBox = 'nino3'
