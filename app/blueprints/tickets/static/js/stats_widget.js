google.load('visualization', '1.0', {'packages':['corechart']});
google.setOnLoadCallback(drawChart);

function drawChart() {
    var data = google.visualization.arrayToDataTable(ticketStatsData);

    var options = {
//	title: 'VM Bandwidth',
//	width:250,
        'title': 'Open Tickets - ' + ticketTotal,
//	height:250,
//	hAxis: {title: 'Data Transferred (GB)'},
//	chartArea: {top: 0, height: '80%'},
	legend: {position: 'bottom'},
//	isStacked: true,
};
    
    var ticketChart = new google.visualization.PieChart(document.getElementById('ticket-widget-stats'));
    ticketChart.draw(data, options);
    google.visualization.events.addListener(ticketChart, 'select', ticketRedirect);

    function ticketRedirect(e) {
//	alert("CALLING!")
	window.location.href = "/tickets";
    }
}

