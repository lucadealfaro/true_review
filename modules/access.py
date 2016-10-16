# Utility for access control.

from gluon import current


def is_logged_in():
    return current.auth.user_id is not None

def is_topic_admin(topic_id):
    user_id = current.auth.user_id
    if user_id is None:
        return False
    db = current.db
    reviewer = db((db.reviewer.user == user_id) &
                  (db.reviewer.topic == topic_id)).select().first()
    if reviewer is None:
        return False
    return reviewer.is_admin

def is_topic_reviewer(topic_id):
    user_id = current.auth.user_id
    if user_id is None:
        return False
    db = current.db
    reviewer = db((db.reviewer.user == user_id) &
                  (db.reviewer.topic == topic_id)).select().first()
    if reviewer is None:
        return False
    return reviewer.is_reviewer

def is_site_admin():
    """Uses a static list of site admins."""
    user_id = current.auth.user_id
    if user_id is None:
        return False
    db = current.db
    return db(db.auth_user.id == user_id).select().first().email in current.site_admins


### The Policies ###

def can_create_topic():
    return is_site_admin()

def can_edit_topic(topic_id):
    return is_topic_admin(topic_id) or is_site_admin()

def can_delete_topic(topic_id):
    return is_site_admin()

def can_add_paper(topic_id):
    """Only administrators for that topic can add papers to it."""
    return is_topic_admin(topic_id) or is_site_admin()

def can_edit_paper(topic_id):
    return is_topic_admin(topic_id) or is_site_admin()

def can_review(topic_id):
    """Only approved reviewers for that topic can add papers to it."""
    return is_topic_reviewer(topic_id) or is_site_admin()
