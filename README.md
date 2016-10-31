# TrueReview

This repository contains the code of the TrueReview web2py app for post-publication peer review of scientific papers. 

For more information about the TrueReview project, please see the UC Santa Cruz School of Engineering Technical Report UCSC-SOE-16-13, available at https://www.soe.ucsc.edu/research/technical-reports/UCSC-SOE-16-13

## Project Members

- Luca de Alfaro (luca@dealfaro.com)
- Marco Faella (marfaella@gmail.com)
- Rakshit Agrawal (ragrawa1@ucsc.edu)
- Massimo Di Pierro (mdipierro@gmail.com)

# Installation

The application can be installed as a standard web2py app.  After installation, copy the file 
private/appconfig.example/ini into private/appconfig.ini, and edit the values as appropriate. 

The app is capable is running under three configurations:

- On Google Appengine, connected to a Google Cloud SQL database (as well as to the Google Datastore).
- As a web2py app connected to a SQL database.
- As a web2py app connected to a development sqlite database. 

Please see the setup in models/db.py for more information.

