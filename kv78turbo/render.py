from datetime import date
from operator import itemgetter
from cgi import escape
from kv78turbo.database import connect

def getLines(dataownercode):
    cur = connect()

    output = {}
    cur.execute("select distinct transporttype from line where dataownercode = %s", (dataownercode,) )
    transporttypes = cur.fetchall()
    for transporttype in transporttypes:
        transporttype = transporttype[0]
        cur.execute("select distinct linepublicnumber, linename, lineplanningnumber from line where dataownercode = %s and transporttype = %s order by linepublicnumber", (dataownercode, transporttype,) )
        lines = cur.fetchall()

        lines_final = []
        for line in lines:
            try:
                lines_final.append((int(line[0]),line[1],line[2]))
            except:
                lines_final.append((line[0],line[1],line[2]))
            
        output[transporttype] = sorted(lines_final, key=itemgetter(0))
        
    return output


def renderpills(dataownercode):
    lines = getLines(dataownercode)
    output = """<ul class="nav nav-pills">"""
    for transporttype in lines.keys():
        output += ''.join(["""<li><a class="ebs-tt-%s" href='#%s_%s' title="%s">%s</a></li>"""%(transporttype, dataownercode, x[2], escape(x[1]), x[0]) for x in lines[transporttype]])
    output += "</ul>"
    print output

def renderLines(dataownercode, lines=None, only=None, active=None):
    if lines is None:
        lines = getLines(dataownercode)
    output = ""
    for transporttype in lines.keys():
        output += '<div class="btn-toolbar" id="lijnen"><div class="btn-group">'
        for x in lines[transporttype]:
            if only is None or x[2] in only:
                extra_class = ""
                lineid = dataownercode + '_' + x[2]
                if active == lineid:
                    extra_class = " active"
                output += """<button class="btn fw%s" title="%s" id="%s">%s</button>"""%(extra_class, escape(x[1]),lineid,x[0])
        output += '</div></div>'
    return output
