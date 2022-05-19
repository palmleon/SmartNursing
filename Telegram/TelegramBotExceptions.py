# Specific Exception Classes for the Telegram Bot

class DuplicatePatientError(Exception):
    pass
class ServerNotFoundError(Exception):
    pass
class PatientNotFoundError(Exception):
    pass
class RoomNotFoundError(Exception):
    pass
class ShiftStartedError(Exception):
    pass
class ShiftEndedError(Exception):
    pass