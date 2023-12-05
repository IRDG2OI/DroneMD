import pandas as pd

def enrich_val(keyword, df_global, df_local):
    """
    Function to enrich metadata for Geoflow from metadata.txt file
    Usage:
    enrich_val('abstract', df_global, df_local, i)
    Where 'abstract' is a value to enrich in final pandas Dataframe
    It will return enriched metadata parsed from metadata.txt if available
    
    Parameters
    ----------
    keyword: str
                keyword available df_global or df_local
    df_global: class 'pandas.core.frame.DataFrame'
                global dataframe extracted from metadata.txt
    df_local: class 'pandas.core.frame.DataFrame'
                local dataframe extracted from metadata.txt
    """
    enriched = ""
    if keyword in df_global.keys():
        if "Series" in str(type(df_global.iloc[0][keyword])):
            enriched = df_global.iloc[0][keyword][0]
        else:
            enriched = df_global.iloc[0][keyword]
        print("INFO: Using glocal {}".format(keyword))
    else:
        print("WARN: No global {}".format(keyword))
        enriched = ''
    if keyword in df_local.keys():
        if "Series" in str(type(df_local.iloc[0][keyword])):
            enriched = df_local.iloc[0][keyword][0]
        else:
            enriched = df_local.iloc[0][keyword]
        print("INFO: Using local {}".format(keyword))
    else:
        if len(enriched) == 0:
            print("WARN: No {} to enrich".format(keyword))
    return enriched

def enrich_field(field, enrich_val_list):
    """
    Refactor fields value to be in geoflow entities format

    Parameters
    ----------
    field: str
                keyword available df_global or df_local
    enrich_val_list: list
                values to reformat
    """
    field = ""
    for d in range(len(enrich_val_list)):
        field = field + enrich_val_list[d] + '_\n'
        # if ":" in enrich_val[d]:
        #     if len(enrich_val_list[d].split(':')[1])>0:
        #         field = field + enrich_val_list[d] + '_\n'
        # else:
        #     if len(enrich_val_list[d])>0:
        #         field = field + enrich_val_list[d] + '_\n'
    field = field[:-2]
    return field