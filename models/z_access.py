# Utility for access control.

def is_logged_in():
    return auth.user_id is not None

def is_topic_admin(topic_id):
    if not auth.user:
        return False
    role = db((db.role.user_email == auth.user.email) &
                  (db.role.topic == topic_id)).select().first()
    if role is None:
        return False
    return role.is_admin

def is_topic_reviewer(topic_id):
    if not auth.user:
        return False
    role = db((db.role.user_email == auth.user.email) &
                  (db.role.topic == topic_id)).select().first()
    if role is None:
        return False
    return role.is_reviewer

def is_site_admin():
    """Uses a static list of site admins."""
    if not auth.user:
        return False
    return auth.user.email in site_admins

# The updates.

def add_admin_to_topic(user_email, topic_id):
    db.role.update_or_insert(
        (db.role.user_email == user_email) & (db.role.topic == topic_id),
        user_email=user_email,
        topic=topic_id,
        is_admin=True
    )

def add_reviewer_to_topic(user_email, topic_id):
    db.role.update_or_insert(
        (db.role.user_email == user_email) & (db.role.topic == topic_id),
        user_email=user_email,
        topic=topic_id,
        is_reviewer=True
    )

def add_author_to_topic(user_email, topic_id):
    db.role.update_or_insert(
        (db.role.user_email == user_email) & (db.role.topic == topic_id),
        user_email=user_email,
        topic=topic_id,
        is_author=True
    )


### The Policies ###

def can_create_topic():
    return is_site_admin()

def can_edit_topic(topic_id):
    return is_topic_admin(topic_id) or is_site_admin()

def can_delete_topic(topic_id):
    return is_site_admin()

def can_add_paper(topic_id):
    """Only administrators for that topic can add items to it."""
    if is_topic_admin(topic_id) or is_site_admin():
        return True
    if not auth.user_id:
        # Non logged-in users cannot add papers.
        return False
    t = db.topic(topic_id)
    return t is not None and t.topic_kind == 'open'

def can_edit_paper(topic_id):
    return is_topic_admin(topic_id) or is_site_admin()

def can_review(topic_id):
    """Only approved reviewers for that topic can add items to it."""
    return is_topic_reviewer(topic_id) or is_site_admin()


## Helpers

def is_topic_empty(topic_id):
    return (
        db(db.paper_in_topic.topic == topic_id).isempty() and
        db(db.paper.primary_topic == topic_id).isempty() and
        db(db.review.topic == topic_id).isempty()
    )