import pandas
# import os
import folium
# from folium import IFrame
# from IPython.display import display
# import base64
import datetime
import pdfkit

def converthms(secondes):
    """
    Convert date in second to hour, min, sec

    Parameters
    ----------
    secondes: int
                seconds
    """
    min, sec = divmod(secondes, 60)
    heure, min = divmod(min, 60)
    return "%d h %02d min %02d sec" % (heure, min, sec)

def define_map(df, sess_path, platform, model, title, nb_images, altitude, survey_area, start, end):
    """
    Generate a map with leaflet
    Some info from drone survey are needed ... 
    For an easy to do report, please watch enrich_drone_mdt in read_metadata.py
    
    Parameters
    ----------
    df: class 'pandas.core.frame.DataFrame'
                Dataframe with complete camera exifs    sess_path:
    platform: str
                Drone platform
    model: str
                Drone Model
    title: str
                Title of session
    nb_images: str
                Number of images in a string format
    altitude: str
                Flight height (not altitude)
    survey_area: str
                Area covered by survey
    start: str
                Start in '%Y:%m:%d %H:%M:%S'
    end: str
                End in '%Y:%m:%d %H:%M:%S'
    """
    ## Define map tiles provider
    attr = ('Tiles &copy Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
    tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png"

    ## Create map object:
    map=folium.Map(location=[df['GPSLatitude'].mean(),df['GPSLongitude'].mean()],zoom_start=17,tiles=tiles, attr=attr, width=800, height=600, left="10.0%")


    for lat, lon, Filename, thumbnail, date in zip(df['GPSLatitude'],df['GPSLongitude'],df['FileName'], df['ThumbnailImage'], df['DateTimeOriginal']):
        # encoded = base64.b64encode(open(Filename, 'rb').read()).decode()
        html = ('<table class="dataframe table table-striped table-hover table-condensed table-responsive"><thead><tr style="text-align: right;"><th>File</th><th>Lon,Lat</th><th>Date Hour</th></tr></thead><tbody><tr><th>' + Filename + '</th><td>' + str(lon) +',' + str(lat) + '</td><td>' + str(date) + '</td></tr></tbody></table>' + '<img src="data:image/jpg;base64,{}" width=400px height=266px>').format
        popup = folium.Popup(html(thumbnail.split('64:')[1]), max_width=400+20, max_height=266+80)
        marker = folium.Circle(radius=6, fill_color="white", fill_opacity=0.4, color="white", weight=1, location=[lat, lon], popup=popup)
        marker.add_to(map)
        
    style_to_insert = "<style>.leaflet-popup-content-wrapper, .leaflet-popup.tip {background-color: #ffffffb0 !important; }</style>"
    map.get_root().header.add_child(folium.Element(style_to_insert))

    title_html = '''
                <h3 align="center" style="font-size:200%"><b>Flight Summary</b></h3>
                '''
                #.format(title)
    map.get_root().html.add_child(folium.Element(title_html))
    
    dir = sess_path
    platform = platform + " " + model
    no_images = nb_images
    body_html = '''
                <div style="padding-left: 10%;">
                <h2 style="font-size:150%; color:MidnightBlue;"><b>{title}</b></h2>
                <p>
                <table>
                    <tbody>
                        <tr>
                            <th style="padding-left: 10px;">
                                Local dir: 
                            </th>
                            <td>
                                {dir}
                            </td>
                            <td>
                            </td>
                            <th style="padding-left: 10px;">
                                Median height: 
                            </th>
                            <td>
                                {altitude} meters
                            </td>                        
                        </tr>
                        <tr>
                            <th style="padding-left: 10px;">
                                Camera: 
                            </th>
                            <td>
                                {platform}
                            </td>
                            <td></td>
                            <th style="padding-left: 10px;">
                                Area: 
                            </th>
                            <td>
                                {survey_area} hectares
                            </td>                        
                        </tr>
                        <tr>
                            <th style="padding-left: 10px;">
                                Number of images: 
                            </th>
                            <td>
                                {nb_images}
                            </td>
                            <td></td>
                            <th style="padding-left: 10px;">
                                Start: 
                            </th>
                            <td>
                                {start}
                            </td>                        
                        </tr>
                        <tr>
                            <th style="padding-left: 10px;">
                                Flight duration
                            </th>
                            <td>
                                {duration}
                            </td>
                            <td></td>
                            <th style="padding-left: 10px;">
                                End: 
                            </th>
                            <td>
                                {end}
                            </td>                        
                        </tr>                                                                               
                    </tbody>
                </table>
                </p>
                <h2 style="font-size:150%; color:MidnightBlue;"><b>Images location</b></h2>
                </div>
                '''.format(title=title, dir=dir.split('/')[-1], altitude=altitude, platform = df.iloc[0]["Make"] + " " + df.iloc[0]["Model"], survey_area=survey_area, nb_images = nb_images, start=start, duration=converthms(((datetime.datetime.strptime(end,'%Y:%m:%d %H:%M:%S'))-(datetime.datetime.strptime(start,'%Y:%m:%d %H:%M:%S'))).seconds) , end=end)
                
    map.get_root().html.add_child(folium.Element(body_html))

    return map

def map_html(map, survey_info, df):
    """
    Convert map to html with base64 embeded pictures 
    
    Parameters
    ----------
    file_name: str
                html file
    survey_info: str
                Some info from drone survey like date meteo, flight height, camera pitch ... 
                For a complete report please watch enrich_drone_mdt in read_metadata.py
    df: class 'pandas.core.frame.DataFrame'
                Dataframe with complete camera exifs
    """
    # print(survey_info)
    map_html = map._repr_html_()
    body_html = map_html.split("&lt;body&gt;")[1].split("\n&lt;/html&gt")[0].replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    mapid = map.to_json().split(",")[1].split(":")[1].replace('"', '').split(" ")[1]

    head = '''<!DOCTYPE html>
    <html>
        <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <style>.leaflet-popup-content-wrapper, .leaflet-popup.tip {background-color: #ffffffb0 !important; }</style>
        
            <script>
                L_NO_TOUCH = false;
                L_DISABLE_3D = false;
            </script>
            
        <style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>
        <style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
        <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"/>
        <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css"/>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css"/>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css"/>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css"/>
        
                <meta name="viewport" content="width=device-width,
                    initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />

                    <style>
                        #map_id_to_replace {
                            position: relative;
                            width: 800.0px;
                            height: 600.0px;
                            left: 10.0%;
                            top: 0.0%;
                        }
                        .leaflet-container { font-size: 1rem; }
                    </style>  
            
    </head>
    '''.replace('map_id_to_replace', "map_" + mapid)

    body = '''
        <body>
            {}
    '''

    body_after = '''
    <p></p>
    <br>
    <div style="padding-left:5%;">
    <h2 style="font-size:150%; color:MidnightBlue;"><b>Images list</b></h2>
    {img_list}
    <p></p>
    <h2 style="font-size:150%; color:MidnightBlue;"><b>Survey informations</b></h2>
    {survey_info}
    </div>
    '''

    footer = '''
        <p></p>
        <br>
        <p style="color:#556B2F; font-style:italic; font-size:90%; text-align:left; padding-left:10%;">
        Script created by Sylvain POULAIN for G2OI</a>
        </p>
    </html>'''

    text = head + body.format(body_html) + body_after.format(img_list = df.to_html(index=False ,columns=['FileName', 'GPSLatitude', 'GPSLongitude', 'GPSAltitude','FlightPitchDegree',"ExposureTime","FNumber","ISOSpeedRatings", "DateTimeOriginal"], border=0), survey_info = survey_info.replace('\n', "<br>")) + footer
    
    return text

def convert_map_pdf(file_name):
    """
    Convert html to pdf
    
    Parameters
    ----------
    file_name: str
                html file
    """
    mapName = file_name
    # Convert Map from HTML to PDF, Delay to Allow Rendering
    options = {'javascript-delay': 500,
        'page-size': 'Letter',
        'margin-top': '0.0in',
        'margin-right': '0.0in',
        'margin-bottom': '0.0in',
        'margin-left': '0.0in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ]}
    pdf = pdfkit.from_file(mapName,  (mapName.split(".")[0] + '.pdf'), options=options)
    # pdffile = mapName + '.pdf'
    return pdf
