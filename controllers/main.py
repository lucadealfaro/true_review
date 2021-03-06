# -*- coding: utf-8 -*-

# We are updating this file to use javascript.
# from google.appengine.api import taskqueue
import json
import review_utils

def dbupdate():
    return "ok"

def set_timezone():
    """Ajax call to set the timezone information for the session."""
    tz_name = request.vars.name
    # Validates the name.
    from pytz import all_timezones_set
    if tz_name in all_timezones_set:
        session.user_timezone = tz_name
        # If the user is logged in, sets also the timezone for the user.
        # Otherwise, it can happen that a user expires a cookie, then click on edit.
        # When the user is presented the edit page, the translation is done according to UTC,
        # but when the user is done editing, due to autodetection, the user is then in
        # it's own time zone, and the dates of an assignment change.
        # This really happened.
        if auth.user is not None:
            db.auth_user[auth.user.id] = dict(user_timezone = tz_name)
        logger.info("Set timezone to: %r" % tz_name)
    else:
        logger.warning("Invalid timezone received: %r" % tz_name)


def index():
    """ Serves the main page."""
    # Displays list of topics.
    q = db.topic
    links=[]
    links.append(dict(header='',
                      body=lambda r:
                          A('Edit', _href=URL('main', 'edit_topic', args=[r.id]))
                             if can_edit_topic(r.id) else None
                      ))
    links.append(dict(header='',
                      body=lambda r:
                           A('Delete', _href=URL('main', 'delete_topic', args=[r.id]))
                             if can_delete_topic(r.id) else None
                      ))
    grid = SQLFORM.grid(q,
        csv=False, details=False,
        links=links,
        create=False,
        editable=False,
        deletable=False,
        maxtextlength=48,
    )
    add_button = A(icon_add, 'Add topic', _class='btn btn-success',
                    _href=URL('main', 'create_topic')) if can_create_topic() else None
    return dict(grid=grid, add_button=add_button)




@auth.requires_login()
def edit_topic():
    """Allows editing of a topic.  The parameter is the topic id."""
    topic_id = request.args(0)
    if not can_edit_topic(topic_id):
        session.flash = T('You do not have the permission to edit this topic')
        redirect(URL('main', 'index'))
    topic = db.topic(topic_id)
    form = SQLFORM(db.topic, record=topic)
    # The "or <emptystring>" part fixes a bug that showed the datastore key in the form
    # when the description itself is empty.
    form.vars.description = text_store_read(topic.description) or ""

    if form.validate():
        topic.update_record(
            name=form.vars.name,
        )
        text_store_write(form.vars.description, key=topic.description)
        session.flash = T('The topic has been modified')
        redirect(URL('main', 'index'))
    return dict(form=form)







def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


