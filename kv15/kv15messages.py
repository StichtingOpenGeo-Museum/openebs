from io.push import Push
from kv15.database import connect

class KV15messages:
    def __init__(self, stopmessages = None):
        if stopmessages is None:
            self.stopmessages = []
        else:
            self.stopmessages = stopmessages

    def __str__(self):
        xml = """       <KV15messages>\n"""
        for stopmessage in self.stopmessages:
            xml += str(stopmessage)
        xml += """      </KV15messages>"""

        return xml

    def push(self, remote, path):
        return Push(dossiername='KV15messages', content = self, namespace='http://bison.connekt.nl/tmi8/kv15/msg').push(remote, path)

    def save(self, cur = None):
        if cur is None:
            cur = connect()

        for stopmessage in self.stopmessages:
            stopmessage.save(cur)
