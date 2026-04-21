/**
 * SmartZone-R - Utilities Module
 * Formatting, helpers, and DOM utilities
 */

/**
 * Format ISO timestamp for display
 * @param {string} iso - ISO timestamp string
 * @returns {string} Formatted timestamp
 */
export function formatTimestamp(iso) {
  if (!iso) return '';
  
  const date = new Date(iso);
  const opts = {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  };
  
  return date.toLocaleDateString('en-US', opts);
}

/**
 * Format zone number with leading zero
 * @param {number} zone - Zone number
 * @returns {string} Formatted zone (e.g., "Zone 03")
 */
export function formatZone(zone) {
  return `Zone ${String(zone).padStart(2, '0')}`;
}

/**
 * Get severity badge class from severity string
 * @param {string} severity - Severity level
 * @returns {string} CSS class name
 */
export function severityClass(severity) {
  return `badge badge-${severity}`;
}

/**
 * Get severity color from severity string
 * @param {string} severity - Severity level
 * @returns {string} Hex color
 */
export function severityColor(severity) {
  const colors = {
    critical: '#ff3333',
    high: '#ffaa00',
    medium: '#ff6600',
    normal: '#00ff88',
    okay: '#00ff88',
    warning: '#ffaa00',
    error: '#ff3333',
  };
  
  return colors[severity?.toLowerCase()] || '#8899aa';
}

/**
 * Determine metric status based on value and thresholds
 * @param {string} metric - Metric name
 * @param {number} value - Current value
 * @param {Object} thresholds - Threshold configuration
 * @returns {string} Severity level
 */
export function metricStatus(metric, value, thresholds = {}) {
  const defaults = {
    stress: { critical: 85, high: 70, medium: 50 },
    rubber_mm: { critical: 10, high: 5, medium: 2 },
    cracks_mm: { critical: 20, high: 10, medium: 5 },
    water_mm: { critical: 10, high: 5, medium: 2 },
    fod_weight_g: { critical: 100, high: 50, medium: 10 },
  };

  const limits = thresholds[metric] || defaults[metric] || defaults.stress;

  if (value >= limits.critical) return 'critical';
  if (value >= limits.high) return 'high';
  if (value >= limits.medium) return 'medium';
  return 'normal';
}

/**
 * Start a live clock in the specified element
 * @param {string} elementId - Element ID
 */
export function startClock(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;

  function update() {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
    
    const date = now.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
    });

    element.innerHTML = `<div class="time">${time}</div><div class="date">${date}</div>`;
  }

  update();
  setInterval(update, 1000);
}

/**
 * Format a number with commas
 * @param {number} n - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
export function formatNumber(n, decimals = 2) {
  if (n === undefined || n === null) return '';
  
  const parts = n.toFixed(decimals).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}

/**
 * Download data as CSV file
 * @param {Array} data - Array of objects
 * @param {string} filename - Output filename
 */
export function downloadCSV(data, filename = 'export.csv') {
  if (!data || data.length === 0) {
    showToast('No data to download', 'warning');
    return;
  }

  // Get headers
  const headers = Object.keys(data[0]);
  
  // Build CSV
  let csv = headers.join(',') + '\n';
  data.forEach(row => {
    csv += headers.map(h => {
      const val = row[h];
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
        return `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    }).join(',') + '\n';
  });

  // Download
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
  
  showToast(`Downloaded: ${filename}`, 'success');
}

/**
 * Show temporary toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, warning, error, info)
 * @param {number} duration - Duration in milliseconds
 */
export function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<p class="toast-message">${message}</p>`;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard', 'success');
    return true;
  } catch (err) {
    showToast('Failed to copy', 'error');
    return false;
  }
}

/**
 * Throttle function calls
 * @param {Function} fn - Function to throttle
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(fn, delay) {
  let lastCall = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return fn(...args);
    }
  };
}

/**
 * Debounce function calls
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(fn, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Parse URL query parameters
 * @returns {Object} Query parameters
 */
export function parseQueryParams() {
  const params = {};
  const searchParams = new URLSearchParams(window.location.search);
  
  for (const [key, value] of searchParams.entries()) {
    params[key] = value;
  }
  
  return params;
}

/**
 * Navigate to page with query parameter
 * @param {string} page - Page name (without .html)
 * @param {Object} params - Query parameters
 */
export function navigateTo(page, params = {}) {
  let url = `${page}.html`;
  
  if (Object.keys(params).length > 0) {
    const qs = new URLSearchParams(params).toString();
    url += `?${qs}`;
  }
  
  window.location.href = url;
}

/**
 * Animate counting up for a number
 * @param {string} elementId - Element ID
 * @param {number} target - Target number
 * @param {number} duration - Duration in milliseconds
 */
export function animateCounter(elementId, target, duration = 1000) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const start = 0;
  const frameDuration = 1000 / 60; // 60 fps
  const totalFrames = Math.round(duration / frameDuration);
  let currentFrame = 0;

  const counter = setInterval(() => {
    currentFrame++;
    const progress = currentFrame / totalFrames;
    const current = Math.floor(start + (target - start) * progress);
    
    element.textContent = formatNumber(current, 0);

    if (currentFrame >= totalFrames) {
      clearInterval(counter);
      element.textContent = formatNumber(target, 0);
    }
  }, frameDuration);
}

/**
 * Toggle element visibility
 * @param {string} elementId - Element ID
 */
export function toggleVisibility(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  element.classList.toggle('hidden');
}

/**
 * Add/remove class from element
 * @param {string} elementId - Element ID
 * @param {string} className - Class name
 * @param {boolean} add - Add or remove
 */
export function toggleClass(elementId, className, add = true) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  if (add) {
    element.classList.add(className);
  } else {
    element.classList.remove(className);
  }
}

export default {
  formatTimestamp,
  formatZone,
  severityClass,
  severityColor,
  metricStatus,
  startClock,
  formatNumber,
  downloadCSV,
  showToast,
  copyToClipboard,
  throttle,
  debounce,
  parseQueryParams,
  navigateTo,
  animateCounter,
  toggleVisibility,
  toggleClass,
};
