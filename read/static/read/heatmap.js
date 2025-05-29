document.addEventListener("DOMContentLoaded", function () {
  let cal = new CalHeatmap();
  let currentStartDate = new Date();
  let currentMonthsToShow = 14; // Default value

  // Initial render
  renderHeatmap();

  // Navigation controls
  document.getElementById("prev-btn").addEventListener("click", function () {
    cal.previous();
  });

  document.getElementById("next-btn").addEventListener("click", function () {
    cal.next();
  });

  document.getElementById("today-btn").addEventListener("click", function () {
    currentStartDate = new Date();
    cal.destroy();
    renderHeatmap();
  });

  // Responsive handling with debounce
  let resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      cal.destroy();
      renderHeatmap();
    }, 100);
  });

  function calculateMonthsToShow() {
    const screenWidth = window.innerWidth;
    if (screenWidth < 768) {
      return 6; // Show 6 months on mobile
    } else if (screenWidth < 1024) {
      return 9; // Show 9 months on tablet
    }
    return 14; // Default to 14 months on desktop
  }

  async function renderHeatmap() {
    // debugger;
    const container = document.getElementById("heatmap-container");
    const response = await fetch(container.dataset.heatmapUrl);
    let data = await response.json();
    console.log(data);

    currentMonthsToShow = calculateMonthsToShow();
    const startDate = new Date(currentStartDate);
    startDate.setMonth(startDate.getMonth() - currentMonthsToShow + 1);

    // data = [
    //   { date: "2025-03-30", value: 3 },
    //   { date: "2025-03-29", value: 6 },
    // ];

    const options = {
      data: {
        source: data,
        type: "json",
        x: "date",
        y: "value",
      },
      date: {
        start: startDate,
      },
      range: currentMonthsToShow,
      scale: {
        color: {
          type: "threshold",
          range: ["#14432a", "#166b34", "#37a446", "#4dd05a"],
          domain: [10, 20, 30],
        },
      },
      domain: {
        type: "month",
        gutter: 4,
        label: {
          text: "MMM",
          textAlign: "start",
          position: "top",
          offset: { x: 10, y: 5 },
        },
      },
      subDomain: {
        type: "ghDay",
        radius: 2,
        width: 11,
        height: 11,
        gutter: 4,
      },
      itemSelector: "#cal-heatmap",
    };

    const plugIns = [
      [
        Tooltip,
        {
          text: function (date, value, dayjsDate) {
            return (
              (value ? value + "°C" : "No data") +
              " on " +
              dayjsDate.format("LL")
            );
          },
        },
      ],
    ];

    cal.paint(options, plugIns);
  }
});
