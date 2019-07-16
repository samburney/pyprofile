google.charts.load('current', { packages: ['corechart'] });
google.charts.setOnLoadCallback(drawChart);

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)", "i"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Distance');
    data.addColumn('number', 'Elevation');

    var options = {
        //interpolateNulls: true,
        hAxis: {
            title: 'Distance',
            format: '#,###.## km'
        },
        vAxis: {
            title: 'Elevation',
            format: '#,###.## m'
        },
        series: {
            0: {
                color: 'green',
                lineWidth: '1',
                visibleInLegend: false,
                type: 'area'
            },
        },
        explorer: {
            actions: [
                'dragToZoom',
                'rightClickToReset'
            ],
            axis: 'horizontal',
            keepInBounds: true,
            maxZoomOut: 1,
            maxZoomIn: 0.01,
        },
    };

    var chart = new google.visualization.ComboChart(document.getElementById('chart'));

    // Get data
    var url = api_base + '/profile';
    var postdata = {
        'backend': backend,
        'srid': srid,
        'lat1': lat1,
        'lng1': lng1,
        'lat2': lat2,
        'lng2': lng2,
        'sample_dist': sample_dist,
    }
    $.post(
        url,
        postdata,
        function(result) {
            if (result.status == 'OK') {
                var distances = result.data.coordinate_distances;
                var coordinates = result.data.geojson.coordinates

                $.each(coordinates, function(iter, coordinate){
                    data.addRow([parseFloat(distances[iter]), parseFloat(coordinate[2])]);
                });
            }

            chart.draw(data, options);
        },
        'json'
    )
}
