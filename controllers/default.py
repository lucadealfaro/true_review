# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import json
import review_utils

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

# TODO: use vue.js
def index():
    """ Serves the main page."""
    # Displays list of topics.
    """ Serves the main page."""
    # Displays list of topics.
    q = (db.topic.is_active == True)
    links=[]
    db.topic.name.label = T('Topic')
    links.append(dict(header='',
                      body=lambda r:
                          A(icon_details, 'Details', _href=URL('default', 'view_topic', args=[r.id]))
                      ))
    links.append(dict(header='',
                      body=lambda r:
                          A(icon_edit, 'Edit', _href=URL('default', 'edit_topic', args=[r.id]))
                             if can_edit_topic(r.id) else None
                      ))
    links.append(dict(header='',
                      body=lambda r:
                           A(icon_delete, 'Delete', _href=URL('default', 'delete_topic', args=[r.id]))
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
                    _href=URL('default', 'create_topic')) if can_create_topic() else ''
    return dict(grid=grid, add_button=add_button)


def topic_index():
    """Displays papers and reviewers in a topic. Already in vue.js"""
    topic_id = request.args(0)
    topic = db.topic(topic_id)
    if topic is None:
        session.flash = T('No such topic')
        redirect(URL('default', 'index'))
    return dict(
        topic=topic,
    )


def view_topic():
    """Views the details of a topic. Work in progress."""
    topic_id = request.args(0)
    topic = db.topic(topic_id)
    if topic is None:
        session.flash = T('No such topic')
        redirect(URL('default', 'index'))
    button_list = []
    if can_edit_topic(topic_id):
        button_list.append(
            A(icon_edit, 'Edit', _class='btn btn-primary',
              _href=URL('default', 'edit_topic', args=[topic_id])))
    if can_edit_topic(topic_id):
        button_list.append(
            A(icon_delete, 'Delete', _class='btn btn-danger',
              _href=URL('default', 'delete_topic', args=[topic_id])))
    return dict(topic=topic,
                description=text_store_read(topic.description),
                button_list=button_list,
                )


# TODO: use vue.js
@auth.requires_login()
def delete_topic():
    """Deletion of a topic.  This simply makes a topic not active for the main list
    of topics, but it does not otherwise affect the system."""
    topic_id = request.args(0)
    if not can_delete_topic(topic_id):
        session.flash = T('You do not have the permission to delete a topic')
        redirect(URL('default', 'index'))
    # TODO: improve code below.  This should be done in the index via a modal form.
    topic = db.topic(topic_id)
    if topic is None:
        session.flash = T('No such topic')
        redirect(URL('default', 'index'))
    is_empty = is_topic_empty(topic_id)
    form = FORM.confirm('Delete' if is_empty else 'Hide',
                        {'Cancel': URL('default', 'index')})
    form.element(_type='submit')['_class']='btn btn-danger'
    if form.accepted:
        if is_empty:
            db(db.topic.id == topic_id).delete()
            session.flash = T('The topic has been deleted')
        else:
            topic.update_record(is_active=False)
            session.flash = T('The topic has been hidden')
        redirect(URL('default', 'index'))
    return dict(topic=topic,
                description=text_store_read(topic.description),
                form=form,
                is_empty=is_empty)


# TODO: use vue.js
@auth.requires_login()
def edit_topic():
    """Allows editing of a topic.  The parameter is the topic id."""
    topic_id = request.args(0)
    if not can_edit_topic(topic_id):
        session.flash = T('You do not have the permission to edit this topic')
        redirect(URL('default', 'index'))
    topic = db.topic(topic_id)
    form = SQLFORM(db.topic, record=topic)
    form.add_button('Cancel', URL('default', 'index'))
    # The "or <emptystring>" part fixes a bug that showed the datastore key in the form
    # when the description itself is empty.
    form.vars.description = text_store_read(topic.description) or ""
    if form.validate():
        topic.update_record(
            name=form.vars.name,
        )
        text_store_write(form.vars.description, key=topic.description)
        session.flash = T('The topic has been updated')
        redirect(URL('default', 'index'))
    return dict(form=form)


# TODO: use vue.js
@auth.requires_login()
def create_topic():
    if not can_create_topic():
        session.flash = T('You do not have the permission to create a topic')
        redirect(URL('default', 'index'))
    form = SQLFORM(db.topic)
    if form.validate():
        topic_id = db.topic.insert(name=form.vars.name,
                                   description=text_store_write(form.vars.description))
        add_admin_to_topic(auth.user.email, topic_id)
        session.flash = T('The topic has been created')
        redirect(URL('default', 'index'))
    return dict(form=form)


# TODO: use vue.js
@auth.requires_login()
def edit_paper():
    """This is a temporary page, so that we can add papers to
    a series of topics.
    In reality we need a more sophisticated method for adding or editing
    papers, and for importing from ArXiV.
    args(0) is the topic; one submits papers to specific topics for rating.
    If args(1) is specified, it is the id of the paper to edit.
    If the variable 'topic' is specified, it is taken to be the topic id
    of a paper to which the paper belongs by default.

    Note that I am assuming here that anyone can edit a paper.
    """
    topic_id = int(request.args(0))
    paper_id = request.args(1)
    user_id = auth.user
    paper = db(db.paper.paper_id == paper_id).select(orderby=~db.paper.start_date).first()
    is_create = paper is None
    # Checks permissions.
    if is_create:
        # Can the user submit?
        if not can_add_paper(topic_id):
            session.message = T('You cannot submit papers to this topic.')
            redirect(URL('default', 'view_topic', args=[topic_id]))
    else:
        # Can the user edit the paper?
        # ---qui---

    form = SQLFORM.factory(
        Field('title', default=None if is_create else paper.title),
        Field('authors', 'list:string', default=None if is_create else paper.authors),
        Field('abstract', 'text', default=None if is_create else text_store_read(paper.abstract)),
        Field('paper_url', default=None if is_create else paper.paper_url, requires=IS_EMPTY_OR(IS_URL())),
        Field('primary_topic', 'reference topic', default=default_topic_id,
              requires=IS_IN_DB(db(), 'topic.id', '%(name)s')),
        Field('secondary_topics'),
    )
    def validate_paper_edit_form(form):
        # Checks the names of the secondary topics.
        primary_topic_id = form.vars.primary_topic
        secondary_topic_ids = []
        if form.vars.secondary_topics is not None:
            secondary_topics_raw_names = form.vars.secondary_topics.split(';')
            for n in secondary_topics_raw_names:
                nn = n.strip()
                if nn != '':
                    t = db(db.topic.name == nn).select().first()
                    if t is None:
                        form.errors.secondary_topics = T('The topic %r does not exist') % nn
                        return form
                    if not can_add_paper(t.id):
                        form.errors.secondary_topics = T('You do not have the permission to include topic %r') % nn
                        return form
                    secondary_topic_ids.append(t.id)
            form.vars.secondary_topic_ids = list(set(secondary_topic_ids) - {primary_topic_id})
        return form

    if form.process(onvalidation=validate_paper_edit_form).accepted:
        # We have to carry out the requests in the form.
        now = datetime.utcnow()
        if is_create:
            # We have to come up with a new random id.
            random_paper_id = review_utils.get_random_id()
            abstract_id = text_store_write(form.vars.abstract)
            # We write the paper.
            db_paper_id = db.paper.insert(paper_id=random_paper_id,
                                          title=form.vars.title,
                                          authors=form.vars.authors,
                                          abstract=abstract_id,
                                          paper_url=form.vars.file,
                                          primary_topic=form.vars.primary_topic,
                                          start_date=datetime.utcnow(),
                                          end_date=None
                                          )
            # Adds a permission line.
            db.paper_role.insert(paper_id=random_paper_id,
                                 can_edit=True,
                                 can_view=True,
                                 )
            session.flash = T('The paper has been added')
        else:
            random_paper_id = paper.paper_id
            abstract_id = paper.abstract
            if form.vars.abstract != text_store_read(paper.abstract):
                abstract_id = text_store_write(form.vars.abstract)
            session.flash = T('The paper has been updated')
            # Closes the validity period of the previous instance of this paper.
            paper.update_record(end_date=now)
            # We write the paper.
            db_paper_id = db.paper.insert(paper_id=random_paper_id,
                                          title=form.vars.title,
                                          authors=form.vars.authors,
                                          abstract=abstract_id,
                                          file=form.vars.file,
                                          primary_topic=form.vars.primary_topic,
                                          start_date=datetime.utcnow(),
                                          end_date=None
                                          )

        # Then, we take care of the topics.
        new_topics = set({form.vars.primary_topic}) | set(form.vars.secondary_topic_ids)
        logger.info("new topics: %r" % new_topics)
        for top in new_topics:
            db.paper_in_topic.insert(
                paper = db_paper_id,
                topic = top,
                is_primary = (top == form.vars.primary_topic),
            )
        if request.vars.topic is not None:
            redirect(URL('default', 'topic_index', args=[request.vars.topic]))
        else:
            redirect(URL('default', 'index'))
    return dict(form=form, is_create=is_create)


def view_paper():
    """Views a paper, including the details of the paper, and all the reviews.
    Work in progress.
     Arguments:
         - paper_id
    """
    return dict(
        signed_url=URL('api', 'paper_do', user_signature=True),
        unsigned_url=URL('api')
    )



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


