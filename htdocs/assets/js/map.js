var map = null;
var selectCtrl = null;

var projection = new OpenLayers.Projection("EPSG:28992"); // Transform from WGS 1984

/* Reference: http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/openflights.js
 */
var vectors = new OpenLayers.Layer.Vector("Haltes",
{
 strategies: [new OpenLayers.Strategy.OVCluster({ distance: 15, threshold: 2 })],
 styleMap: new OpenLayers.StyleMap({
    "default": new OpenLayers.Style(OpenLayers.Util.applyDefaults({
        externalGraphic: 'assets/img/bus-12.png',
        graphicOpacity: 1,
        graphicHeight: 12,
        graphicWidth: 12,
        graphicTitle: "${name}",
        title: "${name}",
    }, OpenLayers.Feature.Vector.style["default"]), { context: { name: function(feature) { if(feature.cluster) { last = feature.cluster.length - 1; if(feature.cluster[0].attributes.name == feature.cluster[last].attributes.name) { feature.attributes.name = feature.cluster[0].attributes.name; } else { feature.attributes.name = ''; } } return feature.attributes.name; } } } ),
    "select": new OpenLayers.Style({
        externalGraphic: 'assets/img/bus-24-selected.png',
        graphicHeight: 24,
        graphicWidth: 24
    })})}
);



  
  
/*function(key, value) {
      markers[value.id] = L.marker([value.lat, value.lon], {icon: busIcon, id: value.id, active: false, title: value.name + ' ('+value.id+')'}).addTo(map).on("click", onClick);
          if (value.lineplanningnumber !== null) {
                  markers[value.id].setIcon(lineIcon);
                          markers[value.id]._icon.style['-webkit-filter'] = 'hue-rotate('+value.lineplanningnumber*35+'deg)';
                              }
                                });
                                });
*/

var stops = {};
var stops_features = [];
var line_stops_features = [];

function selectStop(feature) {
    if (feature.cluster){
        for (var i in feature.cluster){
            feature.cluster[i].renderIntent = feature.renderIntent;
        }
    }
    if ($("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").removeClass('disabled');
        $("#btnNieuwBericht").attr("data-toggle", "modal");
    }
}

function unselectStop(feature) {
    if (feature.cluster){
        for (var i in feature.cluster){
            feature.cluster[i].renderIntent = feature.renderIntent;
        }
    }
    if (vectors.selectedFeatures.length == 0 && !$("#btnNieuwBericht").hasClass('disabled')) {
        $("#btnNieuwBericht").addClass('disabled');
        $("#btnNieuwBericht").removeAttr("data-toggle");
        // berichten = null;
    }
}

function addStop(key, value) {
    var feature = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(value.x, value.y), {active: false, key: key, fid: key, name: value.name, lines: value.lines});
    feature.fid = key;
    stops_features.push(feature);
}

function showLine(lineid) {
    if (lineid === undefined) {
        vectors.removeAllFeatures();
        vectors.addFeatures(stops_features);
        unselectStop();
    } else {
    $('#lijnen').load('/assets/lines/'+lineid+'.html', function () {
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
    });
    $.getJSON('/stops/line/'+lineid.split('_')[1], function(data) {
        line_stops_features = [];
        $.each(data, function(key, value) {
            var feature = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(value.x, value.y), {active: false, key: key, name: value.name, lines: value.lines});
            line_stops_features.push(feature);
        });
        vectors.removeAllFeatures();
        vectors.addFeatures(line_stops_features);
        unselectStop();
/*        map.zoomToExtent(vectors.getDataExtent());*/
    } );

    }
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
        { onSelect: selectStop, onUnselect: unselectStop, multiple: true, toggle: true, box: false}
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
                        $("#lijnen-"+transporttype).append("<a class='btn' style='width: 1em;' onClick='showLine(\""+value.id+"\");' title='"+value.name+"'>"+value.linenr+"</a>");
                    });
                });
            });


    // center map
    if (!map.getCenter()) {
        map.setCenter(new OpenLayers.LonLat(x, y), zoom);
    }

}
