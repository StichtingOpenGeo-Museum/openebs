import helper
from kv17.mutatejourney import MutateJourney
from enum.reason import ReasonType
from enum.reason import SubReasonType
from settings.const import remote

kv17 = MutateJourney('CXX','B120',525,'2009-01-12')
kv17.shorten('101')
kv17.shorten('110')
kv17.shorten('109')
kv17.shorten('108')
kv17.shorten('107')
kv17.changepasstimes('102','FIRST','00:00:00','08:45:00')
kv17.changedestination('102','UtrNeude01','Utrecht Neude','Utrecht Neude')
kv17.changepasstimes('103','INTERMEDIATE','08:50:00','08:50:00')
kv17.changedestination('103','UtrNeude01','Utrecht Neude','Utrecht Neude')
kv17.changepasstimes('104','INTERMEDIATE','08:55:00','08:55:00')
kv17.changedestination('104','UtrNeude01','Utrecht Neude','Utrecht Neude')
kv17.changepasstimes('105','INTERMEDIATE','09:00:00','09:05:00')
kv17.changedestination('105','UtrNeude01','Utrecht Neude','Utrecht Neude')
kv17.changepasstimes('106','LAST','09:10:00','09:00:00')
kv17.reasontype = ReasonType.OMGEVING
kv17.subreasontype = SubReasonType.WERKZAAMHEDEN
kv17.mutationmessage('105')
kv17.push(remote,'/TMI_Post/KV17')
