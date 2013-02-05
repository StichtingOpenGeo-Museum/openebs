import psycopg2
import psycopg2.extras
import operator
import codecs

def exists(list,key,value):
    for row in list:
        if key in row and row[key] == value:
            return True
    return False

def position(list,key,value):
    i = 0
    for row in list:
        if key in row and row[key] == value:
            return i
        i += 1
    return -1

def order(list):
    for s in list: 
        if s['linkorder'] == 1:
            pos = position(list,'userstopcodeend',s['userstopcodebegin'])
            for x in list:
                if set(x['patterncodes']) == set(s['patterncodes']):
                    x['linkorder'] += pos
    list.sort(key=operator.itemgetter('linkorder'))
    for i in range(len(list)):
        s = list[i]
        pos = position(list[i:],'userstopcodeend',s['userstopcodebegin'])
        if pos != -1 and i+1 != pos:
            print i,pos
            print s

def stopline(heen,weer,namekey_heen,codekey_heen,namekey_weer=None,codekey_weer=None):
    if namekey_weer is None:
        namekey_weer = namekey_heen
    if codekey_weer is None:
        codekey_weer = codekey_heen
    if heen is not None and weer is not None:
        return '<tr><td class="left"><button type="button" data-toggle="button" onClick="patternSelectStop(this)" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode1)s">%(name1)s</button></td><td><button class="btn btn-success btn-mini" onclick="patternSelectRow(this);"><i class="icon-resize-horizontal icon-white"></i></td><td class="right"><button type="button" data-toggle="button" onClick="patternSelectStop(this)" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode2)s">%(name2)s</button></td></tr>\n' % {'userstopcode1' : heen['dataownercode']+'_'+heen[codekey_heen], 'name1': heen[namekey_heen], 'userstopcode2' : weer['dataownercode']+'_'+weer[codekey_weer], 'name2' : weer[namekey_weer]}
    elif heen is not None and weer is None:
        return '<tr><td class="left"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" onClick="patternSelectStop(this)" id="%(userstopcode1)s">%(name1)s</button></td><td></td><td></td></tr>\n'%{'userstopcode1' : heen['dataownercode']+'_'+heen[codekey_heen], 'name1' : heen[namekey_heen]}
    elif heen is None and weer is not None:
        return '<tr><td></td><td></td><td class="right"><button type="button" data-toggle="button" class-toggle="btn-success" onClick="patternSelectStop(this)" class="btn btn-primary btn-mini" id="%(userstopcode2)s">%(name2)s</button></td></tr>\n'%{'userstopcode2' : weer['dataownercode']+'_'+weer[codekey_weer], 'name2' : weer[namekey_weer]}

def stopkey(row,stopkey):
    return row['dataownercode'] + '|' + row[stopkey]

def stoparea_equals(stoparea1,stoparea2):
    if stoparea1 is None or stoparea2 is None:
        return False
    return (stoparea1 == stoparea2)

