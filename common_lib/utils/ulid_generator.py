import ulid


def ulid_generator():
    return str(ulid.ULID())
