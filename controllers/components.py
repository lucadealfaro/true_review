# Here we put code for producing components that are in charge of
# rendering particular elements, and can be included in views.

import review_utils
from component_utils import component_fail, get_paper_and_topic_ids

def empty():
    """In case you want an empty component (say, after an error)."""
    return ""

def paper_topic_grid(topic_id, all_papers=False):
    """Produces a grid containing the papers in a topic.
    The grid is done so that it can be easily included in a more complex page.
    The arguments are:
    - topic_id (in path)
    - all_papers=y (in query): if yes, then also papers that are not primary in the topic
      will be included.
    """
    topic = db.topic(topic_id)
    if topic is None:
        component_fail(T('No such topic.'))
    fields = [db.paper_in_topic.paper_id, db.paper.id, db.paper.paper_id,
              db.paper.title, db.paper.authors, db.paper_in_topic.is_primary]
    orderby = db.paper.start_date
    links = []
    if all_papers:
        q = ((db.paper_in_topic.topic == topic.id) &
             (db.paper_in_topic.paper_id == db.paper.paper_id) &
             (db.paper_in_topic.end_date == None) &
             (db.paper.end_date == None) &
             (db.topic.id == db.paper.primary_topic)
             )
        fields.extend([db.paper.primary_topic, db.topic.name])
        # db.paper.primary_topic.represent = lambda v, r: '' if v == topic_id else v
        db.paper.primary_topic.label = T('Primary topic')
        db.topic.name.readable = False
        db.paper.primary_topic.represent = lambda v, r: A(r.topic.name, _href=URL('default', 'topic_index', args=[v]))
        links.append(dict(header='',
                          body=lambda r: (icon_primary_paper if r.paper_in_topic.is_primary else icon_all_paper)))

    else:
        q = ((db.paper.primary_topic == topic_id) &
             (db.paper.end_date == None) &
             (db.paper.paper_id == db.paper_in_topic.paper_id) &
             (db.paper_in_topic.topic == topic_id) &
             (db.paper_in_topic.end_date == None)
             )
        fields.extend([db.paper_in_topic.num_reviews, db.paper_in_topic.score])
        orderby = ~db.paper_in_topic.score
        links.append(dict(header='', body=lambda r: icon_primary_paper))
    db.paper.title.represent = lambda v, r: A(v, _href=URL('default', 'view_paper',
                                                           args=[r.paper_in_topic.paper_id, topic.id]))
    # links.append(dict(header='',
    #                   body=lambda r: A('Versions', _href=URL('default', 'view_paper_versions',
    #                                                         args=[r.paper_in_topic.paper_id]))))
    # links.append(dict(header='',
    #                   body=lambda r: A('Edit', _href=URL('default', 'edit_paper',
    #                                                      args=[r.paper_in_topic.paper_id], vars=dict(topic=topic.id)))))
    grid = SQLFORM.grid(q,
        args=request.args[:1], # The first parameter is the topic id.
        orderby=orderby,
        fields=fields,
        field_id=db.paper.id,
        csv=False, details=False,
        links=links,
        links_placement='left',
        # These all have to be done with special methods.
        create=False,
        editable=False,
        deletable=False,
        maxtextlength=48,
    )
    return grid


def paper_topic_index():
    """Returns a grid, and associated code, to display all papers in a topic.

    Arguments:
        - topic_id (in path): id of the topic
        - all_papers=y: in query, indicates whether all papers should be shown.
    """
    topic_id = request.args(0)
    all_papers = request.vars.all_papers == 'y'
    grid = paper_topic_grid(topic_id, all_papers=all_papers)
    # Creates buttons to see all papers, or only the papers that are primary.
    all_paper_vars = request.vars.copy()
    all_paper_vars.update(dict(all_papers='y'))
    topic_paper_vars = request.vars.copy()
    topic_paper_vars.update(dict(all_papers='n'))
    all_papers_classes = 'btn btn-success'
    primary_papers_classes = 'btn btn-success'
    if all_papers:
        all_papers_classes += ' disabled'
    else:
        primary_papers_classes += ' disabled'
    button_all_papers = A(icon_all_paper, T('All papers'), _id='all_papers_button',
                          cid=request.cid,  # trapped load
                          _class=all_papers_classes,
                          _href=URL('components', 'paper_topic_index',
                                    args=request.args, vars=all_paper_vars))
    button_topic_papers = A(icon_primary_paper, T('Primary topic papers'), _id='primary_papers_button',
                            cid=request.cid,  # trapped load
                            _class=primary_papers_classes,
                            _href=URL('components', 'paper_topic_index',
                                      args=request.args, vars=topic_paper_vars))
    button_list = [button_topic_papers, button_all_papers]
    if can_review(topic_id):
        pick_paper_review_link = A(icon_pick_review, T('Choose paper to review'),
                                   _class='btn btn-primary',
                                   _href=URL('default', 'pick_review', args=[topic_id]))
        button_list.append(pick_paper_review_link)
    if can_add_paper(topic_id):
        add_paper_link = A(icon_add, 'Add a paper', _class='btn btn-danger',
                           _href=URL('default', 'edit_paper', vars=dict(topic=topic_id)))
        button_list.append(add_paper_link)
    return dict(grid=grid,
                button_list=button_list)


