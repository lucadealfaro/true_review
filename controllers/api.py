# Ajax functions callable from the front end.

def topic_papers():
    """Returns the list of papers in a given topic."""
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
        q = ((db.paper_in_topic.topic == topic.id) &
             (db.paper_in_topic.paper_id == db.paper.paper_id) &
             (db.paper_in_topic.end_date == None) &
             (db.paper.end_date == None) &
             (db.topic.id == db.paper.primary_topic)
             )
    else:
        q = ((db.paper.primary_topic == topic_id) &
             (db.paper.end_date == None) &
             (db.paper.paper_id == db.paper_in_topic.paper_id) &
             (db.paper_in_topic.topic == topic_id) &
             (db.paper_in_topic.end_date == None)
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
    result['items'] = papers
    result['can_review'] = can_review(topic.id)
    result['can_add_paper'] = can_add_paper(topic.id)
    return response.json(result)
