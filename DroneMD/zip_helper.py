import os
import zipfile
import shutil


def zip_folder(folder_path, file_zip):
    """
    Simple create zip function.
    
    Parameters
    ----------
    folder_path: input folder
    file_zip: output zip without extension `.zip`
    """
    create_zip = shutil.make_archive(file_zip, "zip", folder_path)
    return create_zip


def zip_each_folder(input, dataframe):
    """
    Compress each subfolder in session.
    Allow better manipulation for Zenodo upload
    
    Parameters
    ----------
    input: str
                input folder where zip will be available
    dataframe: class 'pandas.core.frame.DataFrame'
                Metadata entities (geoflow format)
    """
    for i in range(len(dataframe)):
        print("INFO: Ziping " + dataframe.iloc[i]["Identifier"])
        dir_to_zip = os.path.join(input, dataframe.iloc[i]["Identifier"])
        for folder in os.listdir(dir_to_zip):
            if os.path.isdir(os.path.join(dir_to_zip, folder)):
                zip_folder(
                    os.path.join(dir_to_zip, folder), os.path.join(dir_to_zip, folder)
                )
            else:
                print("    INFO: " + folder + " is not a folder")
                pass


def unzip(folder_path, file_zip, sub_folder_output):
    """
    Unzip files
    
    Parameters
    ----------
    folder_path: str
                Folder where zip is available
    file_zip: str
                zip file
    sub_folder_output: str
                Folder name of extracted zip
    """
    with zipfile.ZipFile(os.path.join(folder_path, file_zip), "r") as zipf:
        zipf.extractall(path=os.path.join(folder_path, sub_folder_output))
    return zipf

