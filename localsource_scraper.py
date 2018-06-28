# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------#
# Copyright 2018 Gabriele Valentini, Marek Borowiec. All rights reserved.      #
# Use of this source code is governed by a MIT license that can be found in    #
# the LICENSE file.                                                            #
#------------------------------------------------------------------------------#

"""
The ``localsource_scraper.py`` allows to add locally stored images to the
database of the idantify-ai application. 

Usage:
  localsource_scraper.py -h | --help
  localsource_scraper.py --version
  localsource_scraper.py -i <file> | --input=<file>

Options:
  -h --help                            Show help screen.
  --version                            Show localsource_scraper.py version.
  -i <file> --input=<file>             Add the images given in <file> to the DB.

Examples:
  localsource_scraper.py -i summary.txt

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/idantify-ai/localsource-scraper/issues
"""

from __future__ import print_function
from docopt     import docopt
from os.path    import isfile, splitext
from pandas     import read_table, read_csv, read_excel, read_json


VERSION         = '0.1'
CLI             = 'localsource_scraper.py'
SUCCESS         = 0
FAILURE         = 1
REQUIRED_FIELDS = ['FileName', 'Genus', 'Species']


def read_data_frame(fname):
    """
    Reads a ``pandas`` dataframe from a file (possible extensions are: txt, 
    json, csv, or excel), checks that the dataframe contains all required
    fields and return it.    
    """
    
    ftype = splitext(fname)[1]    
    if ftype == '.txt':
        df = read_table(fname)
    elif ftype == '.json':
        df = read_json(fname)
    elif ftype == '.csv':
        df = read_csv(fname)
    elif ftype == '.xls':
        df = read_excel(fname)
    else:
        print('File extension not recognized: ', ftype, ' ¯\_(ツ)_/¯', sep='')
        exit(FAILURE)

    for rf in REQUIRED_FIELDS:
        if rf not in df.columns:
            print('Missing columnn: ', rf, ' ¯\_(ツ)_/¯', sep='')
            exit(FAILURE)        
        
    return df


def scrape_data_frame(df):
    """
    For each row of the dataframe ``df``, queries the DB to retrieve the value
    of missing fields, inserts the image into the DB and copies it to the 
    appropriate directory according to ?.
    """
    
    db_ids          = ['domainId', 'kingdomId', 'phylumId', 'classId', 'orderId',
                       'familyId', 'genusId', 'imagesId']
    nimages_scraped = 0
    nimages         = df.shape[0]
    
    for i in range(nimages):
        filename = df.iloc[i]['FileName']
        genus    = df.iloc[i]['Genus']
        species  = df.iloc[i]['Species']

        # Query the DB to get other fields..

        # Insert image to the DB..

        # Copy image to the proper directory..
    
    return nimages_scraped


def getIDString(titleList):
    """
    C&P from bugguide-scraper: 

    creates the id string that will be used for the file directory and 
    the data base.

    titleList = ["eukarya", "animalia", "arthropoda", "class", "order", 
                 "family", "genus", "species"]

    """
	
    payload = {}
    headers = {}
    idDirectory = ""

    # Loop through the taxonomy categories in the titleList list in order
    # to run against API and
    # check for existing ids and create them if none exist
    for x in range(len(titleList)):
	url = os.environ['SpecifierApiUrl'] + titleList[x]
	if(titleList[x] == "domains"):
	    payload = {"name": "eukarya"}
	    headers = {'content-type': 'application/json'}
	else:
	    payload = {idList[x-1] : idIntList[x-1], "name" : taxonomyList[x]}
	    headers = {'content-type': 'application/json'}
		
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	response = json.loads(r.content)
	temp = response['id']
	idIntList[x] = temp
	#add id's to directory string for directory tree.
	idDirectory = idDirectory + "/" + str(response['id'])

    return idDirectory


def save_imgs(img, string):
    """
    Copy & pasted from BugGuide-scraper:

    creates directory and stores jpg file
    """
	
    #payload to be sent to retrieve the image id
    payload = { "speciesId": idIntList[7], "imageShotTypeId": 4,"url": img}
    headers = {'content-type': 'application/json'}

    #send payload
    r = requests.post(os.environ['SpecifierApiUrl'] + "images", data=json.dumps(payload), headers=headers)

    #parse response
    response = json.loads(r.content)

    #adds image id to string
    string += "/" + str(response['id'])

    #check if the path already exists and create if it doesn't
    if not os.path.exists(string):
	os.makedirs(os.path.dirname(string), exist_ok=True)
    #save image file in to the path
    urllib.request.urlretrieve(img, string+".jpg")

        

def main():
    """

    """
    
    options = docopt(__doc__, version = CLI + ' ' + VERSION)
    if options['--input']:
        fname = options['--input']
        if isfile(fname):
            df              = read_data_frame(fname)
            nimages         = df.shape[0]
            nimages_scraped = scrape_data_frame(df)
            
            if nimages_scraped > 0:
                print(str(nimages_scraped), '/', str(nimages),
                      ' images successfully added to the DB!     \(^-^)/', sep='')
                exit(SUCCESS)        
            else:
                print('Something went wrong. No images added to the DB!  ¯\_(ツ)_/¯', sep='')
                exit(FAILURE)                
        else:
            print('File not found: ', fname, ' ¯\_(ツ)_/¯', sep='')
            exit(FAILURE)        

  
if __name__ == "__main__":
    main()
