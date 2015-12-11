class HolviError(RuntimeError):
    pass

class ApiError(HolviError):
    pass

class AuthenticationError(HolviError):
    pass

class NotFound(HolviError):
    pass
