from gluon import current, redirect, URL

def component_fail(message):
    if current.session is not None:
        current.session.flash = message
    redirect(URL('components', 'empty'))

def get_paper_and_topic_ids():
    request = current.request
    paper_id = request.args(0)
    topic_id = request.args(1)
    # If topic_id is None or the string "primary", 
    # then uses as topic_id the main topic of the paper.
    if topic_id in [None, "primary"]:
        db = current.db
        paper = db((db.paper.paper_id == paper_id) &
                   (db.paper.end_date == None)).select().first()
        if paper is None:
            component_fail(T('No such paper'))
        topic_id = paper.primary_topic
    return (paper_id, topic_id)
    
