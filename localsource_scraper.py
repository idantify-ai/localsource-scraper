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


def main():
    """

    """
    
    options = docopt(__doc__, version = CLI + ' ' + VERSION)
    if options['--input']:
        fname = options['--input']
        if isfile(fname):
            df = read_data_frame(fname)
            
        else:
            print('File not found: ', fname, ' ¯\_(ツ)_/¯', sep='')
            exit(FAILURE)        

  
if __name__ == "__main__":
    main()
