/**
 * SmartZone-R - Charts Module
 * Chart.js wrapper functions for building airport-themed charts
 */

// Color palette matching new warm charcoal ATC aesthetic
const COLORS = {
  amber: '#c8a800',
  olive: '#7ab800',
  red: '#ff2200',
  orange: '#ff6600',
  teal: '#00aa88',
  critical: '#ff2200',
};

const ZONE_COLORS = [
  '#c8a800', // amber (Z1)
  '#7ab800', // olive (Z2)
  '#a09870', // warm grey (Z3)
  '#d4b857', // light amber (Z4)
  '#9aab00', // lime-olive (Z5)
  '#b8a800', // muted amber (Z6)
  '#6a9800', // muted olive (Z7)
  '#c09500', // dark amber (Z8)
  '#8aa000', // med olive (Z9)
  '#aa9800', // tan-amber (Z10)
];

// Chart.js configuration defaults
const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: 10,
  },
  plugins: {
    legend: {
      labels: {
        color: '#a09870',
        font: {
          family: "'B612 Mono', monospace",
          size: 11,
        },
      },
    },
    filler: {
      propagate: true,
    },
  },
  scales: {
    x: {
      grid: {
        color: '#2a2820',
        drawBorder: false,
      },
      ticks: {
        color: '#a09870',
        font: {
          family: "'B612 Mono', monospace",
          size: 10,
        },
        maxRotation: 45,
      },
    },
    y: {
      grid: {
        color: '#2a2820',
        drawBorder: false,
      },
      ticks: {
        color: '#a09870',
        font: {
          family: "'B612 Mono', monospace",
          size: 10,
        },
      },
    },
  },
};

/**
 * Build stress time series chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data from API
 */
export function buildStressTimeChart(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) {
    console.error(`Canvas element not found: ${canvasId}`);
    return null;
  }

  // Ensure we have datasets array
  if (!data.datasets) {
    data.datasets = [];
  }

  // Color datasets
  data.datasets = data.datasets.map((dataset, idx) => ({
    ...dataset,
    borderColor: ZONE_COLORS[idx % ZONE_COLORS.length],
    backgroundColor: `${ZONE_COLORS[idx % ZONE_COLORS.length]}20`,
    borderWidth: 2,
    pointRadius: 3,
    pointBackgroundColor: ZONE_COLORS[idx % ZONE_COLORS.length],
    fill: true,
    tension: 0.4,
  }));

  return new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      ...defaultOptions,
      plugins: {
        ...defaultOptions.plugins,
        tooltip: {
          backgroundColor: '#1a1a0e',
          borderColor: '#c8a800',
          borderWidth: 1,
          titleFont: {
            family: "'B612 Mono', monospace",
          },
          bodyFont: {
            family: "'B612 Mono', monospace",
          },
        },
      },
    },
  });
}

/**
 * Build rubber depth bar chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data
 */
export function buildRubberDepthChart(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (!data.datasets) data.datasets = [];

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Rubber Depth (mm)',
          data: data.data || [],
          backgroundColor: data.data?.map(val => {
            if (val > 5) return COLORS.critical;
            if (val > 3) return COLORS.amber;
            return COLORS.olive;
          }) || COLORS.amber,
          borderColor: COLORS.amber,
          borderWidth: 1,
        },
      ],
    },
    options: {
      ...defaultOptions,
      indexAxis: 'x',
      plugins: {
        ...defaultOptions.plugins,
        tooltip: {
          backgroundColor: '#1a1a0e',
          borderColor: '#c8a800',
          borderWidth: 1,
        },
      },
    },
  });
}

/**
 * Build alert severity pie chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data with critical, high, medium, normal counts
 */
export function buildAlertSeverityPie(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  const total = data.critical + data.high + data.medium + data.normal;

  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Normal'],
      datasets: [
        {
          data: [data.critical, data.high, data.medium, data.normal],
          backgroundColor: [COLORS.critical, COLORS.orange, COLORS.amber, COLORS.olive],
          borderColor: '#1a1a0e',
          borderWidth: 2,
        },
      ],
    },
    options: {
      ...defaultOptions,
      plugins: {
        ...defaultOptions.plugins,
        legend: {
          ...defaultOptions.plugins.legend,
          position: 'bottom',
        },
        tooltip: {
          backgroundColor: '#1a1a0e',
          borderColor: '#c8a800',
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const percent = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
              return `${label}: ${value} (${percent}%)`;
            },
          },
        },
      },
    },
  });
}

/**
 * Build FOD trend area chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Time series data
 */
export function buildFODTrendChart(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (!data.datasets) data.datasets = [];

  data.datasets = data.datasets.map(dataset => ({
    ...dataset,
    borderColor: COLORS.amber,
    backgroundColor: `${COLORS.amber}30`,
    borderWidth: 2,
    fill: true,
    tension: 0.4,
    pointRadius: 3,
    pointBackgroundColor: COLORS.amber,
  }));

  return new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      ...defaultOptions,
      plugins: {
        ...defaultOptions.plugins,
        filler: {
          propagate: true,
        },
      },
    },
  });
}

