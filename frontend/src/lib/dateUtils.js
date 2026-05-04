/**
 * Date utilities for Dubai timezone (UTC+4)
 */

const DUBAI_TZ = 'Asia/Dubai';

/**
 * Format date/time in Dubai timezone
 * @param {string|Date} dateString - ISO date string or Date object
 * @param {string} format - 'date' | 'time' | 'datetime'
 * @returns {string} Formatted date/time in Dubai timezone
 */
export function formatInDubaiTz(dateString, format = 'datetime') {
  if (!dateString) return '-';

  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;

  const options = {
    timeZone: DUBAI_TZ,
  };

  switch (format) {
    case 'date':
      return date.toLocaleDateString('en-AE', {
        ...options,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });

    case 'time':
      return date.toLocaleTimeString('en-AE', {
        ...options,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      });

    case 'datetime':
      return date.toLocaleString('en-AE', {
        ...options,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      });

    default:
      return date.toLocaleString('en-AE', options);
  }
}

/**
 * Get current time in Dubai
 * @returns {Date}
 */
export function getNowInDubai() {
  const formatter = new Intl.DateTimeFormat('en-AE', {
    timeZone: DUBAI_TZ,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  const parts = formatter.formatToParts(new Date());
  const values = {};
  parts.forEach(({ type, value }) => {
    values[type] = value;
  });

  return new Date(
    `${values.year}-${values.month}-${values.day}T${values.hour}:${values.minute}:${values.second}`
  );
}
