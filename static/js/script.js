// Renders every Plotly figure found in the page's <script id="charts-data"> JSON.
// Each figure key "foo" is drawn into the element with id="chart-foo".
document.addEventListener("DOMContentLoaded", function () {
  var holder = document.getElementById("charts-data");
  if (!holder || typeof Plotly === "undefined") { return; }
  var charts = JSON.parse(holder.textContent);
  Object.keys(charts).forEach(function (key) {
    var el = document.getElementById("chart-" + key);
    if (el) {
      Plotly.newPlot(el, charts[key].data, charts[key].layout,
                     { responsive: true, displayModeBar: false });
    }
  });
});
