class StorageError(Exception):
    pass

class StorageErrorConflict(StorageError):
    pass

class RecordNotFoundError(StorageError):
    pass

class BookReqFoundError(StorageError):
    pass

class InvalidFieldFormat(Exception):
    pass

class AuthError(Exception):
    pass

class PermissionsError(AuthError):
    pass
