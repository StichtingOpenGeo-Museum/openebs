import helper
import uwsgi
import cgi
import datetime
from datetime import date
from kv78turbo.render import renderLines, getLines as cacheLines
from kv78turbo.journeypatternizer import getLines
from enum.messagepriority import MessagePriority
from enum.messagetype import MessageType
from enum.domain import auth_lookup
from settings.const import remote
from datetime import datetime
from kv15.stopmessage import StopMessage
from kv15.kv15messages import KV15messages

COMMON_HEADERS = [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]
COMMON_HEADERS_TEXT = [('Content-Type', 'text/plain'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]

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

def authenticate(start_response):
    start_response('401 Unauthorized', COMMON_HEADERS_TEXT + [('Content-length', '19'), ('WWW-Authenticate', 'Basic realm="openebs.nl"')])
    yield 'Niet geauthoriseerd'

def openebs(environ, start_response):
    url = environ['PATH_INFO']
    dataownercode = None

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

    if url == '/update':
        renderLinePages(dataownercode)

    elif url == '/berichten.html':
        renderKV15messages(dataownercode)

    elif url == '/KV15scenarios':
         if environ['REQUEST_METHOD'] == 'GET':
            reply = StopMessage().overview_scenario(dataownercode)
            start_response('200 OK', COMMON_HEADERS + [('Content-length', str(len(str(reply)))), ('Content-type', 'application/json')])
            return reply

    elif url == '/KV15messages':
        if environ['REQUEST_METHOD'] == 'GET':
            reply = StopMessage().overview(dataownercode)
            start_response('200 OK', COMMON_HEADERS + [('Content-length', str(len(str(reply)))), ('Content-type', 'application/json')])
            return reply

        elif environ['REQUEST_METHOD'] == 'POST':
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env, keep_blank_values=False)
            userstopcodes = None
            if 'userstopcodes[]' in post:
                try:
                    userstopcodes = [x.value.split('_')[1] for x in post['userstopcodes[]']]
                except:
                    return badrequest(start_response, 'Fout in UserStopCodes formaat')
                for x in post['userstopcodes[]']:
                    if x.value.split('_')[0] != dataownercode:
                        return badrequest(start_response, 'Userstopcodes buiten dataowner domein')
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
                except:
                    return badrequest(start_reponse, 'MessageStartTime kan niet worden gevalideerd')
            
            if 'messageendtime' in post:
                try:
                    msg.messageendtime = datetime.strptime(post['messageendtime'].value, '%Y-%m-%dT%H:%M:%S')
                except:
                    return badrequest(start_reponse, 'MessageEndTime kan niet worden gevalideerd')

            if msg.messagestarttime >= msg.messageendtime:
                return badrequest(start_response, 'MessageStartTime later of gelijk aan MessageEndTime')

            kv15 = KV15messages(stopmessages = [msg])

            if 'messagescenario' in post:
                if len(post['messagescenario']) > 0:
                    kv15.store(post['messagescenario'])
                else:
                    return badrequest(start_reponse, 'MessageScenario kan niet worden gevalideerd')
            
            else:     
                kv15.push(remote, '/TMI_Post/KV15')

    return notfound(start_response)

uwsgi.applications = {'': openebs}
