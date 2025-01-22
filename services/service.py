class Service:
    def __init__(self, name, client):
        self.name = name
        self.client = client
        self.enabled = False

    def run(self, roles):
        pass

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class ServiceData:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return self.name