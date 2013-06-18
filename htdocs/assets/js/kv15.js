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

function userStopCodesInBasket(){
   items = $("#stopBasket").children();
   stops = [];
   for (var i = 0; i < items.length; i++) {
       stops.push(items[i].id);
   }
   return stops;
};

function datetimetoxml(datetime) {
    var arr = datetime.split(' ');
    date_parts = arr[0].split('-');
    time_parts = arr[1].split(':');
    if (time_parts.length == 2){
        return [date_parts[2], date_parts[1], date_parts[0]].join('-') + 'T' + time_parts[0]+':'+time_parts[1]+':00';
    }else{
        return [date_parts[2], date_parts[1], date_parts[0]].join('-') + 'T' + arr[1];
    }
}

function haltesBericht(dataownercode, messagecodedate, messagecodenumber) {
    var id = [dataownercode, messagecodedate, messagecodenumber].join('_');
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
    $("#lijnenpanel a").removeClass("btn-success active");
}

function updateBerichten() {

    $.getJSON('/KV15messages', function(data) {
        berichten = {};
        var features = getFeaturesWithRenderIntent('messageactive');
        for (var i in features){
            features[i].renderIntent = 'default';
            features[i].attributes.name = features[i].data.name;
        }
        $.each(data, function(key, n) {
            berichten[[n['dataownercode'], n['messagecodedate'], n['messagecodenumber']].join('_')] = n;
            if (n['isactive']) {
                $.each(n['userstopcodes'], function(key2, m) {
                    var stop = $('#'+n['dataownercode']+'_'+m);
                    if (stop !== undefined && !stop.hasClass('btn-warning')) {
                        stop.removeClass('btn-primary active');
                        stop.addClass('btn-warning');
                    }
                    feature = getStopFeature(n['dataownercode']+'_'+m);
                    if (feature && feature.renderIntent != "messageactive"){
                        feature.renderIntent = "messageactive";
                        feature.attributes.messageactive = true;
                        feature.attributes.name += '\n[' + n['messagecontent'] +']';
                    }
                });
            }
        });
        refreshMap();
        trs = $.map(data, function(n, i) {
            var key = '\''+[n['dataownercode'], n['messagecodedate'], n['messagecodenumber']].join('\', \'')+'\'';
            var trclass = '';
            var action = '';
            if (n['isactive']) {
                trclass = 'success';
                action  = '<button class="btn btn-danger btn-mini" onclick="kv15deletemessage('+key+')" style="float: right;"><i class="icon-trash icon-white"></i></button>';
            } else {
                trclass = '';
                action  = '<button class="btn btn-success btn-mini" onclick="herplanBericht('+key+');" style="float: right;"><i class="icon-refresh icon-white"></i></button>';
            }
            // console.log(n);
            return '<tr class="'+trclass+'"><td>'+([n['messagestarttime'].replace(' ', '<br/>'), n['messageendtime'].replace(' ','<br/>'), '<a href="#" onclick="haltesBericht('+key+');">'+n['userstopcodes'].length+'</a>', n['messagecontent'], action].join('</td><td>'))+'</td></tr>';
        });

        mytable = '<tr><th style="width: 4em;">Begintijd</th><th style="width: 4em;">Eindtijd</th><th style="width: 4em;">Haltes</th><th>Bericht</th><th style="width: 30px;"></th></tr>'+(trs.join());
        $('#berichten tbody').replaceWith(mytable);
    });
}

function updateScenario() {
    $.getJSON('/KV15scenarios', function(data) {
        scenario = {};
        $.each(data, function(key, n) {
            scenario[n['messagescenario']] = n;
        });

        trs = $.map(data, function(n, i) {
            var key = "'"+n['messagescenario']+"'";
            var action = '';
            if (authorization['scenario_delete'] === true) {
                action  = '<button class="btn btn-danger btn-mini" onclick="kv15deletescenario('+key+')" style="float: right; margin-left: 2px;"><i class="icon-trash icon-white"></i></button>';
            }
            action += ' <button class="btn btn-success btn-mini disabled" onclick="kv15planning('+key+')" style="float: right; margin-right: 2px; margin-left: 2px;"><i class="icon-calendar icon-white"></i></button> <button class="btn btn-success btn-mini" onclick="kv15scenario('+key+')" style="float: right; margin-right: 2px; margin-left: 2px;"><i class="icon-play icon-white"></i></button>';

            return '<tr><td>'+([n['messagescenario'], '<a href="#" onclick="haltesBericht('+key+');">'+n['userstopcodes'].length+'</a>', action].join('</td><td>'))+'</td></tr>';
        });

        mytable = '<tr><th style="width: 6em;">Scenario</th><th style="width: 4em;">Haltes</th><th style="width: 30px;"></th></tr>'+(trs.join());
        $('#scenario tbody').replaceWith(mytable);
    });
}