def reviewers_topic_grid():
    """Grid containing the reviewers in a topic.
    The grid is done so that it can be easily included in a more complex page.
    The arguments are:
    - topic_id (in path)
    """
    topic = db.topic(request.args(0)) or component_fail(T('No such topic'))
    q = ((db.role.topic == topic.id) &
         (db.role.user_email == get_user_email()))
    grid = SQLFORM.grid(q,
        args = request.args[:1], # First is topic_id
        orderby=~db.role.reputation,
        field_id=db.role.id,
        fields=[db.role.reputation, db.auth_user.display_name, db.auth_user.affiliation, db.auth_user.link],
        csv=False, details=True,
        create=False, editable=False, deletable=False,
        maxtextlength=48,
    )
    return grid


def paper_info():
    """Returns information on a paper.
        Arguments:
        - paper_id (in path)
        Optional:
        - topic_id (in path)
        - id=pid (in query) where pid is the id of the paper in the version.
        - date=date (in query) shows the version that was active at a given date.
    """
    (paper_id, topic_id) = get_paper_and_topic_ids()
    if request.vars.id is not None:
        paper = db(db.paper.id == id).select().first()
        paper_id = paper.paper_id # For consistency
    elif request.vars.date is not None:
        d = parse_date(request.vars.date)
        paper = db((db.paper.paper_id == paper_id) &
                   (db.paper.start_date <= d) &
                   ((db.paper.end_date == None) | (db.paper.end_date >= d))).select().first()
    else:
        # Selects last paper.
        paper = db((db.paper.paper_id == paper_id) &
                   (db.paper.end_date == None)).select().first()
    # Paper topics, score, and number of reviews.
    all_topics = db((db.paper_in_topic.paper_id == paper_id) &
                    (db.paper_in_topic.end_date == None) &
                    (db.topic.id == db.paper_in_topic.topic)).select()
    secondary_topics=[]
    primary_topic_name = None
    primary_topic = None
    primary_paper_topic = None
    for t in all_topics:
        if t.paper_in_topic.is_primary:
            primary_topic = t.topic
            primary_paper_topic = t.paper_in_topic
            primary_topic_name = represent_paper_topic(primary_topic.name, primary_topic)
        else:
            secondary_topics.append(represent_paper_topic(t.topic.name, t.topic))
    topics_els = [T('Primary topic: '), primary_topic_name]
    if len(secondary_topics) > 0:
        topics_els.append(SPAN(T(' Secondary topics:'), ' ', _class="second_span"))
        topics_els.append(secondary_topics[0])
        for t in secondary_topics[1:]:
            topics_els.extend([SPAN(', '), t])
    topics_span = SPAN(*topics_els)
    # Earliest, and latest dates.
    latest_version_date = represent_date(paper.start_date, paper)
    earliest_paper = db(db.paper.paper_id == paper_id).select(orderby=db.paper.start_date).first()
    first_version_date = earliest_paper.start_date
    # Creates the button list.
    button_list = []
    if can_edit_paper(topic_id):
        button_list.append(A(icon_edit, T('Edit paper'), _class='btn btn-warning',
                             _href=URL('default', 'edit_paper', args=[paper_id])))
    return dict(paper=paper,
                topics=topics_span,
                first_version_date=first_version_date,
                latest_version_date=latest_version_date,
                abstract=text_store_read(paper.abstract),
                score=primary_paper_topic.score if primary_paper_topic else None,
                num_reviews=primary_paper_topic.num_reviews if primary_paper_topic else None,
                button_list=button_list,
                )



