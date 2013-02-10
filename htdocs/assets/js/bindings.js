// Document ready, excute after succesful load.

$(document).ready(function() {
    $.ajaxSetup({cache:false});

    $.getJSON('/settings.js', function(auth) {
        authorization = auth;
        if (authorization['scenario_create'] === true) {
            $("#auth_messagescenario").attr('style', '');
        }
        $("#username").html(authorization['username']);
    });

    initopenlayers();
    updateBerichten();
    window.setInterval(updateBerichten,30000);

    $(".limit").limit({ maxChars: 255, warnChars: 78, counter: "#counter" });
    $(".limit").limit({ maxChars: 255, warnChars: 78, counter: "#scenariocounter" });


    $('#planningstarttime').timepicker({template: false, showSeconds: true, showMeridian: false, showInputs: true, minuteStep: 1});
    $('#planningendtime').timepicker({template: false, showSeconds: true, showMeridian: false, showInputs: true, minuteStep: 1});

    $('.btn-group > .btn, .btn[data-toggle="button"]').click(function() {
        if($(this).attr('class-toggle') != undefined && !$(this).hasClass('disabled')){
            var btnGroup = $(this).parent('.btn-group');

            if(btnGroup.attr('data-toggle') == 'buttons-radio') {
                btnGroup.find('.btn').each(function() {
                    $(this).removeClass($(this).attr('class-toggle'));
                });
                $(this).addClass($(this).attr('class-toggle'));
            }

            if(btnGroup.attr('data-toggle') == 'buttons-checkbox' || $(this).attr('data-toggle') == 'button') {
                if($(this).hasClass('active')) {
                    $(this).removeClass($(this).attr('class-toggle'));
                } else {
                    $(this).addClass($(this).attr('class-toggle'));
                }
            }
        }
    });
});

// Tabs
$('a[data-toggle="tab"]').on('show', function (e) {
    if ($(e.target).attr('href') == '#map') {
        $('#map').css('width', '100%');
    } else if ($(e.target).attr('href') == '#lijnen') {
        $('#map').css('width', ($(window).width() - $("#lijnen").width() + 15));
    } else {
        if ($(e.target).attr('href') == '#berichten') {
            updateBerichten();
        } else if ($(e.target).attr('href') == '#scenario') {
            updateScenario();
        }

        $('#map').css('width', '50%');
    }
});

$('a[data-toggle="tab"]#tab-lijnen').on('shown', function (e) {
    $('#map').css('width', ($(window).width() - $("#lijnen").width() + 15));
});


// Signout
$( '#username' ).on( 'click', function() {
    $.ajax({type: "GET", url: "https://uitloggen@openebs.nl", dataType: "html"})
    .fail(function (data) {
        document.location = 'https://google.com/';
    });
});

// Clears the selection from basket and map
$( '#btnLeegSelectie' ).on( 'click', function () {
    for (var i in vectors.features) {
        feature = vectors.features[i];
        if (feature.cluster) {
            for (var j in feature.cluster){
                if (feature.cluster[j].renderIntent == "select"){
                    feature.cluster[j].renderIntent = "default";
                }
            }
        } else if (feature.renderIntent == "select"){
            feature.renderIntent = "default";
        }
    }
    $(stopBasket).empty();
    $("#lijnen").find(".active").removeClass("btn-success active");
    refreshMap();
    $("#btnNieuwBericht").addClass('disabled');
    $("#btnLeegSelectie").addClass('disabled');
    $("#btnNieuwBericht").attr("data-toggle", "modal");
    return false;
});

// TODO: implement LineStopCancel
$( '#btnWijzigDienst' ).on( 'click', function () {
    return false;
});

// When the modal view is showed, the basket is updated
$('#nieuwBerichtModal').on('show', function () {
    var selectedFeatures = getSelectedFeatures();
    for (var i in selectedFeatures){
        var feature = selectedFeatures[i];
        $("#stopBasket").find("#"+feature.attributes.key).remove();
        $("#stopBasket").append('<option id="'+feature.attributes.key+'">'+feature.attributes.name+' ('+feature.attributes.key.split("_")[1] +')</option>');
    }
    updateBerichten();
});

$('#messagescenario').keyup(function() {
    if (this.value.length == 0) {
        $("#messagestarttime").removeAttr("disabled");
        $("#messageendtime").removeAttr("disabled");
        $("#messageSubmit").text('Publiceer');
    } else {
        $("#messagestarttime").attr("disabled", "disabled");
        $("#messageendtime").attr("disabled", "disabled");
        $("#messageSubmit").text('Opslaan');
    }
});

$( '#messageSubmit' ).on( 'click', function () {
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
    .done(function () {
        $("#nieuwBerichtModalAlert").removeClass('alert alert-error');
        $("#nieuwBerichtModalAlert").html('');
        $('#nieuwBerichtModal').modal('hide'); updateBerichten();
    })
    .fail(function (data) {
        $("#nieuwBerichtModalAlert").replaceWith('<div id="nieuwBerichtModalAlert" class="alert alert-error"><b>Waarschuwing</b> Publiceren is niet gelukt.<br />'+data.responseText+'</div>');
    });
});

// Enable deletion from the basket with selected stops by using delete or backspace
$( '#stopBasket' ).on( 'keydown', function( event ) {
    if (event.keyCode != 46 || event.keyCode != 8 || $('#stopBasket').children().length <= 1){
        return;
    }

    var item = $(this).children("option").filter(":selected");
    item.remove();

    var feature = getStopFeature(item.attr('id'));
    $("#lijnen").find('#'+item.attr('id')).removeClass("btn-success active");
    if (feature && feature.renderIntent == "select"){
        feature.renderIntent = "default";
        refreshMap();
    }
});

// Enable deletion from the basket with selected scenarios by using delete or backspace
$( '#scenarioBasket' ).on( 'keydown', function( event ) {
    if (event.keyCode != 46 || event.keyCode != 8 || $('#scenarioBasket').children().length <= 1){
        return;
    }
    var item = $(this).children("option").filter(":selected");
    item.remove();
});


$( '#scenarioSubmit' ).on( 'click', function () {
    var post = {
        "scenarioname": $('#scenarioname').val(),
        "scenariostarttime": datetimetoxml($('#scenariostarttime').val()),
        "scenarioendtime": datetimetoxml($('#scenarioendtime').val()),
        "messages": []
    }

    if ($('#scenariocontent').val() != '') {
        post["scenariocontent"] = $('#scenariocontent').val();
    }

    $.each($("#scenarioBasket").children(), function (i, n) {
        v = n.id.split('_');
        post['messages'].push({'messagecodedate': v[0], 'messagecodenumber': v[1]});
    });

    $.ajax({type: "POST", url: "/KV15scenarios", data: post, dataType: "html"})
    .done(function () {
        $("#nieuwScenarioModalAlert").removeClass('alert alert-error');
        $("#nieuwScenarioModalAlert").html('');
        updateBerichten();
        $('#nieuwScenarioModal').modal('hide');
    })
    .fail(function (data) {
        $("#nieuwScenarioModalAlert").replaceWith('<div id="nieuwScenarioModalAlert" class="alert alert-error"><b>Waarschuwing</b> Scenario publiceren is niet gelukt.<br />'+data.responseText+'</div>');
    });
});



