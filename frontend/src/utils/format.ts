export const formatCOP = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '$ 0';
  const numeric = typeof value === 'number' ? value : Number(String(value).replace(/[^0-9.-]/g, ''));
  const safe = Number.isFinite(numeric) ? numeric : 0;
  const formatter = new Intl.NumberFormat('es-CO', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  return `$ ${formatter.format(safe)}`;
};

export const formatKm = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '0.0';
  const numeric = typeof value === 'number' ? value : Number(String(value).replace(/[^0-9.-]/g, ''));
  const safe = Number.isFinite(numeric) ? numeric : 0;
  return safe.toFixed(1);
};

export const formatDateTime = (value: string | null | undefined): string => {
  if (!value) return 'N/A';
  const hasTimezone = /[zZ]|[+-]\d{2}:?\d{2}$/.test(value);
  const normalized = hasTimezone ? value : `${value}Z`;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return 'N/A';
  return date.toLocaleString('es-CO', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};
