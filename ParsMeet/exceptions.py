class ParsMeetError(Exception):
    pass

class APIError(ParsMeetError):
    pass

class NetworkError(ParsMeetError):
    pass

class AuthError(ParsMeetError):
    pass

class RateLimitError(ParsMeetError):
    pass

class ValidationError(ParsMeetError):
    pass

class HandlerError(ParsMeetError):
    pass