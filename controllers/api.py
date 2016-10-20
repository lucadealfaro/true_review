# Ajax functions callable from the front end.

def topic_papers():
    """Returns the list of papers in a given topic.  Accessed by topic id."""
    topic_id = request.args(0)
    topic = db.topic(topic_id)
    result = dict(papers=[], has_more=False)
    if topic is None:
        return response.json(result)
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    all_papers = False if request.vars.primary_papers == 'true' else True
    orderby = ~db.paper_in_topic.score
    if request.vars.sort_score is not None:
        orderby = db.paper_in_topic.score if request.vars.sort_score == 'up' else ~db.paper_in_topic.score
    if request.vars.sort_title is not None:
        orderby = db.paper.title if request.vars.sort_title == 'up' else ~db.paper.title
    if request.vars.sort_num_reviews is not None:
        orderby = db.paper_in_topic.num_reviews if request.vars.sort_num_reviews == 'up' else ~db.paper_in_topic.num_reviews
    if all_papers:
        # All papers that have the given topic among the topics.
        q = (
            (db.paper.end_date == None) & # Paper is current.
            (db.paper_in_topic.topic == db.topic.id) & # Relation with ...
            (db.paper_in_topic.paper == db.paper.id) & # ...topic
            (db.topic.id == topic_id) # And the topic is the specified one.
        )
    else:
        # Papers of a given primary topic.
        q = (
            (db.paper.end_date == None) & # Paper is current.
            (db.paper.primary_topic == topic_id) & # And it has the indicated primary topic.
            (db.paper_in_topic.topic == db.topic_id) & # Relation with ...
            (db.paper_in_topic.paper == db.paper.id) & # ...topic
            (db.topic.id == topic_id) # And the topic is the specified one.
        )
    logger.info("Query; %r" % q)
    records = db(q).select(orderby=orderby, limitby=(start_idx, end_idx + 1))
    papers = [dict(
        title = p.paper.title,
        authors = ', '.join(p.paper.authors),
        view_url = URL('default', 'view_paper', args=[p.paper.paper_id]),
        num_reviews = p.paper_in_topic.num_reviews,
        score = p.paper_in_topic.score,
        is_primary_topic = p.paper_in_topic.is_primary,
    ) for p in records]
    result['has_more'] = len(papers) > end_idx - start_idx
    papers = papers[:end_idx - start_idx]
    result['papers'] = papers
    result['can_review'] = can_review(topic.id)
    result['can_add_paper'] = can_add_paper(topic.id)
    logger.info("Returning items: %r", papers)
    return response.json(result)


def topic_reviewers():
    """Returns the list of reviewers in a given topic."""
    topic_id = request.args(0)
    topic = db.topic(topic_id)
    result = dict(papers=[], has_more=False)
    if topic is None:
        return response.json(result)
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    q = ((db.role.topic == topic.id) &
         (db.role.is_reviewer == True) &
         (db.role.user_email == get_user_email()))
    logger.info("Query; %r" % q)
    records = db(q).select(orderby=~db.role.reputation, limitby=(start_idx, end_idx + 1))
    reviewers = []
    for p in records:
        name, link = get_user_name_and_link(p.user_email)
        reviewers.append(dict(
            name=name,
            score=p.reputation,
            link=link,
            has_link=link is not None,
        ))
    result['has_more'] = len(reviewers) > end_idx - start_idx
    reviewers = reviewers[:end_idx - start_idx]
    result['reviewers'] = reviewers
    return response.json(result)


def get_paper_versions():
    """Returns the list of versions of a paper.  The argument is the paper_id."""
    q = (db.paper.paper_id == request.args(0))
    versions = db(q).select(orderby=db.paper.start_date).as_list()
    # Converts the dates.
    for v in versions:
        v['start_validity'] = datetime_validator.formatter(v.start_date)
        v['end_validity'] = T('current') if v.end_date is None else datetime_validator.formatter(v.end_date)
    return response.json(dict(
        versions=versions,
    ))


def get_paper_topics():
    """Returns the list of topics for the paper.
    These topics can be used to access the reviews.
    This is accessed by paper id."""
    rows = db((db.paper_in_topic.paper == request.args(0)) &
              (db.paper_in_topic.topic == db.topic.id)).select()
    num_reviews = None
    score = None
    topics = []
    for t in rows:
        if t.paper_in_topic.is_primary:
            num_reviews = t.num_reviews
            score = t.score
        topics.append(dict(
            topic_id=t.topic.id,
            topic_name=t.topic.name,
            is_primary=t.paper_in_topic.is_primary,
        ))
    return response.json(dict(
        num_reviews=num_reviews,
        score=score,
        topics=topics,
    ))


def get_paper_reviews():
    """Gets the reviews for a specific version of a paper.
    For each review, we return the most recent; there is a history of reviews that we keep
    internally, but we display the most recent one.
    Parameters:
        - id of the paper
        sort order
        """
    # Decides on the order.  By date, or by score.  Default is newest on top.
    orderby = ~db.review.start_date
    reviews = []
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    if request.vars.sort_reputation is not None:
        rows = db((db.review.paper == request.args(0)) &
                  (db.review.end_date == None) &
                  (db.review.user_email == db.role.user_email) &
                  (db.role.topic == db.paper.primary_topic) &
                  (db.paper.id == request.args(0))).select(
            orderby=~db.role.reputation, limitby=(start_idx, end_idx + 1))
        for r in rows:
            reviews.append(dict(
                start_date=r.review.start_date,
                review_content=r.review.review_content,
                review_grade=r.review.grade,
                useful_count=r.review.userful_count))
    else:
        if request.vars.sort_grade is not None:
            orderby = db.review.grade if request.vars.sort_grade == 'up' else ~db.review.grade
        if request.vars.sort_date is not None:
            orderby = db.review.start_date if request.vars.sort_date == 'up' else ~db.review.start_date
        if request.vars.sort_useful is not None:
            orderby = db.review.useful_count if request.vars.sort_useful == 'up' else ~db.review.useful_count
        rows = db((db.review.paper == request.args(0)) &
                  (db.review.end_date == None)).select(orderby=orderby, limitby=(start_idx, end_idx + 1))
        for r in rows:
            reviews.append(dict(
                start_date=r.start_date,
                review_content=r.review_content,
                review_grade=r.grade,
                useful_count=r.userful_count))
    result = {}
    result['has_more'] = len(reviews) > end_idx - start_idx
    result['reviews'] = reviews[:end_idx - start_idx]
    return response.json(result)

