import rasterio
from rasterio.plot import show

# from rasterio.enums import Resampling
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("agg")
from PIL import Image
import subprocess
import os


##################
#### FOR ORTHO
##################
def geotif_to_overview(geotif, out_dir):
    """
    Convert large geotif to a preview using rasterio
    
    Parameters
    ----------
    geotif: str
                name of geotif
    out_dir: str
                output directory
    """    
    out_tif = os.path.join(
        out_dir, "01_" + geotif.split(".")[0] + "geotif_overview.png"
    )
    with rasterio.open(geotif) as rast:
        ax = show(rast)  # show returns the axes NOT the figure!
        ax.figure.savefig(out_geotif)


def geotif_to_overview2(geotif, out_dir):
    """
    Convert large geotif to a preview using gdal (less usage of RAM)
    
    Parameters
    ----------
    geotif: str
                name of geotif
    out_dir: str
                output directory
    """   
    out_tif = os.path.join(
        out_dir, "01_" + geotif.split(".")[0] + "geotif_overview.tif"
    )
    comp = subprocess.call(
        "gdal_translate -of COG -tr 1 1 -r bilinear " + geotif + " " + out_tif,
        shell=True,
    )
    return comp


##################
### FOR RAW IMAGES
##################
def series_to_img(images, out_dir):
    """
    Generate image with a set of images

    Parameters
    ----------
    images: list
                List of images
    out_dir: str
                Output directory
    """
    outfile = os.path.join(out_dir, "00_sample_rawdata_overview.png")
    print("Nb images: ", len(images))
    line = 8
    if len(images) < 64:
        line = int(len(images) / 8)
    else:
        line = 8

    print("preview 8 x ", line)

    fig, axs = plt.subplots(8, line)
    for imgs, ax in enumerate(axs.flat):
        img = Image.open(images[imgs])
        # try:
        #     # Image.open(images[imgs])
        #     img = Image.open(images[imgs])
        #     # print("image is valid")
        ax.imshow(img)
        ax.axis("off")  # to hide the axes
        # except:
        #     print("image " + images[imgs] + " not valid !")
        # plt.figure(frameon=False)
    ax.figure.savefig(outfile, dpi=150)

