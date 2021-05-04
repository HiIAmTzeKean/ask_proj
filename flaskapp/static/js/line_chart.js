function drawOneLineChart(dateLabel_passed,aikidovalue_passed,line_data_passed) {
    var aikidovalue = aikidovalue_passed;
    var dateLabel=dateLabel_passed;
    var line_data=line_data_passed;

    var data = {
        type: 'line',
        labels: dateLabel,
        datasets: [{
            label: aikidovalue,
            borderJoinStyle: 'miter',
            pointBorderColor: "rgba(75,192,192,1)",
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(75,192,192,1)",
            pointHoverBorderColor: "rgba(220,220,220,1)",
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data: line_data,
            spanGaps: false,
            backgroundColor: ['green'],
        }]
    };
    var option = {
            responsive: true,
            legend: {
                display: false
                },
            scales: {
                xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            },
                        ticks: {
                            maxRotation: 90,
                            minRotation: 90
                        }
                        }],
                yAxes: [{
                        display: true,
                        ticks: {
                            suggestedMin: 1,
                            steps: 1,
                            stepValue: 1,
                            max: 10
                            }
                        }]
            },
            title: {
                display: true,
                text: aikidovalue,
            }
    };

    new Chart.Line(document.getElementById(aikidovalue).getContext("2d"), {data:data,options:option});
};
