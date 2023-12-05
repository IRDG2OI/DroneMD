import os
from PIL import Image

def check_image_with_pil(path):
    """
    Check if image is valid
    
    Parameters
    ----------    
    path: str
                path to analyze
    """
    try:
        Image.open(path)
    except IOError:
        im_error = "Not an image: " + path
        return im_error

def im_list(path):
    """
    Images list of folder and subfolder
    
    Parameters
    ----------
    path: str
                path to analyze
    """
    types = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    images_list = []
    images_list = [os.path.join(root, name)
                for root, dirs, files in os.walk(path)
                for name in files
                if name.endswith(types)]
    return images_list

