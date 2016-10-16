# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

# logging.
import logging
if request.env.web2py_runtime_gae:
    logger = logging
else:
    import sys
    import logging, sys
    FORMAT = "%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger(request.application)
    logger.setLevel(logging.INFO)
    logger.info("Not on gae")

from gluon import current
logging = logger
current.logger = logger
current.logging = logging

import os
is_gae = False
is_test_version = True # We are testing unless we are on the official gae version.
is_local_version = True # Local, not running on the cloud.
gae_version_id = os.environ.get("CURRENT_VERSION_ID")
gae_application_id = os.environ.get('APPLICATION_ID')
logger.info("Application id: %r Version id: %r" % (gae_application_id, gae_version_id))

if request.env.web2py_runtime_gae:
    is_gae = True
    is_test_version = gae_version_id.endswith('test')
    is_local_version = gae_application_id.startswith('dev~')

import logging
if request.env.web2py_runtime_gae:
    logger = logging
else:
    import sys
    FORMAT = "%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger(request.application)
    logger.setLevel(logging.INFO)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
    gdb = DAL(myconf.get('gdb.uri'),
             pool_size=myconf.get('gdb.pool_size'),
             migrate_enabled=myconf.get('gdb.migrate'),
             check_reserved=['all'])
else:
    if is_test_version or is_local_version:
        logger.info("Running locally")
        db = DAL('google:sql://true-review:true-review/true_review_test', migrate_enabled=True)
        ## connect to Google BigTable (optional 'google:datastore://namespace')
        gdb = DAL('google:datastore+ndb//test')
    else:
        db = DAL('google:sql://true-review:true-review/true_review_prod',
                 migrate_enabled=False, ) # Do NOT touch these migrate_enabled=False!!
        gdb = DAL('google:datastore+ndb//prod')
    ## store sessions and tickets there
    session.connect(request, response, db=gdb)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

# so that modules can use it
current.db = db
current.gdb = gdb

## These are the site admins.
site_admins = myconf.get('users.admins')
current.site_admins = site_admins

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################


from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()
# auth available also to modules.
current.auth = auth

# Long-lived logins and sessions.
auth.settings.expiration = 3600 * 24 * 365 # seconds

# Adds a timezone field to the auth table.
from pytz.gae import pytz
from plugin_timezone import tz_nice_detector_widget
my_tz_nice_detector_widget = lambda field, value : tz_nice_detector_widget(field, value, autodetect=True)

auth.settings.extra_fields['auth_user']= [
    Field('display_name', 'string', required=True), # Name to use in displaying reviewer.
    Field('user_timezone', 'string', widget=my_tz_nice_detector_widget),
    Field('affiliation', 'string'),
    Field('link', 'string', requires=IS_EMPTY_OR(IS_URL())),
    Field('blurb', 'text'),
]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## Don't bother with first and last names; they are not used uniformly in all cultures.
auth.settings.table_user.first_name.readable = auth.settings.table_user.first_name.writable = False
auth.settings.table_user.last_name.readable = auth.settings.table_user.last_name.writable = False
auth.settings.table_user.user_timezone.label = T('Time zone')
auth.settings.table_user.display_name.label = T('Display name')
## configure auth policy
auth.settings.registration_requires_verification = myconf.take('registration.verification')
auth.settings.registration_requires_approval = myconf.take('registration.approval')
auth.settings.reset_password_requires_verification = True

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

# Let's log the request.
if request.env.path_info.startswith('/user/'):
    logger.info("====> Request: %r %r" % (request.env.request_method, request.env.path_info))
else:
    logger.info("====> Request: %r %r %r %r" % (request.env.request_method, request.env.path_info, request.args, request.vars))
if auth.user_id is not None:
    logger.info("User: %r %r" % (auth.user.email, session.user_key))
else:
    logger.info("User: %r" % session.user_key)

# Is the user logged in?
# is_logged_in = auth.user_id is not None
