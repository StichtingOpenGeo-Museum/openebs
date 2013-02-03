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

$( '#stopBasket' ).on( 'keydown', function( event ) {
    if (event.keyCode != 46 || $('#stopBasket').children().length <= 1){
        return;
    }
    var item = $(this).children("option").filter(":selected");
    var feature = getStopFeature(item[0].id);
    if (feature){
        feature.renderIntent = "default";
        var cluster = getStopCluster(item[0].id);
        if (cluster){
            cluster.renderIntent = "default";
        }
        vectors.refresh();
    }
    item.remove();
});

function datetimetoxml(datetime) {
    var arr = datetime.split(' ');
    date_parts = arr[0].split('-');
    return [date_parts[2], date_parts[1], date_parts[0]].join('-') + 'T' + arr[1];
}

var berichten = null;

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
}

function updateBerichten() {
    $.getJSON('/KV15messages', function(data) {
        berichten = {};
        $.each(data, function(key, n) {
            berichten[[n['dataownercode'], n['messagecodedate'], n['messagecodenumber']].join('_')] = n;

            if (n['isactive']) {
                $.each(n['userstopcodes'], function(key2, m) {
                    var stop = $('#'+n['dataownercode']+'_'+m);
                    if (stop !== undefined && !stop.hasClass('btn-warning')) {
                        stop.removeClass('btn-primary');
                        stop.addClass('btn-warning');
                    }
                });
            }
        });

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
            return '<tr class="'+trclass+'"><td>'+([n['messagestarttime'].replace(' ', '<br/>'), n['messageendtime'].replace(' ','<br/>'), '<a href="#" onclick="haltesBericht('+key+');">'+n['userstopcodes'].length+'</a>', n['messagecontent'], action].join('</td><td>'))+'</td></tr>';
        });

        mytable = '<tr><th style="width: 4em;">Begintijd</th><th style="width: 4em;">Eindtijd</th><th style="width: 4em;">Haltes</th><th>Bericht</th><th style="width: 30px;"></th></tr>'+(trs.join());
        $('#berichten tbody').replaceWith(mytable);
    });
}

var scenario = null;

function updateScenario() {
    $.getJSON('/KV15scenarios', function(data) {
        scenario = {};
        $.each(data, function(key, n) {
            scenario[n['messagescenario']] = n;
        });

        trs = $.map(data, function(n, i) {
            var key = n['messagescenario'];
            var action = '';
            if (authorization['scenario_create'] === true) {
                action  = '<button class="btn btn-danger btn-mini" onclick="kv15deletescenario('+key+')" style="float: right;"><i class="icon-trash icon-white"></i></button>';
            }
            action += ' <button class="btn btn-success btn-mini" onclick="kv15scenario('+key+')" style="float: right;"><i class="icon-play icon-white"></i></button>';

            return '<tr><td>'+([n['messagescenario'], '<a href="#" onclick="haltesBericht('+key+');">'+n['userstopcodes'].length+'</a>', action].join('</td><td>'))+'</td></tr>';
        });

        mytable = '<tr><th style="width: 6em;">Scenario</th><th style="width: 4em;">Haltes</th><th style="width: 30px;"></th></tr>'+(trs.join());
        $('#scenario tbody').replaceWith(mytable);
    });
}

window.setInterval(updateBerichten,30000);

function kv15deletemessage(dataownercode, messagecodedate, messagecodenumber) {
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

function kv15submit() {
    $("#nieuwBerichtModalAlert").removeClass('alert alert-error');
    $("#nieuwBerichtModalAlert").html('');
    var post = {
        "userstopcodes": userStopCodesInBasket(),
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
    .done(function () { $('#nieuwBerichtModal').modal('hide'); updateBerichten();})
    .fail(function (data) {
        $("#nieuwBerichtModalAlert").replaceWith('<div id="nieuwBerichtModalAlert" class="alert alert-error"><b>Waarschuwing</b> Publiceren is niet gelukt.<br />'+data.responseText+'</div>');
    });
}

function herplanBericht(dataownercode, messagecodedate, messagecodenumber) {
    var id = [dataownercode, messagecodedate, messagecodenumber].join('_');
    if (id in berichten) {
        haltesBericht(dataownercode, messagecodedate, messagecodenumber);
        for (var i = 0; i < vectors.features.length; i++) {
            selectCtrl.select(vectors.features[i]);
        }

        var bericht = berichten[id];
        $('#messagecontent').text(bericht['messagecontent']);
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


