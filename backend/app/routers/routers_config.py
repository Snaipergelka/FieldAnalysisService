from backend.app.database import crud


def connecting_to_db():
    """
    Creates instance of CRUD class
    that connects to database.
    :return:
    """
    return crud.CRUD()
