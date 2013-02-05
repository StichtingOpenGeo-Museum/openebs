import helper
import uwsgi
import cgi
import datetime
import psycopg2
import json
import re
from datetime import date
from kv78turbo.render import renderLines, getLines as cacheLines
from kv78turbo.journeypatternizer import getLines
from enum.messagepriority import MessagePriority
from enum.messagetype import MessageType
from enum.domain import auth_lookup
from enum.authorization import authorization
from settings.const import remote,remote_path,kv15_database_connect,send
from datetime import datetime,timedelta
from kv15.stopmessage import StopMessage
from kv15.kv15messages import KV15messages
from kv15.deletemessage import DeleteMessage
from kv78turbo.kv7api import querylines,querylinesperstop,querystopinline

COMMON_HEADERS_JSON = [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]
COMMON_HEADERS_TEXT = [('Content-Type', 'text/plain'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]
COMMON_HEADERS_HTML = [('Content-Type', 'text/html'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]

def templateLijnen(content):
    template = open('templates/lijnen.html').read()
    return template % {'content': content}

def renderKV15messages(dataownercode):
    messages = getMessages(dataownercode)

def renderLinePages(dataownercode):
    cache_lines = cacheLines(dataownercode)
    lines = getLines(date.today(), dataownercode)

    output = renderLines(dataownercode, cache_lines, lines.keys()) + """
<div class="alert alert-info">
    <p>
        Via deze pagina kun je direct een lijn kiezen en vrije tekst berichten naar haltes publiceren.
        Een lijn wordt gepresenteerd in een heen en terug richting.
        Door een of meerdere haltes aan te klikken maak je een selectie, op de selectie kan een "Nieuw Bericht" worden gepubliceerd.
        In dit nieuwe scherm geef je het type bericht aan, schrijf je het bericht en selecteer je de begin en eind tijd.
    </p>
    <p>
        Naast direct publiceren kun je in dit scherm ook een scenario naam opgeven.
        Op deze manier wordt het bericht niet gepubliceerd, maar alleen opgeslagen.
        Wil je het bericht later gebruiken, ga je naar het berichten overzicht.
    </p>
</div>
<div class="alert alert-warning">
    <i>De lijnvolgorde kan niet altijd correct worden bepaald aan de hand van de gepubliceerde dienstregeling.</i>
</div>
"""
    f = open('tmp/lijnen.html', 'w')
    f.write(templateLijnen(output))
    f.close()

    for lineplanningnumber, data in lines.items():
        lineid = dataownercode + '_' + lineplanningnumber
        output = renderLines(dataownercode, cache_lines, lines.keys(), lineid)
        output += ("""
<div class="row">
    <div class="span9">
        <h4>%(transporttype)s %(linepublicnumber)s</h3>
        <h5>%(linename)s</h4>
    </div>
</div>
<div class="row" style="margin: 0 auto; width: 50%%;">
%(aligned)s
</div>""" % data)
        f = open("tmp/lijnen-%s.html"%(lineid), "w")
        f.write(templateLijnen(output))
        f.close()

def notfound(start_response):
    start_response('404 File Not Found', COMMON_HEADERS_TEXT + [('Content-length', '13')])
    yield 'Niet gevonden'

def badrequest(start_response, error):
    start_response('400 Bad Request', COMMON_HEADERS_TEXT + [('Content-length', str(len(error)))])
    yield error

def forbidden(start_response, error):
    start_response('403 Forbidden', COMMON_HEADERS_TEXT + [('Content-length', str(len(error)))])
    yield error

def authenticate(start_response):
    start_response('401 Unauthorized', COMMON_HEADERS_TEXT + [('Content-length', '19'), ('WWW-Authenticate', 'Basic realm="openebs.nl"')])
    yield 'Niet geauthoriseerd'

#def signout(start_response):
#    reply = '<html><head><meta http-equiv="refresh" content="1; URL=https://www.openebs.nl/"></head><body>U bent uitgelogd</body></html>'
#    start_response('401 Logout', COMMON_HEADERS_HTML + [('Content-length', str(len(reply))), ('WWW-Authenticate', 'Invalidate, Basic realm="logout"')])
#    yield reply

stopinline_cache = {}

def openebs(environ, start_response):
    url = environ['PATH_INFO']
    dataownercode = None

#    if url == '/uitloggen':
#    	return signout(start_response)

    if 'REMOTE_USER' not in environ and 'HTTP_AUTHORIZATION' not in environ:
        return authenticate(start_response)

    if 'REMOTE_USER' not in environ and 'HTTP_AUTHORIZATION' in environ:
        import base64
        environ['REMOTE_USER'], _pass = base64.decodestring(environ['HTTP_AUTHORIZATION'].split('Basic ')[1]).split(':', 2)

    try:
        username, domain = environ['REMOTE_USER'].split('@')
        dataownercode = auth_lookup[domain.lower()]
    except:
        return notfound(start_response)
    author = environ['REMOTE_USER']
    auth_author = {'scenario_create': False, 'scenario_delete': False}
    if author in authorization:
        auth_author = authorization[author]

    if url == '/stops/line':
        reply = querylinesperstop(dataownercode)
        start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
        return reply
    elif '/stops/line/' in url:
        arguments = url.split('/')
        # temp fix, while waiting for linedirection in KV7network, query will be fast enough then
        key = dataownercode+'_'+arguments[3]
        if key in stopinline_cache:
            reply = stopinline_cache[key]
        else:
            reply = querystopinline(dataownercode,arguments[3])
            stopinline_cache[key] = reply
        start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
        return reply
    
    elif url == '/line':
        reply = querylines(dataownercode)
        start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
        return reply

    elif url == '/update':
        renderLinePages(dataownercode)

    elif url == '/berichten.html':
        renderKV15messages(dataownercode)

    elif url == '/settings.js':
        reply = json.dumps(dict(auth_author.items() + [('username', author)]))

        start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
        return reply

    elif url == '/KV15scenarios':
         if environ['REQUEST_METHOD'] == 'GET':
            reply = StopMessage().overview_scenario(dataownercode)
            start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
            return reply
         elif environ['REQUEST_METHOD'] == 'POST':
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env, keep_blank_values=False)
            scenarioname = None
            scenariostarttime = None
            scenarioendtime = None

            if 'scenarioname' not in post:
                return badrequest(start_response, 'Kan geen scenario plannen zonder ScenarioName')

            if 'scenariostarttime' in post:
                try:
                    scenariostarttime = datetime.strptime(post['scenariostarttime'].value, '%Y-%m-%dT%H:%M:%S')
                    if scenariostarttime > (datetime.now() + timedelta(hours=72)):
                        return badrequest(start_response, 'ScenarioStartTime kan niet 72 uur in de toekomst liggen')                    
                except:
                    return badrequest(start_response, 'ScenarioStartTime kan niet worden gevalideerd')
            else:
                return badrequest(start_response, 'Kan geen scenario plannen zonder ScenarioStartTime')
            
            if 'scenarioendtime' in post:
                try:
                    scenarioendtime = datetime.strptime(post['scenarioendtime'].value, '%Y-%m-%dT%H:%M:%S')
                except:
                    return badrequest(start_response, 'ScenarioEndTime kan niet worden gevalideerd')
            else:
                return badrequest(start_response, 'Kan geen scenario plannen zonder ScenarioEndTime')

            if scenariostarttime >= scenarioendtime:
                return badrequest(start_response, 'ScenarioStartTime later of gelijk aan ScenarioEndTime')

            return badrequest(start_response, 'Je hebt alles goed ingevuld, maar dit stukje moeten we nog implementeren.')         

    elif url.startswith('/KV15scenarios/'):
         if environ['REQUEST_METHOD'] == 'GET':
            scenario = url.split('/KV15scenarios/')[1]
            reply = StopMessage().overview_scenario(dataownercode, scenario)
            start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
            return reply
    
    elif url == '/KV15deletescenarios':
         if environ['REQUEST_METHOD'] == 'POST':
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env, keep_blank_values=False)

            if 'scenario_delete' in auth_author and auth_author['scenario_delete']:
                if 'scenarioname' not in post:
                    return badrequest(start_response, 'Geen scenario opgestuurd')

                StopMessage().delete_scenario(dataownercode, post['scenarioname'].value)
                reply = 'OK'
                start_response('200 OK', COMMON_HEADERS_HTML + [('Content-length', str(len(str(reply)))),])
                return reply
            else:
                return badrequest(start_response, 'U heeft geen rechten om een scenario te verwijderen')

    elif url == '/KV15deletemessages':
         if environ['REQUEST_METHOD'] == 'POST':
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env, keep_blank_values=False)
            messagecodedate = None
            messagecodenumber = None
            if 'messagecodedate' not in post:
                return badrequest(start_response, 'Geen messagecodedate ingevuld')
            else:
                messagecodedate = post['messagecodedate'].value

            if 'messagecodenumber' not in post:
                return badrequest(start_response, 'Geen messagecodenumber ingevuld')
            else:
                try:
                    messagecodenumber = int(post['messagecodenumber'].value)
                except:
                    return badrequest(start_response,'Messagecodenumber geen integer')
            msg = DeleteMessage(dataownercode=dataownercode, messagecodedate=messagecodedate, messagecodenumber=messagecodenumber)
            kv15 = KV15messages(stopmessages = [msg])

            conn = psycopg2.connect(kv15_database_connect)
            kv15.save(conn=conn)
            kv15.log(conn=conn,author=author,message='DELETE')
            respcode, resp = kv15.push(remote, remote_path)
            if not send or '>OK</' in resp:
                conn.commit()
                conn.close()
            else:
                conn.rollback()
                conn.close()
                regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>",re.MULTILINE|re.LOCALE|re.DOTALL)
                r = regex.search(resp)
                resp = r.groups()[0]
                return badrequest(start_response,resp)
            reply = 'Bericht verwijderd'
            start_response('200 OK', COMMON_HEADERS_TEXT + [('Content-length', str(len(reply))),])
            return reply
            

    elif url == '/KV15messages':
        if environ['REQUEST_METHOD'] == 'GET':
            reply = StopMessage().overview(dataownercode)
            start_response('200 OK', COMMON_HEADERS_JSON + [('Content-length', str(len(str(reply)))),])
            return reply

        elif environ['REQUEST_METHOD'] == 'POST':
            kv15 = None
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env, keep_blank_values=False)
            userstopcodes = None
            if 'userstopcodes[]' in post:
                try:
                    if isinstance(post['userstopcodes[]'],list):
                        userstopcodes = [x.value.split('_')[1] for x in post['userstopcodes[]']]
                        for x in post['userstopcodes[]']:
                            if x.value.split('_')[0] != dataownercode:
                                return badrequest(start_response, 'Userstopcodes buiten dataowner domein')
                    else:
                        userstopcodes = [str(post['userstopcodes[]'].value).split('_')[1]]
                        if str(post['userstopcodes[]'].value).split('_')[0] != dataownercode:
                            return badrequest(start_response, 'Userstopcode buiten dataowner domein')
                except Exception as e:
                    print e
                    return badrequest(start_response, 'Fout in UserStopCodes formaat')
            else:
                if 'userstopcodes[]' not in post:
                    return badrequest(start_response, 'UserStopCodes ontbreken')

            if 'messagecontent' not in post:
                return badrequest(start_response, 'Bericht ontbreekt')

            msg = StopMessage(dataownercode=dataownercode, userstopcodes=userstopcodes, messagecontent=post['messagecontent'].value)
            if 'messagepriority' in post:
                if MessagePriority().validate(post['messagepriority'].value):
                    msg.messagepriority = post['messagepriority'].value
                else:
                    return badrequest(start_response, 'MessagePriority kan niet worden gevalideerd')

            if 'messagetype' in post:
                if MessageType().validate(post['messagetype'].value):
                    msg.messagetype = post['messagetype'].value
                else:
                    return badrequest(start_response, 'MessageType kan niet worden gevalideerd')

            if 'messagestarttime' in post:
                try:
                    msg.messagestarttime = datetime.strptime(post['messagestarttime'].value, '%Y-%m-%dT%H:%M:%S')
                    if msg.messagestarttime > (datetime.now() + timedelta(hours=72)):
                        return badrequest(start_response, 'MessageStartTime kan niet 72 uur in de toekomst liggen')                    
                except:
                    return badrequest(start_response, 'MessageStartTime kan niet worden gevalideerd')
            
            if 'messageendtime' in post:
                try:
                    msg.messageendtime = datetime.strptime(post['messageendtime'].value, '%Y-%m-%dT%H:%M:%S')
                except:
                    return badrequest(start_response, 'MessageEndTime kan niet worden gevalideerd')

            if msg.messagestarttime >= msg.messageendtime:
                return badrequest(start_response, 'MessageStartTime later of gelijk aan MessageEndTime')

            kv15 = KV15messages(stopmessages = [msg])

            if 'messagescenario' in post:
                if 'scenario_create' in auth_author and auth_author['scenario_create']:
                    if len(post['messagescenario'].value) > 0:
                        conn = psycopg2.connect(kv15_database_connect)
                        kv15.save(conn=conn, messagescenario=post['messagescenario'].value)
                        conn.commit()
                        conn.close()
                    else:
                        return badrequest(start_response, 'MessageScenario kan niet worden gevalideerd')            
                else:
                    return forbidden(start_response, 'U heeft geen rechten om een scenario te maken')
            else:     
                conn = psycopg2.connect(kv15_database_connect)
                kv15.save(conn=conn)
                kv15.log(conn=conn,author=author,message='PUBLISH')
                respcode,resp = kv15.push(remote, remote_path)
                if not send or '>OK</' in resp:
                    conn.commit()
                    conn.close()
                else:
                    conn.rollback()
                    conn.close()
                    regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>",re.MULTILINE|re.LOCALE|re.DOTALL)
                    r = regex.search(resp)
                    resp = r.groups()[0]
                    return badrequest(start_response,resp)
            reply = 'Bericht verstuurd'
            start_response('200 OK', COMMON_HEADERS_TEXT + [('Content-length', str(len(reply)))])
            return reply
    return notfound(start_response)

uwsgi.applications = {'': openebs}
