import requests
import json
import os
import time
import pandas as pd
# import mimetypes
import settings

zenodo_baseurl = "https://zenodo.org/api/"
headers = {"Content-Type": "application/json"}
ACCESS_TOKEN = settings.ZENODO

def zenlist_all(base_url, token):
    """
    Return list of all Zenodo records
    
  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
        
    e.g.: 
    # List of records:
    zenlist_all("https://zenodo.org/api", token)
    """
    r = requests.get(base_url + "deposit/depositions", params={"access_token": token})
    return r


def zenlist_all_query(base_url, token, query):
    """
    Return list of all Zenodo records and a query
    
  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    query: str
                keyword you want to look for

    e.g.: 
    # List of records with keywords:
    zenlist_all_query("https://zenodo.org/api", token, "G2OI")
    """
    r = requests.get(
        base_url + "deposit/depositions", params={"q": query, "access_token": token}
    )
    return r


def zenlist_single(base_url, token, record_id):
    """
    Return details of one Zenodo record
    
  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                Zenodo record id

    e.g.: 
    # Details of single record:
    zenlist_single("https://zenodo.org/api", token, 10064384)
    """
    r = requests.get(
        base_url + "deposit/depositions/" + str(record_id), params={"access_token": token}
    )
    return r

def zen_latest(base_url, token, record_id):
    """
    Return latest record_id of query record
    
  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                Zenodo record id
    
    e.g.: 
    # List of latest record:
    zenlist_all("https://zenodo.org/api", token)
    """
    # POST /api/records/{id}/versions/latest
    # r = requests.post(
        # base_url + "deposit/depositions/" + record_id + "/actions/newversion",
    r = requests.post(base_url + "records/" + str(record_id) + "/versions/latest",
        params={"access_token": token},
    )
    return r

def zenlist_single_files(base_url, token, record_id):
    """
    Return files of one Zenodo record

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                Zenodo record id

    e.g.: 
    # List of files:
    zenlist_single("https://zenodo.org/api", token, 10064384)
    """
    r = requests.get(
        base_url + "deposit/depositions/" + str(record_id) + "/files",
        params={"access_token": token},
    )
    return r


def zen_registerid(base_url, token, record_id):
    """
    Register conceptdoi from draft

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                Zenodo record id

    e.g.: 
    # List of records:
    zenlist_single("https://zenodo.org/api", token, 10064384)
    """
    r = requests.post(
        base_url + "deposit/depositions/" + str(record_id) + "/actions/registerconceptdoi",
        params={"access_token": token},
    )
    return r

def zen_del_file(url, token):
    """
    Delete file on zenodo platform

  Parameters
  ----------
    url: str
                url of zenodo file
    token: str
                zenodo access token
    """
    r = requests.delete(
        url,
        params={'access_token': ACCESS_TOKEN}
    )

def zen_newversion(base_url, token, record_id):
    """
    Create a new DOI version

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    """
    # POST /api/records/{id}/draft
    r = requests.post(
        base_url + "deposit/depositions/" + record_id + "/actions/newversion",
        # r = requests.post(base_url + "records/" + record_id + "/draft",
        params={"access_token": token},
    )
    return r


def zen_unlock_submited(base_url, token, record_id):
    """
    Unlock published version to update metadata

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    """
    r = requests.post(
        base_url + "deposit/depositions/" + record_id + "/actions/edit",
        params={"access_token": token},
    )
    return r


def check_token(base_url, token):
    """
    Function to check if Zenodo token is allowed to deposit files

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    """
    r = requests.post(
        base_url + "deposit/depositions",
        params={"access_token": token},
        json={},
        headers=headers,
    )
    if r.status_code == 201:
        print("Allowed to deposit some files")
    else:
        print("Please check your token or url")
    return r


def zenvar(requests_response):
    """
    Store 3 variables in a list:
    - bucket_url
    - Reserved DOI
    - Record id
    from check_token function

  Parameters
  ----------
    requests_response: Python requests.Response Object
                answer from check_token
    """
    bucket_url = requests_response.json()["links"]["bucket"]
    reserved_doi = requests_response.json()["metadata"]["prereserve_doi"]["doi"]
    recid = requests_response.json()["metadata"]["prereserve_doi"]["recid"]
    return [bucket_url, reserved_doi, recid]


def zenfiles(base_url, token, record_id):
    """
    Retrieve uploaded files
    
  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    """    
    r = requests.post(
        base_url + "deposit/depositions/" + record_id + "/files",
        # r = requests.post(base_url +"records/" + record_id + "draft/files",
        params={"access_token": token},
    )
    return r