def patternize(dataownercode):
    dummies = set([])
    stoparea = {}
    conn = psycopg2.connect("dbname='kv1%s'" % dataownercode.lower())
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("select dataownercode||'|'||userstopcode as dummy from usrstop where getin = false and getout = false")
    for row in cur:
        dummies.add(row['dummy'])
    cur.execute("select dataownercode||'|'||userstopcode as id,userstopareacode from usrstop")
    for row in cur:
        stoparea[row['id']] = row['userstopareacode'] 
    cur.execute("""
SELECT
j.direction,
jt.dataownercode,
j.lineplanningnumber,
userstopcodebegin,u1.name as namebegin,
userstopcodeend, u2.name as nameend,
cast(max(timinglinkorder) as integer) as linkorder,
array_agg(distinct destcode) as destcodes,
array_agg(distinct jt.journeypatterncode) as patterncodes
from jopa as j, jopatili as jt,usrstop as u1, usrstop as u2
where
j.version = jt.version AND
j.dataownercode = jt.dataownercode AND
j.lineplanningnumber = jt.lineplanningnumber AND
j.journeypatterncode = jt.journeypatterncode AND
userstopcodebegin <> userstopcodeend AND
jt.version = u1.version AND
jt.version = u2.version AND
jt.dataownercode = u1.dataownercode AND
jt.dataownercode = u2.dataownercode AND
jt.userstopcodebegin = u1.userstopcode AND
jt.userstopcodeend = u2.userstopcode AND
jt.version in (select version from version where current_date >= validfrom and current_date <= validthru)
group by j.lineplanningnumber,j.direction,jt.dataownercode,userstopcodebegin,u1.name,userstopcodeend,u2.name
order by lineplanningnumber,direction,linkorder""")
    pattern = {}
    for row in cur.fetchall():
        key = '_'.join([row['dataownercode'],row['lineplanningnumber']])
        if key not in pattern:
            pattern[key] = {row['direction'] : []}
        if row['direction'] not in pattern[key]:
            pattern[key][row['direction']] = []
        pattern[key][row['direction']].append(row)
    for key,item in pattern.items():
        f = open(key+'.html','w')
        f.write('<table class="lijn"><tr><th class="left"><button class="btn btn-success btn-mini" onclick="patternSelect(0);"><i class="icon-arrow-down icon-white"></i></th><th><button class="btn btn-success btn-mini" onclick="patternSelect(2);"><i class="icon-resize-horizontal icon-white"></i></th><th class="right"><button class="btn btn-success btn-mini" onclick="patternSelect(1);"><i class="icon-arrow-up icon-white"></i></th></tr>')
        if 2 not in item:
            order(item[1])
            for stop in item[1]:
                if stopkey(stop,'userstopcodebegin') not in dummies:
                    f.write(stopline(stop,None,'namebegin','userstopcodebegin'))
            f.write(stopline(stop,None,'nameend','userstopcodeend'))
            continue
        if 1 not in item:
            order(item[2])
            for stop in reversed(item[2]):
                if stopkey(stop,'userstopcodeend') not in dummies:
                    f.write(stopline(stop,None,'nameend','userstopcodeend'))
            f.write(stopline(stop,None,'namebegin','userstopcodebegin'))
            continue
        order(item[1])
        order(item[2])
        item[2] = list(reversed(item[2])) #userstopcodebegin/end wordt niet! omgedraaid.
        i,j = 0,0
        while i <= len(item[1]) and j <= len(item[2]):
            if i < len(item[1]) and stopkey(item[1][i],'userstopcodebegin') in dummies:
                i += 1
            if j < len(item[2]) and stopkey(item[2][j],'userstopcodeend') in dummies:
                j += 1
            inlen = (i < len(item[1]) and j < len(item[2]))
            if i < len(item[1]) or j < len(item[2]):
                if inlen:
                    stopkey_heen = stopkey(item[1][i],'userstopcodebegin')
                    stoparea_heen = stoparea[stopkey_heen]
                    stopkey_weer = stopkey(item[2][j],'userstopcodeend')
                    stoparea_weer = stoparea[stopkey_weer]
                if inlen and (item[1][i]['namebegin'] == item[2][j]['nameend'] or stoparea_equals(stoparea_heen,stoparea_weer)): #Haltenamen gelijk
                    f.write(stopline(item[1][i],item[2][j],'namebegin','userstopcodebegin',namekey_weer='nameend',codekey_weer='userstopcodeend'))
                    i += 1
                    j += 1
                elif not inlen and i < len(item[1]): #Een van de patronen is afgewerkt
                    if stopkey(item[1][i],'userstopcodebegin') not in dummies:
                        f.write(stopline(item[1][i],None,'namebegin','userstopcodebegin'))
                    i += 1
                elif not inlen and j < len(item[2]):
                    if stopkey(item[2][j],'userstopcodeend') not in dummies:
                        f.write(stopline(None,item[2][j],'nameend','userstopcodeend'))
                    j += 1
                else:
                    pos = position(item[2][j:],'nameend',item[1][i]['namebegin'])
                    if i == len(item[1]) -1 or j == len(item[2]) - 1:
                        pos = max(pos,position(item[2][j:],'namebegin',item[1][i]['nameend']))
                    if pos == -1: #Heen bevat dit patroon niet, print halte in heen patroon
                        if stopkey(item[2][j],'userstopcodeend') not in dummies:
                            f.write(stopline(item[1][i],None,'namebegin','userstopcodebegin'))
                        i += 1
                    else:    #Weer bevat dit patroon niet, print halte in weer patroon
                        if stopkey(item[2][j],'userstopcodeend') not in dummies:
                            f.write(stopline(None,item[2][j],'nameend','userstopcodeend'))
                        j += 1

            if i == len(item[1]) or j == len(item[2]): #niet elif want je wilt in de loop al einde kunnen afhandelen
               if i == len(item[1]) and j == len(item[2]): #case beide patronen zijn aan laatste toe
                   i += 1
                   j += 1
                   if item[1][-1]['nameend'] == item[2][-1]['namebegin']:
                       f.write(stopline(item[1][-1],item[2][-1],'nameend','userstopcodeend',namekey_weer='namebegin',codekey_weer='userstopcodebegin'))
                   else:
                       f.write(stopline(item[1][-1],None,'nameend','userstopcodeend'))
                       f.write(stopline(None,item[2][-1],'namebegin','userstopcodebegin'))
               elif i == len(item[1]):
                   f.write(stopline(item[1][-1],None,'nameend','userstopcodeend'))
                   i += 1
               elif j == len(item[1]):
                   f.write(stopline(None,item[2][-1],'namebegin','userstopcodebegin'))
                   j += 1
        f.write('</table>')
        f.close()
patternize('SYNTUS')
patternize('HTM')
patternize('VTN')
patternize('ARR')
patternize('GVB')
patternize('EBS')
