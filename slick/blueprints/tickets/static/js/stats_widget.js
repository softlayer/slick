google.load('visualization', '1.0', {'packages':['corechart']});
google.setOnLoadCallback(drawChart);

function drawChart() {
    var data = google.visualization.arrayToDataTable(ticketStatsData);

    var options = {
        'title': 'Open Tickets - ' + ticketTotal,
	legend: {position: 'bottom'},
};
    
    var ticketChart = new google.visualization.PieChart(document.getElementById('ticket-widget-stats'));
    ticketChart.draw(data, options);
    google.visualization.events.addListener(ticketChart, 'select', ticketRedirect);

    function ticketRedirect(e) {
	window.location.href = "/tickets";
    }
}

