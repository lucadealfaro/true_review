from gluon import *

def reputation_atom(old_score, grade, current_score):
    """Returns the reputation boost due to having assigned [grade] to a paper
       that at the time had score [old_score] 
       and currently has score [current_score]."""
    baseline = 10
    alpha = 0.5 # fraction of "informativeness"
    return baseline + alpha*(old_score-current_score)**2 - (1-alpha)*(grade-current_score)**2


def update_reputation(paper, topic, review_id, old_score, new_score):
    """Update the reputation of all involved users after a new review.
       It should be called whenever the score of a paper changes."""

    logger = current.logger
    db = current.db

    # All users who have reviewed this paper in this topic.
    reviewers = db( (db.review.paper_id == paper.paper_id) &
                    (db.review.topic == topic.id) &
                    (db.reviewer.user == db.review.author) & 
                    (db.reviewer.topic == topic.id) ).select(db.reviewer.ALL, distinct=True)
    for reviewer in reviewers:
        # the earliest review of this reviewer on this paper in this topic
        # (it may even be the very review that originated this update request)
        effective_review = db( (db.review.paper_id == paper.paper_id) &
                               (db.review.author == reviewer.user) ).select(
                                    db.review.ALL, orderby=db.review.start_date).first()
        if effective_review.id == review_id:
            old_reputation_boost = 0
        else:
            old_reputation_boost = reputation_atom(effective_review.old_score, 
                                                   effective_review.grade, 
                                                   old_score)
        new_reputation_boost = reputation_atom(effective_review.old_score, 
                                               effective_review.grade, 
                                               new_score)
        new_reputation = reviewer.reputation - old_reputation_boost + new_reputation_boost
        reviewer.update_record(reputation=new_reputation)
        logger.info("Updating user %r with new reputation = %r" % (reviewer.user, new_reputation) );
