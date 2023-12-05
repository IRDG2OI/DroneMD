library(uasimg)
library(pagedown)
library(rmarkdown)

# datadir <- "/home/sylvain/DATA/TERRE_SAINTE" ### WITHOUT TRAILING /
datadir <- commandArgs(trailingOnly = TRUE)
print(datadir)
sessdir <- "UAV" #### PATTERN CONTAINING DATA TO BE PROCESSED
origfolder <- getwd()

for (i in list.dirs(datadir , full.names = FALSE , recursive = TRUE)){
  inputdir <- file.path(datadir, i)
  if (grepl(sessdir, inputdir) == TRUE) {
    print(paste("processing:", inputdir))
    setwd(inputdir)
    outputdir = file.path(inputdir, "METADATA")
    if (file.exists(outputdir)){
      print("METADATA folder available")
    } else {
      dir.create(file.path(outputdir))
    }

    flt1_info <- 
      uas_info(
        file.path(inputdir, "DCIM"), 
        fp = TRUE,
        # metadata = file.path( inputdir , "METADATA/metadata.txt"),
        cache = TRUE,
        update_cache = TRUE
        )

    flts_sum <- uas_report(
      flt1_info,
      thumbnails = TRUE,
      # png_map = TRUE,
      # attachments = "mcp_kml",
      report_title = paste(i, "Flight Summary"),
      # report_rmd = system.file("report/uas_report_metrics.Rmd", package="uasimg"),
      report_rmd = "/home/sylvain/DroneMDT/uas_report_metrics.Rmd",
      output_dir = outputdir,
      overwrite_html = TRUE
    )
    
    # output_dir = "/home/sylvain/Documents/IRD/DATA/uav_2022_09_19_aldabra-arm01_Mavic2Pro_1/METADATA"
    # fname = "Report_2022-10-19_18-17-02_202JPEGs.html"
    # fn = "/home/sylvain/Documents/IRD/DATA/uav_2022_09_19_aldabra-arm01_Mavic2Pro_1/METADATA/Report_2022-10-19_18-17-02_202JPEGs.html"
    #html_to_pdf(dir = output_dir)
    # chrome_print(fn, format=c("pdf"))
    for (i in list.files(outputdir)) 
      {
      if (endsWith(tolower(i), "html")) 
        {chrome_print(file.path(outputdir, i), format = c("pdf"))
      }
      }
    
    # uas_exp_shp(
    #   flt1_info,
    #   overwrite = TRUE,
    #   output_dir = outputdir,
    #   mcp = TRUE,
    #   ctr = TRUE, # Centroid
    #   fp = TRUE # Footprint
    # )

  setwd(origfolder)
  } # END SESSION SELECTION
} # END LOOP DATADIR 


# library(terra)
# library(exactextractr)
# library(sf)
# #v <- vect("2022-10-19_18-17-02_202JPEGs_fp.shp")
# v <- st_read(dsn="2022-10-19_18-17-02_202JPEGs_fp.shp")
# set.seed(1)
# library(sp)
# pts <- spsample(v, n=200, type="random")
# plot(pts, add=TRUE, col="red")
# library(rgeos)
# polys <- gBuffer(pts, width=50000, byid=TRUE)
# plot(polys, add=TRUE, border="red")
# #  gives something like USrelig.shp.
# library(rgeos)
# gO <- gOverlaps(v, polys, byid=c(TRUE, TRUE))
# dim(gO)
# #makes a logical matrix with TRUE where scot_BNG[i,] overlaps with polys[j].
# count_by_city <- apply(gO, 2, sum)



##### TOC ... TO BE DONE
# uas_toc(
#   html_reports = flt1_info,
#   output_dir = "/home/sylvain/Documents/IRD/DATA/uav_2022_09_19_aldabra-arm01_Mavic2Pro_1/METADATA"
# )
# 
# ## Create TOC, copying all the individual HTML files to one place
# uas_toc(flts_sum, 
#         output_dir = "/home/sylvain/Documents/IRD/DATA/uav_2022_09_19_aldabra-arm01_Mavic2Pro_1/METADATA",
#         toc_title = "Aldabra ARM01", 
# #        fltmap_base = TRUE,
#         gather_dir = ".", 
#         overwrite_toc = TRUE, 
#         open_toc = FALSE)
