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
  For help using this tool open an issue on the Github repository:
  https://github.com/idantify-ai/localsource-scraper/issues
"""

from __future__ import print_function
from docopt     import docopt
from os         import environ, makedirs
from os.path    import isfile, isdir, splitext, exists, join
from pandas     import read_table, read_csv, read_excel, read_json
from shutil     import copyfile
from json       import loads, dumps
from requests   import post

VERSION         = '0.1'
CLI             = 'localsource_scraper.py'
SUCCESS         = 0
FAILURE         = 1
REQUIRED_FIELDS = ['FileName', 'Genus', 'Species', 'ShotType']


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
    appropriate directory.
    """
    
    nimages_scraped = 0
    nimages_fail    = 0
    nimages         = df.shape[0]

    try:
        # api_url = environ['SpecifierApiUrl']
        api_url = "http://tclasol-jkj3dh2.dhcp.asu.edu:81/api/"
    except KeyError:
        print('Environment variable <SpecifierApiUrl> not defined!   ¯\_(ツ)_/¯', sep='')
        exit(FAILURE)

    try:
        headers   = {'content-type': 'application/json'}
        r         = requests.get(api_url + "image-shot-types", headers = headers)
        if r.status_code != 200:
            raise ConnectionError
    except:
        print('The Specifier Api can not be reached!   ¯\_(ツ)_/¯', sep='')
        exit(FAILURE)        

    try:
        #db_dir = environ['SpecifierImagesDirectory']
        db_dir = ""
        if not isdir(db_dir):
            print('Directory ', db_dir, ' not found!   ¯\_(ツ)_/¯', sep='')
        exit(FAILURE)                    
    except KeyError:
        print('Environment variable <SpecifierImagesDirectory> not defined!   ¯\_(ツ)_/¯',
              sep='')
        exit(FAILURE)        


#check if you can write to db_dir..
        
    for i in range(nimages):
        filename = df.iloc[i]['FileName']
        genus    = df.iloc[i]['Genus']
        species  = df.iloc[i]['Species']
        shottype = df.iloc[i]['ShotType']

        if isfile(filename):
            rval   = insert_image_to_db(api_url, db_dir, genus, species, shottype, filename)
            dpath  = rval[0]
            dfname = rval[1]
            status = 'added'
        else:
            status = 'fail'

        if status == 'added':            
            if not exists(dpath):
                makedirs(dpath, exist_ok = True)
            copyfile(filename, join(dpath, dfname))
            nimages_scraped = nimages_scraped + 1
        elif status == 'fail':
            nimages_fail    = nimages_fail + 1

        print('Scraping image ', str(i + 1), '/', str(nimages), ': ',
              str(nimages_scraped), ' added, ',
              str(nimages_fail), ' failed to add.', sep = '', endl = '\r')
    
    return nimages_scraped


def insert_image_to_db(api_url, db_dir, genus, species, shottype, filename):
    """
    Add an image to the DB using the API. 

    returns:
        filename, the file name including destination path where to copy the
                  newly added image
    """

    # Find domain id
    headers   = {'content-type': 'application/json'}
    payload   = {"name": "eukarya"}
    r         = post(api_url + "domains", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    domainId  = response['id']

    # Find kingdom id 
    payload   = {"domainId": domainId, "name": "animalia"}
    r         = post(api_url + "kingdoms", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    kingdomId = response['id']

    # Find phylum id
    payload   = {"kingdomId": kingdomId, "name": "arthropoda"}
    r         = post(api_url + "phyla", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    phylumId  = response['id']

    # Find class id
    payload   = {"phylumId": phylumId, "name": "insecta"}
    r         = post(api_url + "classes", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    classId   = response['id']

    # Find order id
    payload   = {"classId": classId, "name": "hymenoptera"}
    r         = post(api_url + "orders", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    orderId   = response['id']

    # Find family id
    payload   = {"orderId": orderId, "name": "formicidae"}
    r         = post(api_url + "families", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    familyId  = response['id']

    # Find genus id
    payload   = {"familyId": familyId, "name": genus.lower()}
    r         = post(api_url + "genera", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    genusId   = response['id']

    # Find species id
    payload   = {"genusId": genusId, "name": species.lower()}
    r         = post(api_url + "species", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    speciesId = response['id']

    # Find species id
    payload   = {"genusId": genusId, "name": species.lower()}
    r         = post(api_url + "species", data=dumps(payload), headers = headers)
    response  = loads(r.content)
    speciesId = response['id']

    # Find shot type id
    #r         = requests.get(api_url + "image-shot-types", headers = headers)
    #shottypes = loads(r.content)
    #sttypeId  = [st for st in shottypes if st["sourceKey"] == shottype][0]["id"]
    #if sttypeId < 1 or sttypeId > 4: 
    #    sttypeId = 4

    # Add image to the db and get its id
    payload   = {"speciesId": speciesId, "imageShotTypeId": sttypeId, "url": filename}
    r         = requests.post(api_url + "images", data=json.dumps(payload), headers = headers)
    response  = json.loads(r.content)
    imageId   = response['id']

    # Create destination path
    dest_path  = join(str(db_dir), str(domainId), str(kingdomId), str(phylumId), str(classId), str(orderId), str(familyId), str(genusId), str(speciesId), str(shottype))
    dest_fname = str(imageId) + splitext(filename)[1]

    return [dest_path, dest_fname]
           

def main():
    """
    Main entry point for the ``localsource-scraper.py`` script.
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
