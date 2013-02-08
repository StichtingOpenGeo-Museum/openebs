import psycopg2

from io.push import Push

from settings.const import kv15_database_connect

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

    def save(self, conn = None, messagescenario = None):
        conn_created = False
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)
            conn_created = True
        for stopmessage in self.stopmessages:
            stopmessage.save(conn,messagescenario)
        if conn_created:
            conn.close()

    def log(self, conn = None,author=None,message=None,ipaddress=None):
        conn_created = False
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)
            conn_created = True
        for stopmessage in self.stopmessages:
            stopmessage.log(conn,author=author,message=message,ipaddress=ipaddress)
        if conn_created:
            conn.close()
