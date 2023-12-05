from rpy2.robjects.packages import importr
import os

try:
    geoflow = importr('geoflow', lib_loc="~/R/x86_64-pc-linux-gnu-library/4.3")
except:
    try:
        geoflow = importr('geoflow', lib_loc="/usr/lib/R/library")
    except:
        pass

def run_geoflow(config, geoflow_folder):
    """
    Execute geoflow
    
    Parameters
    ----------
    config: str
                json to execute
    geoflow_folder: str
                geoflow folder where json is available if relative path in json
                jobs will be stored in this folder    
    """
    os.chdir(geoflow_folder)
    gf = geoflow.executeWorkflow(config)
    # gf = geoflow.initWorkflow(config)
    return gf