def paper_review_grid():
    """Grid of reviews for a paper.

    The arguments are:
    - paper_id
    - topic_id or the string "primary"
    """
    (paper_id, topic_id) = get_paper_and_topic_ids()

    # DEBUG
    logger.info("paper_review_grid : %r %r" % (paper_id, topic_id))

    q = ((db.review.paper_id == paper_id) &
         (db.review.topic == topic_id) &
         (db.review.end_date == None))
    # Retrieves the edit history of reviews.
    def get_review_history(r):
        logger.info("get_review_history : %r %r %r" % (paper_id, topic_id, r))
        review_history_len = db((db.review.paper_id == paper_id) &
                                (db.review.topic == topic_id) &
                                (db.review.user_email == r.user_email)).count()
        return '' if review_history_len < 2 else A(T('Review history'), cid=request.cid,
                                                     _href=URL('components', 'review_history',
                                                               args=[r.review_id, paper_id]))
    # Retrieves the version of paper reviewed, if different from current one.
    current_paper = db((db.paper.paper_id == paper_id) &
                       (db.paper.end_date == None)).select().first()
    def get_reviewed_paper(r):
        if r.paper == current_paper.id:
            return 'Current'
        else:
            return A(T('View'), _href=URL('default', 'view_specific_paper_version', args=[r.paper]))
    links = []
    db.review.paper.readable = False
    db.review.user_email.readable = False
    # Link to review edit history if any.
    links.append(dict(header='',
                      body=lambda r: get_review_history(r)))
    # Link to actual version of paper reviewed, if different from current one.
    links.append(dict(header='Reviewed version',
                      body=lambda r: get_reviewed_paper(r)))
    # edit_review_link=A(T('Edit'), cid=request.cid, _href=URL('components', 'do_review', args=[paper_id, topic_id]))
    grid = SQLFORM.grid(q,
        args=request.args[:2],
        fields=[db.review.grade, db.review.useful_count, db.review.review_content, db.review.review_id,
                db.review.paper_id, db.review.paper, db.review.user_email, db.review.start_date],
        links=links,
        orderby=~db.review.start_date,
        details=True, csv=False,
        editable=False, deletable=False, create=False,
        maxtextlength=48,
        )
    return grid


def paper_reviews():
    """List of reviews for a paper.
       Argument: paper_id"""
    grid = paper_review_grid()
    (paper_id, topic_id) = get_paper_and_topic_ids()
    # DEBUG
    # logger.info("paper_reviews: args(0) %r args(1) %r" % (request.args(0), request.args(1)))
    paper = db((db.paper.paper_id == paper_id) &
               (db.paper.end_date == None)).select().first()
    button_list = []
    if auth.user_id is not None:
        # We let a user add a review only if it has not written one already.
        no_user_review = db((db.review.user_email == get_user_email()) &
                            (db.review.paper_id == paper_id)).isempty()
        if no_user_review and can_review(topic_id):
            button_review = A(icon_add, T('Write a review'),
                              _class='btn btn-danger', cid=request.cid,
                              _href=URL('components', 'do_review', args=[paper_id, topic_id, 'e']))
            button_list.append(button_review)
        elif not no_user_review: # user has a review
            button_your_review = A(icon_your_review, T('Your review'),
                                   _class='btn btn-success', cid=request.cid,
                                   _href=URL('components', 'do_review', args=[paper_id, topic_id, 'v']))
            button_list.append(button_your_review)
    return dict(grid=grid, button_list=button_list)


