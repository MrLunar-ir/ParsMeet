class ParsMeetError(Exception):
    pass

class ParsMeetAuthError(ParsMeetError):
    pass

class ParsMeetNetworkError(ParsMeetError):
    pass

class ParsMeetRoomNotFoundError(ParsMeetError):
    pass