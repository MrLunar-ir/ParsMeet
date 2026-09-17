class MaintenanceMode:
    def __init__(self, message="Bot is under maintenance."):
        self.active = False
        self.message = message

    def enable(self, message=None):
        self.active = True
        if message:
            self.message = message

    def disable(self):
        self.active = False

    def check(self):
        return self.active