def prepare(base_class, engine):
    """
    Reflect base class to current database engine.
    """
    base_class.prepare(engine, reflect=True)
