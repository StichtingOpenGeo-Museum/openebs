/* Copyright (c) 2006-2013 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

/**
 * @requires OpenLayers/Strategy.js
 */

/**
 * Class: OpenLayers.Strategy.OVCluster
 * Strategy for clustering stops, based on name and selected state.
 *
 * Inherits from:
 *  - <OpenLayers.Strategy>
 *  - <OpenLayers.Strategy.Cluster>
 */
OpenLayers.Strategy.OVCluster = OpenLayers.Class(OpenLayers.Strategy.Cluster, {

    /**
     * Method: addToCluster
     * Add a feature to a cluster.
     *
     * Parameters:
     * cluster - {<OpenLayers.Feature.Vector>} A cluster.
     * feature - {<OpenLayers.Feature.Vector>} A feature.
     */
    addToCluster: function(cluster, feature) {
        cluster.cluster.push(feature);
        cluster.attributes.count += 1;
    },

    /**
     * Method: shouldCluster
     * Determine whether to include a feature in a given cluster.
     *
     * Parameters:
     * cluster - {<OpenLayers.Feature.Vector>} A cluster.
     * feature - {<OpenLayers.Feature.Vector>} A feature.
     *
     * Returns:
     * {Boolean} The feature should be included in the cluster.
     */
    shouldCluster: function(cluster, feature) {
        if (cluster.cluster[0].attributes.name != feature.attributes.name || cluster.cluster[0].renderIntent != feature.renderIntent){
            return false;
        }
        var cc = cluster.geometry.getBounds().getCenterLonLat();
        var fc = feature.geometry.getBounds().getCenterLonLat();
        var distance = (
            Math.sqrt(
                Math.pow((cc.lon - fc.lon), 2) + Math.pow((cc.lat - fc.lat), 2)
            ) / this.resolution
        );
        return (distance <= this.distance);
    },

    /**
     * Method: createCluster
     * Given a feature, create a cluster.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     *
     * Returns:
     * {<OpenLayers.Feature.Vector>} A cluster.
     */
    createCluster: function(feature) {
        var center = feature.geometry.getBounds().getCenterLonLat();
        var cluster = new OpenLayers.Feature.Vector(
            new OpenLayers.Geometry.Point(center.lon, center.lat),
            {count: 1}
        );
        cluster.cluster = [feature];
        cluster.renderIntent = feature.renderIntent;
        return cluster;
    },

    /**
     * Method: recluster
     * User-callable function to recluster features
     * Useful for instances where a clustering attribute (distance, threshold, ...)
     *     has changed
     */
    recluster: function(){
        var event={"recluster":true};
        this.cluster(event);
    },

    
    /**
     * Method: cluster
     * Cluster features based on some threshold distance.
     *
     * Parameters:
     * event - {Object} The event received when cluster is called as a
     * result of a moveend event.
     */
     cluster: function(event) {
        if((!event || event.zoomChanged) && this.features) {
            var resolution = this.layer.map.getResolution();
            if(resolution != this.resolution || !this.clustersExist()) {
                this.resolution = resolution;
                var clusters = [];
                var feature, clustered, cluster;
                for(var i=0; i<this.features.length; ++i) {
                    feature = this.features[i];
                    if(feature.geometry) {
                        clustered = false;
                        for(var j=clusters.length-1; j>=0; --j) {
                            cluster = clusters[j];
                            if(this.shouldCluster(cluster, feature)) {
                                this.addToCluster(cluster, feature);
                                clustered = true;
                                break;
                            }
                        }
                        if(!clustered) {
                            clusters.push(this.createCluster(this.features[i]));
                        }
                    }
                }
                this.clustering = true;
                this.layer.removeAllFeatures();
                this.clustering = false;
                if(clusters.length > 0) {
                    if(this.threshold > 1) {
                        var clone = clusters.slice();
                        clusters = [];
                        var candidate;
                        for(var i=0, len=clone.length; i<len; ++i) {
                            candidate = clone[i];
                            if(candidate.attributes.count < this.threshold) {
                                Array.prototype.push.apply(clusters, candidate.cluster);
                            } else {
                                clusters.push(candidate);
                            }
                        }
                    }
                    this.clustering = true;
                    // A legitimate feature addition could occur during this
                    // addFeatures call. For clustering to behave well, features
                    // should be removed from a layer before requesting a new batch.
                    this.layer.addFeatures(clusters);
                    this.clustering = false;
                }
                this.clusters = clusters;
            }
        }
    },

    CLASS_NAME: "OpenLayers.Strategy.OVCluster" 
});
