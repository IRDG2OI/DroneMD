import pandas as pd
import os
import datetime
import pycountry
from enriched_func import *
from meteo_helper import meteo
from exif_helper import *
from zip_helper import *
from raster_helper import *
from report import *
# import pdfkit
import geopandas as gpd
# pandas > 1.3.0

### Parse input folder
def filter_folder_name(input, session):
    """
    Filter input folder name to match regular folder name

    Parameters
    ----------
    input: str
                Input folder where sessions are stored
    session: str
                Session name including name of folder
    """
    sess = os.listdir(input)
    folder_name = []
    for i in range(len(sess)):
        if session in sess[i]:
            if '.zip' in sess[i]:
                pass
            else:
                folder_name.append(sess[i])
    return folder_name

def basic_geoflow_df(folder_name):
    """
    Generate a basic dataframe compatible with geoflow
    
    Parameters
    ----------
    folder_name: str
                Folder to parse
    """
    df = {}
    df = pd.DataFrame ({'Identifier': folder_name,
                #    'Lon': lon_list,
                #    'Desc': desc_list
                   })
    pd.set_option('max_colwidth', 105)

    ### 1. Title column
    df["Title"] = "title:" + df["Identifier"].str.capitalize()
    df["Title"] = (df["Title"].str.replace("_", " ")).str.replace("-", " ")
    ### 2. Description column
    desc = "No           \n\ndescription\n!"
    df["Description"] = "abstract:" + "'" + desc + "'"
    ### 3. Subject column
    project = "None"
    df["Subject"] = "project:" + project
    ### 4. Creator colum
    creator = "None"
    df["Creator"] = "creator:" + creator
    ### 5. Date
    date_content = "publication:" + datetime.datetime.now().strftime('%Y-%m-%d') + "_\n" + "edition:" + datetime.datetime.now().strftime('%Y-%m-%d')
    df["Date"] = date_content
    ### 6. Type
    df["Type"] = "dataset"
    ### 7. Language
    df["Language"] = "eng"
    ### 8. SpatialCoverage
    df["SpatialCoverage"] = ""
    ### 9. TemporalCoverage
    df["TemporalCoverage"] = str(df["Identifier"]).split('_')[1]
    ### 10. Relation
    df["Relation"] = "None"
    ### 11. Rights
    df["Rights"] = "useLimitation:Utilisation libre sous réserve de mentionner la source (a minima le nom du producteur) et la date de sa dernière mise à jour_\naccessConstraint:otherRestrictions_\nuseConstraint:intellectualPropertyRights_\notherConstraint:Le fournisseur n’est pas en mesure de garantir l’exactitude, la mise à jour, l’intégrité, l’exhaustivité des données et en particulier qu'elles sont exemptes d'erreurs ou d'imprécisions, notamment de localisation, d’identification ou de qualification. Aucune garantie quant à l'aptitude des données à un usage particulier n'est apportée par le fournisseur. Les utilisateurs utilisent les données sous leur responsabilité pleine et entière, sans recours possible contre le fournisseur dont la responsabilité ne saurait être engagée du fait d’un dommage résultant directement ou indirectement de l’utilisation de ces données. En particulier, il appartient aux utilisateurs d’apprécier, sous leur seule responsabilité : l'opportunité d'utiliser les données; la compatibilité des fichiers avec leurs systèmes informatiques; l’adéquation des données à leurs besoins; qu’ils disposent de la compétence suffisante pour utiliser les données. Le fournisseur n’est en aucune façon responsable des éléments extérieurs aux données et notamment des outils d’analyse, matériels, logiciels, réseaux..., utilisés pour consulter et/ou traiter les données. L’utilisateur veille à vérifier que l’actualité des informations mises à disposition est compatible avec l’usage qu’il en fait."
    ### 12. Provenance
    df["Provenance"] = "None"
    ### 13. Format
    format = "image/jpg"
    df["Format"] = "resource:" + format
    ### 14. Data column
    df["Data"] = "None"
    # df["Data"] = "source:" + df.id + "@" + input + os.sep + df.id + "_\n" + "uploadZip:true"
    # make sure indexes pair with number of rows
    # df = df.reset_index()
    return df

### Check global metadata and parse it if exists.
def global_mdt(input, md_file):
    """
    Parse global metadata.txt file

    Parameters
    ----------
    input: str
                Input folder
    md_file: str
                Name of metadata file to parse
    """
    if md_file in os.listdir(input):
        md_glob_path = os.path.join(input, md_file)
        mdt_df_glob = {}
        mdt_df_glob = mdt(md_glob_path)
        print("INFO: Global `metadata.txt` found !")
    else:
        mdt_df_glob = {}
        print("WARN: No global `metadata.txt` in {} to parse".format(input))
    return mdt_df_glob


