// JavaScript component (ES6 style) to be imported and used in a web app
// Assumes Chart.js is available globally or imported elsewhere

export function renderCpChartFromJson(jsonData, canvasElementId) {
  const nodes = jsonData.nodes || [];

  const cappedData = nodes.map(node => ({
    index: node.index,
    cp: Math.max(-3300, Math.min(3300, node.cp))
  }));

  const ctx = document.getElementById(canvasElementId).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: cappedData.map(d => d.index),
      datasets: [{
        label: 'Centipawn Evaluation',
        data: cappedData.map(d => d.cp),
        borderWidth: 2,
        borderColor: 'blue',
        fill: false,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          min: -3500,
          max: 3500,
          title: {
            display: true,
            text: 'Centipawn Score'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Move Index'
          }
        }
      },
      plugins: {
        title: {
          display: true,
          text: 'CP Evaluation per Move (Capped at ±3300)'
        }
      }
    }
  });
}
