function featuresToUserStopCodes() {
    return $.map(vectors.selectedFeatures, function(n, i) {
        if (n.cluster) {
            return  $.map(n.cluster, function(n, i) {
                return n.attributes.key; 
            });
        }
        return n.attributes.key;
    });
}

function datetimetoxml(datetime) {
    var arr = datetime.split(' ');
    date_parts = arr[0].split('-');
    return [date_parts[2], date_parts[1], date_parts[0]].join('-') + 'T' + arr[1];
}

var berichten = null;

function haltesBericht(id) {
    if (id in berichten) {
        vectors.removeAllFeatures();
        var haltes = $.map(berichten[id]['userstopcodes'], function(n, i) {
            return berichten[id]['dataownercode'] + '_' + n;
        });

/*
 *      TODO: ik wil hier alle haltes zien, maar de bericht haltes geselecteerd
 *
        vectors.addFeatures(stops_features);


        $.each(vectors.features, function(feature) {
            if ($.inArray(feature.fid, haltes) >= 0) {
                selectCtrl.select(feature);
            }
        });*/

        var filtered_stops = $.map(stops_features, function(n, i) {
            if ($.inArray(n.fid, haltes) >= 0) {
                return n;
            }
        });

        vectors.addFeatures(filtered_stops);
    }
}

function updateBerichten() {
    $.getJSON('/KV15messages', function(data) {
        berichten = {};
        $.each(data, function(key, n) {
            berichten[[n['dataownercode'], n['messagecodedate'], n['messagecodenumber']].join('_')] = n;
        });

        tds = $.map(data, function(n, i) {
            return '<td>'+([n['messagestarttime'].replace(' ', '<br/>'), n['messageendtime'].replace(' ','<br/>'), n['messagecontent'], '<a href="#" onclick="haltesBericht(\''+[n['dataownercode'], n['messagecodedate'], n['messagecodenumber']].join('_')+'\');">'+n['userstopcodes'].length+'</a>'].join('</td><td>'))+'</td><td><button class="btn btn-success btn-mini" onclick=""><i class="icon-refresh icon-white"></i></button> <button class="btn btn-danger btn-mini" onclick="" style="float: right;"><i class="icon-trash icon-white"></i></button></td>';
        });

        mytable = '<tr><th>Begintijd</th><th>Eindtijd</th><th>Bericht</th><th>Aantal haltes</th><th></th></tr><tr>'+(tds.join('</tr><tr>'))+'</tr>';
        $('#berichten tbody').replaceWith(mytable);
    });
}

window.setInterval(updateBerichten,30000);

function kv15submit() {
    $("#nieuwBerichtModalAlert").removeClass('alert alert-error');
    $("#nieuwBerichtModalAlert").html('');
    var post = {
        "userstopcodes": featuresToUserStopCodes(),
        "messagepriority": $('button[name="messagepriority"].active').val(),
        "messagetype": $('button[name="messagetype"].active').val(),
        "messagecontent": $('#messagecontent').val()
    }

    
    var messagescenario = $('#messagescenario').val();
    if (messagescenario != '') {
        post['messagescenario'] = messagescenario;
    } else {
        post['messagestarttime'] = datetimetoxml($('#messagestarttime').val());
        post['messageendtime'] = datetimetoxml($('#messageendtime').val());
    }
    $.ajax({type: "POST", url: "/KV15messages", data: post, dataType: "html"})
    .done(function () { $('#nieuwBerichtModal').modal('hide'); })
    .fail(function (data) {
        $("#nieuwBerichtModalAlert").replaceWith('<div id="nieuwBerichtModalAlert" class="alert alert-error"><b>Waarschuwing</b> Publiceren is niet gelukt.<br />'+data.responseText+'</div>');
    });
}
