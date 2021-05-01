function drawRadarChart(radar_data_passed) {
     var radar_data = radar_data_passed
     const config = {
          type: 'radar',
          data: {
          labels: ['technique','ukemi','discipline','coordination','knowledge','spirit'],
          datasets: [{
               fillColor: "rgba(0,120,0,0.2)",
               strokeColor: "rgba(0,120,0,1)",
               pointColor: "rgba(10,10,10,1)",
               pointStrokeColor: "#ccc",
               pointHighlightFill: "#333",
               pointHighlightStroke: "rgba(255,255,0,1)",
               data: radar_data,
               pointLabelFontSize: 16,
               pointColor: "rgba(10,10,10,1)",
               }]
          },
          options: {
               responsive: true,
               maintainAspectRatio: false,
               pointDot: false,
               showTooltips: false,
               legend: {
                    display: false
                    },
     
               scale: {
                    ticks: {
                    beginAtZero: true,
                    max: 10,
                    min: 1,
                    stepSize: 1
                    },
               }
          }
     };

     var radar_chart = new Chart(document.getElementById('chart'), config);
   };