function kv15deletescenario(scenarioname) {
    if (!confirmdelete || confirm('Weet u zeker dat u "'+scenarioname+'"wilt verwijderen?')) {
        var post = {
            "scenarioname": scenarioname
        }
        $.ajax({type: "POST", url: "/KV15deletescenarios", data: post, dataType: "html"})
        .done(function (data) {
            $("#scenarioAlert").removeClass('alert alert-error');
            $("#scenarioAlert").html('');
            updateScenario();
        })
        .fail(function (data) {
            $("#scenarioAlert").replaceWith('<div id="berichtenAlert" class="alert alert-error"><b>Waarschuwing</b> '+data.responseText+'</div>');
        });
     }
}

function kv15planning(scenario) {
    // $('#nieuwPlanningModal').modal('show');
}

function kv15scenario(scenario) {
    $('#scenarioname').attr('value', scenario);
    $.ajax({type: "GET", url: "/KV15scenarios/"+scenario, dataType: "json"})
	.done(function (data) {
        $("#scenarioBasket").empty();
        $.each(data['messages'], function (i, n) {
            var key = [n['messagecodedate'], n['messagecodenumber']].join('_');
            $("#scenarioBasket").append('<option id="'+key+'">'+n['messagecontent']+' ('+n['userstopcodes'].length+')</option>');
        });
        $('#nieuwScenarioModal').modal('show');
	});

}

function kv15deletemessage(dataownercode, messagecodedate, messagecodenumber) {
    var bericht = berichten[[dataownercode, messagecodedate, messagecodenumber].join('_')];
    if (bericht !== undefined) {
        bericht = ' "'+bericht['messagecontent']+'"';
    } else {
        bericht = '';
    }
    if (!confirmdelete || confirm('Weet u zeker dat u het bericht'+bericht+' wilt verwijderen?')) {
        var post = {
            "dataownercode": dataownercode,
            "messagecodedate": messagecodedate,
            "messagecodenumber": messagecodenumber
        }
        $.ajax({type: "POST", url: "/KV15deletemessages", data: post, dataType: "html"})
        .done(function () {
            $("#berichtenAlert").removeClass('alert alert-error');
            $("#berichtenAlert").html('');
            updateBerichten(); 
        })
        .fail(function (data) {
            $("#berichtenAlert").replaceWith('<div id="berichtenAlert" class="alert alert-error"><b>Waarschuwing</b> Verwijderen is niet gelukt.<br />'+data.responseText+'</div>');
        });
    }
}

function herplanBericht(dataownercode, messagecodedate, messagecodenumber) {
    var id = [dataownercode, messagecodedate, messagecodenumber].join('_');
    if (id in berichten) {
        $( '#btnLeegSelectie' ).click()
        haltesBericht(dataownercode, messagecodedate, messagecodenumber);
        for (var i = 0; i < vectors.features.length; i++) {
            selectCtrl.select(vectors.features[i]);
        }

        var bericht = berichten[id];
        $('#messagecontent').attr('value', bericht['messagecontent']);
        $('#messagecontent').keypress();
        $('#messagestarttime').attr('value', bericht['messagestarttime']);
        $('#messageendtime').attr('value', bericht['messageendtime']);
        $('button[name="messagepriority"][value="'+bericht['messagepriority']+'"]').click();
        $('button[name="messagetype"][value="'+bericht['messagetype']+'"]').click();
        $('#nieuwBerichtModalAlert').removeClass('alert alert-error');
        $('#nieuwBerichtModalAlert').html('');
        $('#nieuwBerichtModal').modal('show');
    }
}
