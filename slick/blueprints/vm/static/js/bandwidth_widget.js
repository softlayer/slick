google.load('visualization', '1.0', {'packages':['corechart']});
google.setOnLoadCallback(drawChart);

function drawChart() {
    var data = google.visualization.arrayToDataTable(vmBandwidthData);
//    data.setColumnProperty(2, 'role', 'scope');

    var options = {
//	title: 'VM Bandwidth',
//	width:300,
//	height:225,
	hAxis: {title: 'Data Transferred (GB)'},
	chartArea: {top: 0, height: '80%'},
	legend: {position: 'bottom'},
	isStacked: true,
};
    
    var chart = new google.visualization.BarChart(document.getElementById('vm-widget-bandwidth'));
    chart.draw(data, options);
}

