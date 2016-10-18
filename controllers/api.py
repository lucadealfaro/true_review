# Ajax functions callable from the front end.

def topic_papers():
    """Returns the list of papers in a given topic."""
    topic_id = request.args(0)
    topic = db.topic(topic_id)
    result = dict(papers=[], has_more=False)
    if topic is None:
        return response.json(result)
    orderby = db.paper.start_date # Fix
    all_papers = True # Fix
    start_idx = 0 # Fix
    end_idx = 20 # Fix
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
    records = db(q).select(orderby=orderby, limitby=(start_idx, end_idx + 1))
    papers = [dict(
        title = p.paper.title,
        authors = ', '.join(p.paper.authors),
        view_url = URL('default', 'view_paper', args=[p.paper.paper_id]),
        num_reviews = p.paper_in_topic.num_reviews,
        score = p.paper_in_topic.score,
        is_primary_topic = p.paper_in_topic.is_primary,
    ) for p in records]
    result['papers'] = papers
    return response.json(result)
