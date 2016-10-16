# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(SPAN(SPAN('True', _class='main_logo_true'), SPAN('Review', _class='main_logo_review'), _class='navbar-brand'),
                  _href=URL('true_review', 'default', 'index'))
response.title = 'TrueReview'
response.subtitle = 'Open, truthful post-publication review of scientific papers.'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Luca de Alfaro, Marco Faella, and contributors'
response.meta.description = 'Open, truthful post-publication review of scientific papers.'
response.meta.keywords = 'paper review, open publishing'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu = [
        ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
