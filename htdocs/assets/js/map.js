var map = null;
var selectCtrl = null;

var projection = new OpenLayers.Projection("EPSG:28992"); // Transform from WGS 1984
var cluster_strategy = new OpenLayers.Strategy.OVCluster({ distance: 15, threshold: 2 })
/* Reference: http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/openflights.js
 */
var vectors = new OpenLayers.Layer.Vector("Haltes",
{
 strategies: [cluster_strategy],
 styleMap: new OpenLayers.StyleMap({
    "default": new OpenLayers.Style(OpenLayers.Util.applyDefaults({
        externalGraphic: 'assets/img/kleinedris-12.png',
        graphicOpacity: 1,
        graphicHeight: 12,
        graphicWidth: 12,
        graphicTitle: "${name}",
        title: "${name}",
    }, OpenLayers.Feature.Vector.style["default"]), { context: { name: function(feature) { if(feature.cluster) { last = feature.cluster.length - 1; if(feature.cluster[0].attributes.name == feature.cluster[last].attributes.name) { feature.attributes.name = feature.cluster[0].attributes.name; } else { feature.attributes.name = ''; } } return feature.attributes.name; } } } ),
    "select": new OpenLayers.Style({
        externalGraphic: 'assets/img/kleinedris-24.png',
        graphicHeight: 24,
        graphicWidth: 24
    }),
    "messageactive": new OpenLayers.Style({
            externalGraphic: 'assets/img/kleinedrisbericht-12.png',
	            graphicHeight: 12,
		    graphicWidth : 12})
    })}
);
  
  
var stops = {};
var stops_features = [];
var line_stops_features = [];

function getStopFeature(stop_id){
   for (var i in vectors.features){
       feature = vectors.features[i];
       if (feature.cluster){
           for (var j in feature.cluster){
               if (feature.cluster[j].attributes.key == stop_id){
                   return feature.cluster[j];
               }
           }
       }else if (feature.attributes.key == stop_id){
           return feature;
       }
   }
   return null;
}

function getSelectedFeatures(){
   return getFeaturesWithRenderIntent("select");
}

function getFeaturesWithRenderIntent(renderintent){
   selected = [];
   for (var i in vectors.features){
       feature = vectors.features[i];
       if (feature.cluster){
           for (var j in feature.cluster){
               if (feature.cluster[j].renderIntent == renderintent){
                   selected.push(feature.cluster[j]);
               }
           }
       }else if (feature.renderIntent == renderintent){
           selected.push(feature);
       }
   }
   return selected
}


function refreshMap(){
    cluster_strategy.recluster();
}

function getStopCluster(stop_id){
   for (var i in vectors.features){
       feature = vectors.features[i];
       if (feature.cluster){
           for (var j in feature.cluster){
               if (feature.cluster[j].attributes.key == stop_id){
                   return feature;
               }
           }
       }else if (feature.attributes.key == stop_id){
           return feature;
       }
   }
   return null;
}

function selectStop(feature) {
    if (feature.attributes.messageactive == true){
        feature.renderIntent = 'messageactive';
        refreshMap();
        return;
    }
    if (feature.cluster){
        for (var i in feature.cluster){
            clust = feature.cluster[i];
            clust.renderIntent = feature.renderIntent;
            $("#stopBasket").find("#"+clust.attributes.key).remove();
            $("#stopBasket").append('<option id="'+clust.attributes.key+'">'+clust.data.name+' ('+clust.attributes.key.split("_")[1] +')</option>');
            var button = $("#lijnen").find('#'+clust.attributes.key)
            if (button){
                button.addClass("btn-success active");
            }
        }
    }else{
        $("#stopBasket").find("#"+feature.attributes.key).remove();
        var button = $("#lijnen").find('#'+feature.attributes.key);
        if (button){
           button.addClass("btn-success active");
        }
        $("#stopBasket").append('<option id="'+feature.attributes.key+'">'+feature.data.name+' ('+feature.attributes.key.split("_")[1] +')</option>');
    }
    if ($("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").removeClass('disabled');
        $("#btnLeegSelectie").removeClass('disabled');
        $("#btnNieuwBericht").attr("data-toggle", "modal");
    }
}

function unselectStop(feature) {
    if (feature && feature.cluster){
        for (var i in feature.cluster){
            feature.cluster[i].renderIntent = feature.renderIntent;
            $("#stopBasket").find("#"+feature.cluster[i].attributes.key).remove();
            $("#lijnen").find('#'+feature.cluster[i].attributes.key).removeClass("btn-success active");
        }
    }else if (feature){
        $("#stopBasket").find("#"+feature.attributes.key).remove();
        $("#lijnen").find('#'+feature.attributes.key).removeClass("btn-success active");
    }
    if ($("#stopBasket").children().length == 0 && !$("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").addClass('disabled');
        $("#btnLeegSelectie").addClass('disabled');
        $("#btnNieuwBericht").removeAttr("data-toggle");
        // berichten = null;
    }
}

function addStop(key, value) {
    var feature = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(value.x, value.y), {active: false, key: key, fid: key, name: value.name, lines: value.lines});
    feature.fid = key;
    stops_features.push(feature);
}

function patternSelectStop(element) {
    patternSelectStopEach(element);
    patternSelectStopFinal();
}