def tree_sort_by_name(path=os.getcwd(), indent=0):
    """
    Generate folder list in tree style

    Parameters
    ----------
    path: str
                path to extract
    indent: int
                value to indent, default 0
    """
    print('|' + indent*'----' + ' ' + '└─ ', path.split('/')[-1])
    treed = '│' + indent*'----' + '  ' + '└─ ' +  path.split('/')[-1]
    for file in sorted(os.listdir(path)):
        if os.path.isdir(os.path.join(path, file)):
            treed = treed + "\n" + tree_sort_by_name(os.path.join(path, file), indent+2)
        ### To print files as well
        # else:
            # print('  ' + indent*' ' + '    ' + '──', file)
            # treed = treed + "\n" + '  ' + indent*' ' + '    ' + '──', file
    return treed

def enrich_drone_mdt(input, df, md_file, mdt_df_glob):
    """
    Main function of DroneMD:
    - Parse global and local metadata.txt file.
    - Enrich basic geoflow dataframe with complete set of metadata including data field
    - Generate report in html and pdf with base64 thumbnails

    Parameters
    ----------
    input: str
                Input folder
    df: class 'pandas.core.frame.DataFrame'
                Metadata entities (geoflow format)
    md_file: str
                Name of local metadata file to parse
    mdt_df_glob: str
                name of global metadata file to parse
    """
    for i in range(len(df)):
        sess_path = os.path.join(input, df.iloc[i]['Identifier'])
        ### Reading METADATA folder
        ### Check and create METADATA Directory if it not exists
        mdt_dir = os.path.join(sess_path, 'METADATA')
        if os.path.exists(mdt_dir):
            if md_file in os.listdir(mdt_dir):
                md_file_path = os.path.join(mdt_dir, md_file)
                mdt_df_sess = {}
                mdt_df_sess = mdt(md_file_path)
                print("INFO: `metadata.txt` found for {} !".format(df.iloc[i]['Identifier']))
            else:
                mdt_df_sess = {}
                print("WARN: No metadata.txt in {} to parse".format(mdt_dir))
        else:
            print("INFO: Create METADATA folder, no metadata.txt in {} to parse")
            os.mkdir(mdt_dir)
            mdt_df_sess = {}

        ### Reading GPS folder
        ### Check and create GPS Directory if it not exists
        gps_dir = os.path.join(sess_path, 'GPS')
        if os.path.exists(gps_dir):
            print("INFO: GPS Folder found")
        else:
            print("INFO: Create GPS folder")
            os.mkdir(gps_dir)
        
        print("Format id to obtain date, country name, optionnal place, and platform")
        id_split = df.iloc[i]["Identifier"].split("_")
        id_date = id_split[0]
        id_loc = id_split[1]
        if "-" in id_loc:
            countrycode = id_loc.split("-")[0]
            country = pycountry.countries.get(alpha_3 = countrycode).name
            place = id_loc.split("-")[1:]
            place = ' '.join(place).capitalize()
        else:
            country = id_loc
            place = " "
        
        # print(countrycode + " " + country + " " + place)
        
        platform = id_split[2].split("-")[0]
        model = id_split[2].split("-")[1]
        flight = id_split[-1]
        # print(platform)
        
        print('####################\n### 2. Enrich Title\n ####################')
        title = ""
        title = str(enrich_val("title", mdt_df_glob, mdt_df_sess))
        print(title)
        print("format field")
        title = title.format(date = str(id_date), country = country, place = place, platform = platform) + ' - ' + str(model) + '_' + str(flight)             
        df.iloc[i, df.columns.get_loc("Title")] = "title:" + title #+ df.iloc[i]["Identifier"]
        
        print('####################\n### 8. Enrich Language\n ####################')
        language = ""
        language = enrich_val("language", mdt_df_glob, mdt_df_sess)
        df.iloc[i, df.columns.get_loc("Language")] = language
        
        print('####################\n### 4. Enrich Subject\n ####################')
        # df.iloc[i, df.columns.get_loc('Subject')].split(':')[1] == 'None'
        subject = ""
        subject_list = []
        subject_list.append(enrich_val('theme', mdt_df_glob, mdt_df_sess))
        # subject_list.append(enrich_val('taxonomy', mdt_df_glob, mdt_df_sess))
        subject_list.append("project:" + enrich_val('project', mdt_df_glob, mdt_df_sess))
        subject = enrich_field(subject, subject_list)
        df.iloc[i, df.columns.get_loc('Subject')] = subject
        
        print('####################\n### 5. Enrich Creator\n ####################')
        creator = ""
        creator_list = []
        for cl in (['author', 'publisher', 'owner', 'pointOfContact', 'processor']):
            creator_list.append("{}:".format(cl) + enrich_val(cl, mdt_df_glob, mdt_df_sess))
        creator = enrich_field(creator, creator_list)
        df.iloc[i, df.columns.get_loc('Creator')] = creator
        
        print('####################\n### 11. Enrich Relation\n ####################')
        relation = ""
        relation_list = []
        # for rl in (['thumbnail', 'parent', 'http']):
        for rl in (['thumbnail', 'http']):    
            relation_list.append("{}:".format(rl) + enrich_val(rl, mdt_df_glob, mdt_df_sess))
        relation = enrich_field(relation, relation_list)
        df.iloc[i, df.columns.get_loc('Relation')] = relation
        
        print('####################\n### Reading DCIM folder\n ####################')
        image_list = getImagelist(os.path.join(sess_path, 'DCIM'))
        nb_images = nbImages(image_list)
        print("Extract image coordinates and thumbnails: it could takes some time !")
        ic = images_coords(image_list)
        # print(ic)
        print(sess_path)
        
        print("Generate image with a set of images")
        series_to_img(image_list, sess_path)
        # print("Write thumbnail to hmtl")
        # for im in range(len(ic)):
        #     tbhtml = display_image(ic.iloc[im]['Thumbnail'])
        #     with open('/tmp/test.html', 'a') as dhtml:
        #         dhtml.write(tbhtml)
        bb = bbox(ic)
        # print('####################\n### 9. Enrich SpatialCoverage\n####################')
        # df.iloc[i, df.columns.get_loc('SpatialCoverage')] = "SRID=4326;POLYGON((" + str(bb[0]) + " " + str(bb[1]) + "," + str(bb[0]) + " " + str(bb[3]) + "," + str(bb[2]) + " " + str(bb[3]) + "," +  str(bb[2]) + " " + str(bb[1]) + "))"
        lon = str(center_bbox(bb)[0])
        lat = str(center_bbox(bb)[1])
        
        print('####################\n### 10. Enrich TemporalCoverage\n ####################')
        # print(datebe(ic))
        begin = datebe(ic)[0].replace(":", "-")
        # begin = datebe(ic)[0].split(" ")[0].replace(":", "-") + " " + datebe(ic)[0].split(" ")[1]
        end = datebe(ic)[1].replace(":", "-")
        # end = datebe(ic)[1].split(" ")[0].replace(":", "-") + " " + datebe(ic)[1].split(" ")[1]
        if begin == end:
            df.iloc[i, df.columns.get_loc('TemporalCoverage')] = begin
        else:
            df.iloc[i, df.columns.get_loc('TemporalCoverage')] = begin + " - " + end
        
        print('####################\n### 00. Prepare Provenance (13) and Description (3) \n ####################')
        exif = str(common_tags(image_list)).replace(",", "\n").replace("{","").replace("}","").replace("'","")
        
        print('####################\nFetching open-meteo\n ####################')
        condition = meteo(lat, lon, begin, end, "best_match")
        alt = altimg(ic)
        ### Convert dataframe to geodataframe and export to GIS format
        print("Convert Dataframe to UTM")
        print(ic.keys())
        gdf = gpd.GeoDataFrame(ic, geometry = gpd.points_from_xy(ic['GPSLongitude'], ic['GPSLatitude']), crs = 'EPSG:4326')
        gdfutm = gdf.to_crs(gdf.estimate_utm_crs())
        geom_mdt = "SurveyMetadata.gpkg"
        # with open("/tmp/tb.jpg", "wb") as fh:
        #     fh.write(tags['JPEGThumbnail'])
        print("Compute convex hull")
        survey_polygon = gdfutm.unary_union.convex_hull
        survey_polygon_gdf = gpd.GeoDataFrame(pd.DataFrame({'Identifier':[i], 'polygon':[survey_polygon]}), geometry='polygon', crs = gdfutm.crs.srs)
        print("Export BBOX to GPKG")
        survey_polygon_gdf.to_file(os.path.join(gps_dir, geom_mdt), layer="emprise", driver="GPKG")
        print("Exporting geolocation files including thumbnails: it could take some time !")
        gdfutm.to_file(os.path.join(gps_dir, geom_mdt), layer="images", driver='GPKG', method="a")
        print("Exporting metadata.csv !")
        gdf.to_csv(os.path.join(mdt_dir, "metadata.csv"), quoting=1, quotechar='"', index=False)
        survey_area = round(survey_polygon.area/10000, 2)
        
        print('####################\n### 13. Enrich Provenance\n ####################')
        start = ic['DateTime'].min()
        end = ic['DateTime'].max()
        survey_info_minimal = "- Camera model and parameters:\n" + " " + str(exif) + "\n\n- Survey informations:\n" + " No Images: {}".format(str(nb_images) + "\n") + " Median height: {}".format(str(round(alt)))+" meters\n" + " Survey area: {}".format(str(survey_area))+" hectares\n" + " Survey from: " + start + " to: " + end
        survey_info = (survey_info_minimal + "\n\nUTM Coordinate system:\n" +
                                                        " " + gdfutm.crs.name + "\n" +
                                                        " " + gdfutm.crs.srs + "\n Description:\n" +
                                                        str(gdfutm.crs.area_of_use).replace("- ", "  ") +
                                                        "\n\n- Meteo:\n" + str(condition)
                                                        )
        df.iloc[i, df.columns.get_loc('Provenance')] = "statement:" + '"{}"'.format(survey_info)
        
        print('####################\n### 3. Enrich Description\n ####################')
        description = ""
        desc_list = []
        for dl in (['abstract', 'purpose', 'info', 'edition']):
            desc_list.append("{}:".format(dl) + '"{}"'.format(enrich_val(dl, mdt_df_glob, mdt_df_sess)))
        description = str(enrich_field(description, desc_list))
        
        treed = tree_sort_by_name(input + "/" + df.iloc[i]['Identifier'])
        description = description.format(date = str(id_date), country = country, place = place, platform = platform, no_images = str(nb_images), treed = treed, survey_stat = survey_info_minimal)
        description = description.replace("\n", "\n<br />").replace("<br />info:", "info:").replace("<br />purpose:", "purpose:").replace("<br />edition:", "edition:")
        
        df.iloc[i, df.columns.get_loc('Description')] = description
        
        print('####################\n### 14. Enrich Formats\n ####################')
        df.iloc[i, df.columns.get_loc('Format')] = df.iloc[i]['Format'] + "_\ndistribution:application/geopackage+sqlite3[GeoPackage]"
        
        print('####################\n### 15. Enrich data\n ####################')
        df.iloc[i, df.columns.get_loc('Data')] = "source:" + "SurveyMetadata.gpkg" + "@" + input + "/" + df.iloc[i]['Identifier'] + "/GPS/" + 'SurveyMetadata.gpkg' + "_\n" + "sourceType:gpkg_\nuploadSource:SurveyMetadata.gpkg_\nuploadType:gpkg_\nstore:" + df.iloc[i]['Identifier'] + "_\nlayer:emprise_\nlayername:"+ df.iloc[i]['Identifier'] + "-SurveyMetadata.gpkg" + "_\nstyle:generic_\nspatialRepresentationType:vector"
        
        print('####################\n### 16. Generate HTML and PDF Report\n ####################')
        print("Generate map")
        map = define_map(gdf, sess_path, platform, model, title, nb_images, str(round(alt)), survey_area, start, end)
        print("Generate html")
        map_to_html = map_html(map, survey_info, gdf)
        print("Save html to disk")
        html_file= os.path.join(mdt_dir,"Report_" + start.replace(":","-").replace(" ", "_") + "_" + str(nb_images) + "-JPEGs.html")
        with open(html_file, "w") as html_fn:
            html_fn.write(map_to_html)
        print("Convert html to pdf")
        convert_map_pdf(html_file)
        print("####################\n####     END    ####\n####################")


def mdt(md_file):
    """
    Return Metadata file parsing. Transpose dataframe to better search.
    
    Parameters
    ----------
    md_file: str
                metadata.txt file
    
    Metadata file
    Structure of Metadata file:
    abstract="My abstract description"
    #######
    e.g.: 
    # Load Metadata file:
    mdt(metadata_file)
    
    # Get Metadata info:
    mdt(md_file).info()
    
    # Write formated Metadata file to csv
    mdt(md_file).to_csv("/path/to/file.csv", index=False)
    """
    columns = ['parameter','value']
    metadata = pd.read_csv(md_file, sep="=", header=None, names=columns, on_bad_lines='skip')
                    #    ["parameter", "value"], usecols=["parameter", "value"],sep="=", skiprows=1)
                    # # "abstract" in metadata.parameter[0]
                    # # abstract = metadata['value'].where(metadata['parameter'] == "abstract")
                    # # metadata = metadata.transpose()
    metadata = metadata.set_index('parameter').T
    # if "abstract" in metadata.columns:
    #     # print(metadata["abstract"][0])
    #     print(metadata["abstract"].value)
    # else:
    #     pass
    return metadata