def zenul(bucket_url, token, folder, filename):
    """
    Upload new files to Zenodo
    The target URL is a combination of the base url with records, record_id and files seperated by a slash.
    folder: str

    Parameters
    ----------
    bucket_url: str
                Zenodo bucket url
    token: str
                Zenodo token
    filename: list
                Filename to upload
    """
    for i in range(len(filename)):
        print("    Sleep 5 seconds before new upload")
        time.sleep(5)
        print("upload: " + filename[i])
        
        absfilename = os.path.join(folder, filename[i])
        
        url = "%s/%s" % (bucket_url, filename[i])
    
        with open(absfilename, "rb") as fp:
            data = fp.read()
        
        r = requests.put(
                url,
                data=data,
                params={"access_token": token},
                headers = {
                    'content-type': 'application/octet-stream'
                },
            )

    return r


def zenul2(base_url, record_id, token, folder, filename):
    """
    Upload new files to Zenodo
    The target URL is a combination of the base url with records, record_id and files seperated by a slash.
    folder: str

    Parameters
    ----------
    base_url: str
                Zenodo base url ended by /
    record_id: str
                Zenodo record id. Also answered from zenvar[-1]
                Folder path where your archive is available
    filename: list
                Filename to upload
    """
    for i in range(len(filename)):
        print("upload: " + filename[i])
        absfilename = os.path.join(folder, filename[i])
        r = requests.post(
                    base_url + "deposit/depositions/" + record_id + "/files",
                    data={"file": filename[i]},
                    params={"access_token": token},
                    headers={"content_type": "multipart/form-data"},
                    )
    return r


def creator_dict(df, i, contact_file=""):
    """
    Format Creator field to dict.
    Add orcid from contact file (geoflow format)
    Replace email with name
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Pandas dataframe from metadata entities (geoflow format)
    i: int
                Line of metadata entities
    contact_file: str 
                Filename containing contacts (geoflow format)
                
    
    e.g.:
    
    "creators":
    [{
    "orcid": "0000-0002-1825-0097",
    "affiliation": "Feline reasearch institute",
    "name": "Field, Gar"
    },
    {
    "orcid": "0000-0002-1825-0097",
    "affiliation": "Feline reasearch institute",
    "name": "Cat, Felix"
    }],
    
    """
    
    creator = df.iloc[i]["Creator"].split("_\n")[0].split(":")[1].split(",")
    if contact_file == "":
        print("No contact file, email will be displayed in Zenodo !")
        for cdi in range(len(creator)):
            cdict = {}
            cdict["name"] = creator[cdi]
            creator[cdi] = cdict
    
    else:
        print("Using contact file")
        contact_df = pd.read_csv(contact_file)
        for cdi in range(len(creator)):
            cdict = {}
            print("  Looking for " + str(creator[cdi]))
            if str(creator[cdi]) in str(contact_df["Identifier"].values):
                print("    Look for email {} in Contact file".format(str(creator[cdi])))
                filtered_contact = contact_df.loc[contact_df["Identifier"].str.contains(str(creator[cdi]))]
                if "orcid" in str(filtered_contact["Identifier"].values):
                    print("      Add orcid")
                    cdict["orcid"] = str(filtered_contact.iloc[0]["Identifier"].split("_\norcid:")[1])
                    
                if len(str(filtered_contact.iloc[0]["FirstName"])) > 0 and len(str(filtered_contact.iloc[0]["LastName"])) > 0:
                    print("      Add First and Last Name")
                    cdict["name"] = str(filtered_contact.iloc[0]["FirstName"]) + " " + str(filtered_contact.iloc[0]["LastName"])
                else:
                    print("      No First or Last Name, using email")
                    cdict["name"] = creator[cdi]
                    
                if len(str(filtered_contact.iloc[0]["OrganizationName"])) > 0:
                    print("      Add Affiliation")
                    cdict["affiliation"] = str(filtered_contact.iloc[0]["OrganizationName"])

            else:
                print("  -" + str(creator[cdi]) + " not in df, using email!")
                cdict["name"] = creator[cdi]
            
            creator[cdi] = cdict
    
    return creator


def zenedit(base_url, token, record_id):
    """
    Unlock published version to update metadata

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    """  
    r = requests.post(
        base_url + "deposit/depositions/" + record_id + "/actions/edit",
        params={"access_token": token},
    )
    return r

