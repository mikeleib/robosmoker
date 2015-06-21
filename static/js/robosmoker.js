function updatePit() {
    $.getJSON('BBQ/Status').done(function(data) {
	$("#pitTemp").text(data.pit);
	$("#goalTemp").text(data.goal);
	$("#fan").text(data.fan);
	console.log("data length: " + data.history.length);
	var temps = [];
	var goals = [];
	var fan = [];
	for (i = 0; i < data.history.length; i++) {
            temps.push([i, data.history[i].pit]);
            goals.push([i, data.history[i].goal]);
	    fan.push([i, data.history[i].airValue]);       
	}
	if (plot)
            plot.destroy();
        options.axes.xaxis.max = temps.length;
	plot = $.jqplot('chartdiv', [temps, goals, fan], options);
    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err )
    }).always(function() {
	setTimeout(updatePit, 3000);
	console.log('always')
    })
}

function loaded() {
    updatePit();
    options = {
	axes: {
	    yaxis: {
		min: 0
	    },
	    xaxis: {
		min: 0
	    }
	},
	seriesDefaults: {
	    showMarker: false
        }
    };
    plot = $.jqplot('chartdiv',  [[[]]], options);
    $("#tempClose").bind("click", function() {
	console.log("close clicked!");
        var value = parseInt($("#slider-1").val());
	console.log("value: " + value);
	var JSONObject = { "goal": value };
	var request = $.ajax({
	    url: 'BBQ/Status',
	    type: "PUT",
	    data: JSON.stringify(JSONObject),
	    dataType: "JSON",
	    complete: function(jqXHR, textStatus) {
		console.log("status: " + textStatus);
	    }});
    });
}

