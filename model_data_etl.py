import arcpy
import datetime
import logging
import os.path
import pickle


def get_start_date_from_db(mosaic_ds):
    try:
        sql_where = "Name IS NOT NULL AND DateObtained IS NOT NULL"
        # Sort most recent date first (descending) so we can just grab the first row then break out of the for loop!
        # Also, only request the Name and DateObtained fields as that is all we need and it should be faster.
        rows = arcpy.SearchCursor(mosaic_ds, sql_where, '', fields="Name; DateObtained", sort_fields="DateObtained D")
        the_date = None
        for r in rows:
            the_date = datetime.datetime.strptime(r.dateObtained, "%Y/%m/%d")
            break

        if the_date is None:
            the_date = datetime.datetime.strptime("2020/01/01", "%Y/%m/%d")

        return the_date

    except Exception, e:
        logging.error('### Error occurred in get_start_date_from_db ###, %s' % e)
        return None


def run_etl_for(which):
    arcpy.env.overwriteOutput = True
    print "Starting " + which
    variable = myConfig[which + 'Var']
    gdb = myConfig['gdb']
    mosaic_ds = gdb + myConfig[which + 'MDS']
    extract = myConfig['extract_Folder']
    name = "\\" + myConfig[which + 'Name']
    extension = myConfig[which + 'Extension']

    time_var = myConfig[which + 'TimeVar']
    time_dim = myConfig[which + 'TimeDim']

    the_start_date = get_start_date_from_db(mosaic_ds)
    while the_start_date.date() < datetime.date.today():
        the_start_date += datetime.timedelta(days=1)
        temp_date = the_start_date.strftime(myConfig[which + 'NameDateFormat'])
        in_net_cdf = extract + name + temp_date + extension
        if os.path.isfile(in_net_cdf):
            print (in_net_cdf + " exist")
            nc_fp = arcpy.NetCDFFileProperties(in_net_cdf)
            nc_dim = nc_fp.getDimensions()
            the_date = ''
            if len(time_var) + len(time_dim) > 0:
                the_date = nc_fp.getAttributeValue(time_var, time_dim)
                if the_date.find(" UTC") > 0:
                    the_date = the_date.split(' ')[0].replace('.', '-')
                elif the_date.find("Z") > 0:
                    print str(the_date)
                    the_date = the_date.split("T")[0]

            for dimension in nc_dim:
                top = nc_fp.getDimensionSize(dimension)
                for i in range(0, top):
                    if dimension == "time":
                        dimension_values = nc_fp.getDimensionValue(dimension, i)
                        if the_date == '':
                            the_date = str(dimension_values)

            rast = the_date.replace('-', '')
            arcpy.MakeNetCDFRasterLayer_md(in_net_cdf, variable, myConfig[which + 'Lon'], myConfig[which + 'Lat'], rast,
                                           "", "", "BY_VALUE", "CENTER")

            # convert the layer to a raster
            arcpy.CopyRaster_management(rast,
                                        mosaic_ds + rast, "", "",
                                        "-3,402823e+038", "NONE", "NONE",
                                        "", "NONE", "NONE")

            # Process: Add Rasters To Mosaic Dataset
            arcpy.AddRastersToMosaicDataset_management(mosaic_ds,
                                                       "Raster Dataset",
                                                       mosaic_ds + rast,
                                                       "UPDATE_CELL_SIZES",
                                                       "NO_BOUNDARY",
                                                       "NO_OVERVIEWS", "", "", "", "", "",
                                                       "SUBFOLDERS",
                                                       "ALLOW_DUPLICATES", "true", "true",
                                                       "NO_THUMBNAILS", "")

            the_name = myConfig[which + 'MDS'].replace('\\', '').replace('/', '') + rast

            expression = "Name= '" + the_name + "'"
            rows = arcpy.UpdateCursor(mosaic_ds, expression)  # Establish r/w access to data in the query expression.
            if the_date.find("-") < 0:
                year = the_date[0:4]
                month = the_date[4:6]
                day = the_date[6:8]
            else:
                year = the_date[0:4]
                month = the_date[5:7]
                day = the_date[8:10]

            dt_obj = year + "/" + month + "/" + day
            for r in rows:
                r.dateObtained = dt_obj  # here the value is being set in the proper field
                rows.updateRow(r)  # update the values

            del rows


# *********** VARIABLES *************

pkl_file = open('config.pkl', 'rb')
myConfig = pickle.load(pkl_file)
pkl_file.close()

# Run ETL for each type
# be sure to include the properties for the type in the configPickle.py
# and run C:\Python27\ArcGIS10.8\python configPickle.py to create the pkl

# imerg tested and working, just need to work out paths to real data
run_etl_for('imerg')
print "imerg ETL Complete"
#
# # gldas tested and working, just need to work out paths to real data
run_etl_for('gldas')  # fix date
print "gldas ETL Complete"
#
# # tempsrh tested and working, just need to work out paths to real data
run_etl_for('tempsrh')
print "tempsrh ETL Complete"

# # wind tested and working, just need to work out paths to real data
run_etl_for('wind')
print "wind ETL Complete"

# # airs tested and working, just need to work out paths to real data
run_etl_for('airs')
print "airs ETL Complete"

#
# run_etl_for('fldas')
# print "fldas ETL Complete"