def zenmdt(base_url, token, record_id, df, i, contact_file=""):
    """
    Set and fill Metadata from Dataframe

    Parameters
    ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    df: class 'pandas.core.frame.DataFrame'
                Pandas dataframe from metadata entities (geoflow format)
    i: int
                Line of metadata entities
    contact_file: str 
                Filename containing contacts (geoflow format)
    """
    data = {
        #  "title": df.iloc[i]["Title"].split(':')[1],
        "metadata": {
            "title": df.iloc[i]["Title"].split(":")[1],
            "publication_date": df.iloc[i]["Date"].split("_\n")[0].split(":")[1],
            "description": df.iloc[i]["Description"].split("_\n")[0].split("abstract:")[1],  # .replace('\n', '<br />') +"<br />"+df.iloc[i]["Provenance"].split("_\n")[0].replace('\n', '<br />'),
            "access_right": "open",
            "notes": """<p></p><div class="ui message warning">This study was funded by the European Regional Development Fund (ERDF) within the programme Interreg V 2014-2020 through the project G2OI</div><br /><img src="https://github.com/IRDG2OI/geoflow-g2oi/raw/main/img/logos_partenaires.png?raw=True">""",
            "creators": creator_dict(df, i, contact_file),
            "keywords": df.iloc[i]["Subject"].split("_\n")[0].split(":")[1].split(","),
            "related_identifiers": [
                {
                    "identifier": "urn:{}".format(
                        df.iloc[i]["Identifier"].split("_\n")[0].split(":")[1]
                    ),
                    "relation": "isIdenticalTo",
                    "scheme": "urn",
                }
            ],
            "version": str(
                df.iloc[i]["Description"].split("edition:")[1].split("_\n")[0].replace('"', '')
            ),
            "language": df.iloc[i]["Language"],
            "license": "cc-by-4.0",
            "imprint_publisher": "Zenodo",
            "upload_type": df.iloc[i]["Type"],
            # "communities":[{'identifier':'uav'},
            #                {'identifier':'ecfunded'}],
            # "license": {
            #         "id": "CC-BY-4.0"
            #             },
            # "grants": [{"funder": {
            #   "doi": "10.13039/501100000780",
            #   "acronyms": [
            #     "EC"
            #   ],
            #   "name": "European Commission",
            #   "links": {
            #     "self": "https://zenodo.org/api/funders/10.13039/501100000780"
            #   }
            # }
            #              }]
        }
    }
    print(data)
    r = requests.put(
        base_url + "deposit/depositions/" + str(record_id),
        params={"access_token": token},
        data=json.dumps(data),
        headers=headers,
    )

    return r


def zenpublish(base_url, token, record_id):
    """
    Publish record !

  Parameters
  ----------
    base_url: str
                url of zenodo or zenodo sandbox without trailing '/'
    token: str
                zenodo access token
    record_id: str
                zenodo record id
    """
    r = requests.post(
        base_url + "deposit/depositions/" + str(record_id) + "/actions/publish",
        params={"access_token": token},
    )
    return r


### JSON config for Zenodo
def zenodo_json(fname, type, output, out_prefix):
    """
    JSON configuration for Zenodo with optionnal type parameter
    if type is not defined, regular zenodo will be use.
    if type='sandbox': Zenodo Sandbox will be use !

  Parameters
  ----------
    fname: str
                file name
    type: str
                regular zenodo or zenodo sandbox
    output: str
                output folder
    out_prefix: str
                name in front of file name, usually date and hour
    """
    if type == "sandbox":
        zenodo_url = "https://sandbox.zenodo.org/api"
    else:
        zenodo_url = "https://zenodo.org/api"

    zen_json = {
        "profile": {
            "id": "rawdata",
            "name": "rawdata",
            "project": "Publish rawdata with Geoflow",
            "organization": "IRD",
            "environment": {"file": ".env", "hide_env_vars": ["MOTDEPASSE"]},
            "logos": [
                "https://en.ird.fr/sites/ird_fr/files/2019-08/logo_IRD_2016_BLOC_UK_COUL.png"
            ],
            "mode": "entity",
        },
        "metadata": {
            "entities": [
                {
                    "handler": "csv",
                    "source": os.path.join(output, out_prefix) + "_zenodo-rawdata.csv",
                }
            ],
            "contacts": [
                {
                    "handler": "csv",
                    "source": "https://drive.ird.fr/s/EYS3qccyB28PrA9/download/geoflow_g2oi_contacts.csv",
                }
            ],
        },
        "software": [
            {
                "id": "my-zenodo",
                "type": "output",
                "software_type": "zenodo",
                "parameters": {
                    "url": zenodo_url,
                    "token": "{{ ZENODO_SANDBOX_TOKEN }}",
                    "logger": "DEBUG",
                },
                "properties": {"clean": {"run": False}},
            }
        ],
        "actions": [
            {
                "id": "zen4R-deposit-record",
                "options": {
                    "update_files": True,
                    "communities": "uav",
                    "depositWithFiles": True,
                    "publish": False,
                    "update_metadata": True,
                    "strategy": "newversion",
                    "deleteOldFiles": True,
                },
                "run": True,
            }
        ],
    }
    return zen_json

