import helper

from kv15.stopmessage import StopMessage
from kv15.kv15messages import KV15messages
from settings.const import remote

kv15 = KV15messages(stopmessages=[StopMessage(userstopcodes=['0000123', '1234000'], messagecontent='Hoi Joost'), StopMessage(userstopcodes=['1000123', '1234001'], messagecontent='Hoi Thomas')])
kv15.push(remote, '/KV15messages')