function patternSelectStopEach(element) {
    element = $(element);
    var id = element.attr('id');
    var feature = getStopFeature(id);
    if (element.hasClass('btn-success')){
        if (feature)
            feature.renderIntent = 'default';
        element.removeClass('btn-success');
        element.removeClass('active');
        element.addClass('btn-primary');
        $("#stopBasket").find("#"+id).remove();
    } else {
        $("#stopBasket").find("#"+id).remove();
        $("#stopBasket").append('<option id="'+id+'">'+element.text()+' ('+id.split("_")[1] +')</option>');
        if (feature)
            feature.renderIntent = 'select';
        element.addClass('btn-success');
        element.addClass('active');
    }
}

function patternSelectStopFinal() {
    if ($("#stopBasket").children().length == 0 && !$("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").addClass('disabled');
        $("#btnLeegSelectie").addClass('disabled');
        $("#btnNieuwBericht").removeAttr("data-toggle");
    } else if ($("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").removeClass('disabled');
        $("#btnLeegSelectie").removeClass('disabled');
        $("#btnNieuwBericht").attr("data-toggle", "modal");
    }
    refreshMap();
}

function patternSelectRow(element) {
    patternSelectStopEach($(element).parent().prev().find('.btn')[0]);
    patternSelectStopEach($(element).parent().next().find('.btn')[0]);
    patternSelectStopFinal();
}

function patternSelect(index) {
        var selector = '';
        if (index == 0) {
                selector = '.lijn .left > .btn-primary';
        } else if (index == 1) {
                selector = '.lijn .right > .btn-primary';
        } else {
                selector = '.lijn .btn-primary';
        }

        $.each($(selector), function (i, v) { patternSelectStopEach(v) });
        patternSelectStopFinal();
}

function showLine(target, lineid) {
    $("#lijnenpanel a").removeClass("btn-success active");
    $(target).addClass("btn-success active");

    $('#lijnen').load('/assets/lines/'+lineid+'.html', function (data) {
        /* TODO: deze code even abstract maken met showlines */
        for (var key in berichten) {
            n = berichten[key];
            if (n['isactive']) {
                $.each(n['userstopcodes'], function(key2, m) {
                    var stop = $('#'+n['dataownercode']+'_'+m);
                    if (stop !== undefined) {
                        stop.removeAttr("data-toggle");
                        stop.removeClass('btn-primary');
                        stop.addClass('btn-warning disabled');
                        stop.attr('title', n['messagecontent']);
                    }
                });
            }
        }
        $("#stopBasket").find("option").map(function () {
        var button = $("#lijnen").find('#'+this.id)[0];
        if (button){
            $(button).addClass('btn-success active');
        } 
        });
        $('#tab-lijnen').tab('show');
        $('#map').css('width', ($(window).width() - ($("#lijnen").width() + 15)));
    });

    $.getJSON('/stops/line/'+lineid.split('_')[1], function(data) {
        line_stops_features = [];
        $.each(data, function(key, value) {
            var feature = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(value.x, value.y), {active: false, key: key, name: value.name, lines: value.lines});
            if ($("#stopBasket").find('#'+key).length > 0){
                feature.renderIntent = "select";
            }
            line_stops_features.push(feature);
        });
        vectors.removeAllFeatures();
        vectors.addFeatures(line_stops_features);
        unselectStop();
/*      map.zoomToExtent(vectors.getDataExtent());*/
    });
}

// initialise the 'map' object
function initopenlayers() {
    // start position for the map (hardcoded here for simplicity)
    var x = 85000;
    var y = 452000;
    var zoom = 7;
 
    // complex object of type OpenLayers.Map
    var map_controls = [new OpenLayers.Control.Navigation(), new OpenLayers.Control.PanPanel(), new OpenLayers.Control.ZoomPanel(), new OpenLayers.Control.LayerSwitcher()];
 
   map = new OpenLayers.Map('map', {
        controls: map_controls,
        maxExtent: new OpenLayers.Bounds(-285401.92,22598.08,595401.9199999999,903401.9199999999),
        resolutions: [3440.64, 1720.32, 860.16, 430.08, 215.04, 107.52, 53.76,26.88, 13.44, 6.72, 3.36, 1.68, 0.84, 0.42, 0.21],
        units: 'm',
        numZoomLevels: 15,
        projection: projection
    });
 
    var brt = new OpenLayers.Layer.TMS( "BRT Achtergrondkaart","http://geodata.nationaalgeoregister.nl/tiles/service/tms/",
              {transitionEffect: 'resize',
               sphericalMercator: false,
               layername:'brtachtergrondkaart',
               type:'png8',
               'className':'olBackgroundLayer'});

    map.addLayers([brt, vectors]);

    selectCtrl = new OpenLayers.Control.SelectFeature(vectors, 
        { onSelect: selectStop, onUnselect: unselectStop, multiple: true, toggle: true, box: false, clickout: false}
    );

    map.addControl(selectCtrl);

    selectCtrl.activate();
             $.getJSON('/stops/line', function(data) {
                stops = data;
                stops_features = [];
                $.each(stops, addStop);
                vectors.addFeatures(stops_features);
            } );

            $.getJSON('/line', function(data) {
                $.each(data, function(transporttype, value) {
                    $("#lijnen-"+transporttype).empty();
                    $.each(value, function(key, value) {
                        $("#lijnen-"+transporttype).append("<a class='btn' style='width: 1em;' onClick='showLine(this, \""+value.id+"\");' title='"+value.name.replace('"', '&quot;').replace('<', '&gt;').replace('>', '&lt;').replace("'", "&#39;")+"'>"+value.linenr+"</a>");
                    });
                });
            });


    // center map
    if (!map.getCenter()) {
        map.setCenter(new OpenLayers.LonLat(x, y), zoom);
    }

}
