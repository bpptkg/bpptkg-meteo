from .sessions import session_scope


def bulk_insert(engine, model, entries):
    """
    Insert entries to database model.

    This operation is done by using SQLAlchemy session bulk insert mappings.
    """

    with session_scope(engine) as session:
        session.bulk_insert_mappings(model, entries)
        session.commit()
