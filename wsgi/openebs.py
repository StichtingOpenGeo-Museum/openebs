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
    start_response('404 File Not Found', COMMON_HEADERS + [('Content-length', '12')])
    yield '<notfound />'

def badrequest(start_response):
    start_response('400 Bad Request', COMMON_HEADERS + [('Content-length', '14')])
    yield '<badrequest />'

def openebs(environ, start_response):
    url = environ['PATH_INFO'][1:]
    dataownercode = None
    try:
        username, domain = environ['REMOTE_USER'].split('@')
        dataownercode = authlookup[domain.lower()]
    except:
        return notfound(start_response)

    if url == '/update':
        renderLinePages(dataownercode)

    elif url == '/berichten.html':
        renderKV15messages(dataownercode)

    elif url == '/KV15messages':
        if environ['REQUEST_METHOD'] == 'GET':
            renderMessagePage(dataownercode)

        elif environ['REQUEST_METHOD'] == 'POST':
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            post = cgi.FieldStorage(fp=env['wsgi.input'], environ=post_env, keep_blank_values=False)

            if 'userstopcodes' in post and messagecontent in post:
                try:
                    [int(x) for x in post['userstopcodes']]
                except:
                    return badrequest(start_reponse)
            else:
                return badrequest(start_response)

            msg = StopMessage(dataownercode=dataowner, userstopcodes=post['userstopcodes'], messagecontent=post['messagecontent'])

            if 'messagepriority' in post:
                if MessagePriority().validate(post['messagepriority']):
                    msg.messagepriority = post['messagepriority']
                else:
                    return badrequest(start_response)

            if 'messagetype' in post:
                if MessageType().validate(post['messagetype']):
                    msg.messagetype = post['messagetype']
                else:
                    return badrequest(start_response)

            if 'messagestarttime' in post:
                try:
                    msg.messagestarttime = datetime.strptime(post['messagestarttime'], '%Y-%m-%dT%H:%M:%S')
                except:
                    return badrequest(start_reponse)
            
            if 'messageendtime' in post:
                try:
                    msg.messageendtime = datetime.strptime(post['messageendtime'], '%Y-%m-%dT%H:%M:%S')
                except:
                    return badrequest(start_reponse)

            kv15 = KV15messages(stopmessages = [msg])

            if 'messagescenario' in post:
                if len(post['messagescenario']) > 0:
                    kv15.store(post['messagescenario'])
                else:
                    return badrequest(start_reponse)
            
            else:     
                kv15.push(remote, '/TMI_Post/KV15')

