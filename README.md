# Model Date ETL for Lake Atitlan

[Currently in Development]

Extracts, translates, and loads the data from the Lake Atitlan water quality model run into an ArcGIS server 
where it can be served as wms to web applications.

## Installation Requirements

### Required

- Licensed ArcGIS Server
- ArcGIS Image Server extension
- python 2.7 (due to arcpy from ArcMap 10.8.1)
- Model data from Lake Atitlan

### Helpful

- ArcMap 10.8.1

## Setup

- Create an ArcGIS geodatabase (this is where ArcMap is handy to use.)
- Create Mosaic Datasets for each of the model data:
  - imerg
  - gldas
  - tempsrh 
  - wind 
  - airs 
    
- Add a new field to each of the datasets named dateObtained of type text
- Open config.Pickle.py and fill in the last six entries as described
- Open a console and run the configPickle.py file using python 2.7 (you can use the full path to the 
  python in your ArcMap directory.) This will output a new file called config.pkl that the application will use.
  
## Execute the application
Once setup is complete all you have to do is run model_data_etl.py using the full path to the
  python in your ArcMap directory.  Of course this is assuming that you have data in the extract directory.