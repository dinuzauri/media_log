document.addEventListener("DOMContentLoaded", function () {
  // console.log("Starting Heatmap");

  const cal = new CalHeatmap();
  const data = [
    { date: "2025-02-01", value: 10 },
    { date: "2025-03-20", value: 10 },
    { date: "2025-03-21", value: 15 },
    { date: "2025-03-22", value: 20 },
    { date: "2025-03-23", value: 5 },
    { date: "2025-03-24", value: 30 },
    { date: "2025-03-25", value: 30 },
    { date: "2025-03-26", value: 100 },
    { date: "2025-03-27", value: 59 },
  ];
  const startDate= new Date();
  startDate.setFullYear(startDate.getFullYear()-1);
  // console.log(startDate)

  const options = {
    data: {
      source: data,
      type: "json",
      x: "date",
      y: "value",
    },
    date: {
      start: startDate
    },
    range: 13, // Show one year (12 months)
    scale: {
      color: {
        type: "threshold",
        range: ["#14432a", "#166b34", "#37a446", "#4dd05a"], // Adjust the colors
        domain: [10, 20, 30],
      },
    },
    domain: {
      type: "month",
      gutter: 4,
      label: { text: "MMM", textAlign: "start", position: "top" },
    },
    subDomain: {
      type: "ghDay", // GitHub-like day blocks
      radius: 2,
      width: 11,
      height: 11,
      gutter: 4,
    },
    itemSelector: "#cal-heatmap", // Selects where to render the heatmap
  };

  const plugIns=[
    [
      Tooltip,
      {
        text: function (date, value, dayjsDate) {
          return (
            (value ? value + '°C' : 'No data') + ' on ' + dayjsDate.format('LL')
          );
        },
      },
    ]];

  // console.log(options);
  cal.paint(options, plugIns);

  // console.log("Heatmap should now be painted");
});