/**
 * Build aircraft impact bar chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data
 */
export function buildAircraftImpactChart(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Average Stress (%)',
          data: data.data || [],
          backgroundColor: COLORS.amber,
          borderColor: COLORS.amber,
          borderWidth: 1,
        },
      ],
    },
    options: {
      ...defaultOptions,
      indexAxis: 'y',
      plugins: {
        ...defaultOptions.plugins,
        tooltip: {
          backgroundColor: '#1a1a0e',
          borderColor: '#c8a800',
          borderWidth: 1,
        },
      },
    },
  });
}

/**
 * Build zone heatmap (custom)
 * Note: Chart.js doesn't have built-in heatmap, so we use a matrix chart
 * @param {string} containerId - Container div ID
 * @param {Object} data - Heatmap data with zones, metrics, and values
 */
export function buildZoneHeatmap(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container) return null;

  const { zones, metrics, data: heatmapData } = data;

  let html = '<table class="heatmap-table">';
  
  // Header row
  html += '<tr><th></th>';
  zones.forEach(zone => {
    html += `<th class="heatmap-zone-header">Zone ${String(zone).padStart(2, '0')}</th>`;
  });
  html += '</tr>';

  // Data rows
  heatmapData.forEach((row, metricIdx) => {
    html += `<tr><td class="heatmap-metric-label">${metrics[metricIdx]}</td>`;
    row.forEach(value => {
      const percent = value || 0;
      const color = getHeatmapColor(percent);
      html += `<td class="heatmap-cell" style="background-color: ${color};">${percent.toFixed(1)}</td>`;
    });
    html += '</tr>';
  });

  html += '</table>';
  container.innerHTML = html;
  return container;
}

/**
 * Get heatmap color based on risk percentage
 * @param {number} percent - Risk percentage (0-100)
 * @returns {string} Hex color
 */
function getHeatmapColor(percent) {
  if (percent >= 80) return COLORS.critical;
  if (percent >= 60) return COLORS.amber;
  if (percent >= 40) return COLORS.orange;
  if (percent >= 20) return COLORS.olive;
  return COLORS.teal;
}

/**
 * Build metric gauge (SVG-based)
 * @param {string} containerId - Container div ID
 * @param {number} value - Current value (0-100)
 * @param {string} label - Metric label
 * @param {string} unit - Unit of measurement
 */
export function buildMetricGauge(containerId, value, label, unit = '%') {
  const container = document.getElementById(containerId);
  if (!container) return null;

  const size = 140;
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  const color = value >= 80 ? COLORS.critical : value >= 60 ? COLORS.amber : COLORS.olive;

  const svg = `
    <svg width="${size}" height="${size / 2 + 30}" viewBox="0 0 140 100" class="gauge-svg">
      <!-- Background arc -->
      <circle cx="70" cy="70" r="${radius}" fill="none" stroke="#2a2820" stroke-width="8" stroke-dasharray="${circumference}" />
      
      <!-- Value arc -->
      <circle 
        cx="70" 
        cy="70" 
        r="${radius}" 
        fill="none" 
        stroke="${color}" 
        stroke-width="8" 
        stroke-dasharray="${circumference}" 
        stroke-dashoffset="${offset}"
        stroke-linecap="round"
        style="transform: rotate(-90deg); transform-origin: 70px 70px;"
      />
      
      <!-- Center text -->
      <text x="70" y="75" text-anchor="middle" font-size="24" font-weight="bold" fill="${color}" font-family="'B612 Mono', monospace">
        ${value.toFixed(0)}${unit}
      </text>
    </svg>
    <div class="gauge-label">${label}</div>
  `;

  container.innerHTML = svg;
  return container;
}

/**
 * Build alerts by zone bar chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data with labels and alert counts
 */
export function buildAlertsZoneChart(canvasId, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Alert Count',
          data: data.data || [],
          backgroundColor: ZONE_COLORS,
          borderColor: COLORS.amber,
          borderWidth: 2,
        },
      ],
    },
    options: {
      ...defaultOptions,
      indexAxis: 'y',
      plugins: {
        ...defaultOptions.plugins,
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1a1a0e',
          borderColor: '#c8a800',
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color: '#2a2820',
            drawBorder: true,
          },
          ticks: { color: '#a09870' },
        },
        y: {
          grid: { display: false },
          ticks: { color: '#c8a800' },
        },
      },
    },
  });
}

export default {
  buildStressTimeChart,
  buildRubberDepthChart,
  buildAlertSeverityPie,
  buildFODTrendChart,
  buildAircraftImpactChart,
  buildZoneHeatmap,
  buildMetricGauge,
  buildAlertsZoneChart,
};