@auth.requires_login()
def do_review():
    """Shows to a user their review of a paper, allowing them to edit it
    or to enter it for the first time.  The arguments are:
    - paper_id : the paper.
    - topic.id : the id of the topic, or the string "primary".
    - v / e: view, or edit.
    If there is a current review, then lets the user edit that instead,
    keeping track of the old review.
    """
    (paper_id, topic_id) = get_paper_and_topic_ids()
    is_view = request.args(2) == 'v'

    paper = db((db.paper.paper_id == request.args(0)) &
               (db.paper.end_date == None)).select().first()
    topic = db.topic(topic_id)

    #logger.info("do_review paper.id %r topic.id %r is_view %r" % (paper,topic,is_view))

    if paper is None or topic is None:
        component_fail(T('No such paper or topic.'))

    # Checks whether the paper is currently in the topic.
    paper_in_topic = db((db.paper_in_topic.paper_id == paper.paper_id) &
                        (db.paper_in_topic.topic == topic.id) &
                        (db.paper_in_topic.end_date == None)).select().first()
    if paper_in_topic is None:
        component_fail(T('The paper is not in the selected topic'))
    # Verify permissions.
    if not is_view and not can_review(topic.id):
        component_fail(T('You do not have the permission to perform reviews in this topic'))
    # Fishes out the current review, if any.
    current_review = db((db.review.user_email == get_user_email()) &
                        (db.review.paper_id == paper.paper_id) &
                        (db.review.topic == topic.id) &
                        (db.review.end_date == None)).select().first()
    # Sets some defaults.
    logger.info("My user email: %r" % get_user_email())
    db.review.paper.writable = False
    db.review.paper_id.readable = False
    db.review.user_email.default = get_user_email()
    db.review.paper_id.default = paper.paper_id
    db.review.paper.default = paper.id
    db.review.topic.default = topic.id
    db.review.start_date.label = T('Review date')
    db.review.end_date.readable = False
    db.review.useful_count.readable = is_view
    db.review.old_score.default = paper_in_topic.score
    # Creates the form for editing.
    form = SQLFORM(db.review, record=current_review, readonly=is_view)
    form.vars.user_email = get_user_email()
    form.vars.review_content = None if current_review is None else text_store_read(current_review.review_content)
    if form.validate():
        # We must write the review as a new review.
        # First, we close the old review if any.
        now = datetime.utcnow()
        if current_review is not None:
            current_review.update_record(end_date=now)
        # Builds the correct review id.
        review_id = current_review.review_id if current_review is not None else None
        if review_id is None:
            review_id = review_utils.get_random_id()
        # Then, writes the current review.
        db.review.insert(user_email=get_user_email(),
                         paper_id=paper.paper_id,
                         review_id=review_id,
                         paper=paper.id,
                         topic=topic.id,
                         start_date=now,
                         end_date=None,
                         review_content=str(text_store_write(form.vars.content)),
                         old_score=paper_in_topic.score,
                         grade=form.vars.grade,
                         )
        add_reviewer_to_topic(get_user_email(), topic.id)
        session.flash = T('Your review has been accepted.')
        redirect(URL('components', 'do_review', args=[paper.paper_id, topic_id, 'v']))
    button_list = []
    button_list.append(A(icon_reviews, T('All reviews'), cid=request.cid,
                         _class='btn btn-success',
                         _href=URL('components', 'paper_reviews', args=[paper.paper_id, topic_id])))
    if is_view and can_review(topic.id):
        button_list.append(A(icon_edit, T('Edit review'), cid=request.cid,
                             _class='btn btn-warning',
                             _href=URL('components', 'do_review', args=[paper.paper_id, topic_id, 'e'])))
    # else:
    #    button_list.append(A(icon_your_review, T('Your review'), cid=request.cid,
    #                         _class='btn btn-success',
    #                         _href=URL('components', 'do_review', args=[paper.paper_id, topic_id, 'v'])))
    return dict(button_list=button_list,
                form=form)


def review_history():
    """Shows the review history of a certain paper by a certain author in
    the paper primary topic.

    The arguments are:
    - review id (the rest of the information is taken from the review)
    - paper id  (to produce other links).
    """
    db.review.paper.represent = lambda v, r: represent_specific_paper_version(v)
    review_id = request.args(0)
    paper_id = request.args(1)
    q = (db.review.review_id == review_id)
    grid = SQLFORM.grid(q,
        args=request.args[:2],
        fields=[db.review.grade, db.review.useful_count, db.review.content,
                db.review.paper, db.review.start_date],
        details=True, csv=False,
        editable=False, deletable=False, create=False,
        maxtextlength=48,
        )
    button_list=[]
    button_list.append(A(icon_reviews, T('All reviews'), cid=request.cid,
                     _class='btn btn-success',
                     _href=URL('components', 'paper_reviews', args=[paper_id])))
    # We let a user add a review only if it has not written one already.
    no_user_review = db((db.review.author == auth.user_id) &
                        (db.review.paper_id == paper_id)).isempty()
    paper =  db((db.paper.paper_id == paper_id) &
                   (db.paper.end_date == None)).select().first()
    topic_id = paper.primary_topic
    if no_user_review and can_review(topic_id):
        button_review = A(icon_add, T('Write a review'),
                          _class='btn btn-danger', cid=request.cid,
                          _href=URL('components', 'do_review', args=[paper_id, topic_id, 'e']))
        button_list.append(button_review)
    else:
        button_your_review = A(icon_your_review, T('Your review'),
                               _class='btn btn-success', cid=request.cid,
                               _href=URL('components', 'do_review', args=[paper_id, topic_id, 'v']))
        button_list.append(button_your_review)

    author = db.auth_user(request.args(2))
    return dict(grid=grid,
                button_list=button_list,
                author=author)
