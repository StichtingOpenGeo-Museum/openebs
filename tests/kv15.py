import helper

from time import sleep

from datetime import date
from datetime import time
from datetime import datetime

from kv15.stopmessage import StopMessage
from kv15.deletemessage import DeleteMessage
from kv15.kv15messages import KV15messages
from settings.const import remote

from enum.messagepriority import MessagePriority
from enum.messagetype import MessageType
from enum.messagedurationtype import MessageDurationType

def waitforit(timestamp):
	now = datetime.today()
	seconds = (timestamp - now).seconds
	print '\nWaiting for: %s (%ds)' % (timestamp, seconds)
	if seconds < 3600:
		sleep(seconds)

XX = 23
YY = (XX + 1) % 24


# GENERAL
# REMOVE

waitforit(datetime.combine(date.today(), time(XX, 00)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='GENERAL REMOVE')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.REMOVE
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(XX, 10)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# GENERAL
# ENDTIME

waitforit(datetime.combine(date.today(), time(XX, 15)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='GENERAL ENDTIME')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.ENDTIME
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(XX, 20))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(XX, 20)))

waitforit(datetime.combine(date.today(), time(XX, 25)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='GENERAL ENDTIME2')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.ENDTIME
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(XX, 35))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(XX, 30)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# GENERAL
# FIRSTVEJO

waitforit(datetime.combine(date.today(), time(XX, 35)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='GENERAL FIRSTVEJO')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.FIRSTVEJO
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(XX, 37))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')


waitforit(datetime.combine(date.today(), time(XX, 45)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='GENERAL FIRSTVEJO2')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.FIRSTVEJO
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(XX, 46)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# OVERRULE
# REMOVE

waitforit(datetime.combine(date.today(), time(XX, 50)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE REMOVE')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.REMOVE
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(XX, 55)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# OVERRULE
# ENDTIME

waitforit(datetime.combine(date.today(), time(YY, 00)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE ENDTIME')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.ENDTIME
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(YY, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(YY, 05)))

waitforit(datetime.combine(date.today(), time(YY, 10)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE ENDTIME2')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.ENDTIME
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(YY, 20))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(YY, 15)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# OVERRULE
# FIRSTVEJO

waitforit(datetime.combine(date.today(), time(YY, 20)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE FIRSTVEJO')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.FIRSTVEJO
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
msg.messageendtime = datetime.combine(date.today(), time(YY, 22))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')


waitforit(datetime.combine(date.today(), time(YY, 30)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE FIRSTVEJO2')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.FIRSTVEJO
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(YY, 31)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


# Overigen

waitforit(datetime.combine(date.today(), time(YY, 35)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='OVERRULE FIRSTVEJO')
msg.messagetype = MessageType.BOTTOMLINE
msg.mesagedurationtype = MessageDurationType.FIRSTVEJO
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')


# Lange vrijetekst met een tekst van
# ongeveer 200 karakters

waitforit(datetime.combine(date.today(), time(YY, 40)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='Deze aanbieder adviseert over en ontwikkelt, beheert en onderhoudt informatiesystemen voor mobiliteit. Als specialist in multi-modaal verkeer en vervoer zet zij haar kennis en ervaring in voor het hele traject van systeemontwikkeling en -onderhoud.')
msg.messagetype = MessageType.GENERAL
msg.mesagedurationtype = MessageDurationType.REMOVE
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(YY, 45)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')


waitforit(datetime.combine(date.today(), time(YY, 50)))
msg = StopMessage(userstopcodes=['42028501'], messagecontent='Deze aanbieder adviseert over en ontwikkelt, beheert en onderhoudt informatiesystemen voor mobiliteit. Als specialist in multi-modaal verkeer en vervoer zet zij haar kennis en ervaring in voor het hele traject van systeemontwikkeling en -onderhoud.')
msg.messagetype = MessageType.OVERRULE
msg.mesagedurationtype = MessageDurationType.REMOVE
msg.messagestarttime = datetime.combine(date.today(), time(XX, 05))
kv15 = KV15messages(stopmessages = [msg])
kv15.push(remote, '/TMI_Post/KV15')

waitforit(datetime.combine(date.today(), time(YY, 55)))
delmsg = msg.delete()
kv15 = KV15messages(stopmessages = [delmsg])
kv15.push(remote, '/TMI_Post/KV15')




#kv15 = KV15messages(stopmessages=[StopMessage(userstopcodes=['0000123', '1234000'], messagecontent='Hoi Joost'), StopMessage(userstopcodes=['1000123', '1234001'], messagecontent='Hoi Thomas')])
#kv15 = KV15messages(stopmessages=[StopMessage(userstopcodes=['0000123', '1234000'], messagecontent='Hoi Joost'), StopMessage(userstopcodes=['1000123', '1234001'], messagecontent='Hoi Thomas')])
#kv15.push(remote, '/TMI_Post/KV15')
