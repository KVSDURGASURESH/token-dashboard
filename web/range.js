// range.js — the shared 7d/30d/90d/All time-range tabs, driven by ?range= in the hash.

import { readHashParam, writeHashParam } from '/web/app.js';

export const RANGES = [
  { key: '7d',  label: '7d',  days: 7 },
  { key: '30d', label: '30d', days: 30 },
  { key: '90d', label: '90d', days: 90 },
  { key: 'all', label: 'All', days: null },
];

const DEFAULT_RANGE = RANGES[1]; // 30d

export function readRange() {
  const key = readHashParam('range');
  return RANGES.find(r => r.key === key) || DEFAULT_RANGE;
}

export function sinceIso(range) {
  if (!range.days) return null;
  return new Date(Date.now() - range.days * 86400 * 1000).toISOString();
}

export function withSince(url, since) {
  if (!since) return url;
  return url + (url.includes('?') ? '&' : '?') + 'since=' + encodeURIComponent(since);
}

export function rangeTabs(active) {
  return `
    <div class="range-tabs" role="tablist">
      ${RANGES.map(r => `<button data-range="${r.key}" class="${r.key === active.key ? 'active' : ''}">${r.label}</button>`).join('')}
    </div>`;
}

// Call after the tabs are in the DOM — switching range re-renders via hashchange.
export function bindRangeTabs(root) {
  root.querySelectorAll('.range-tabs button[data-range]').forEach(btn => {
    btn.addEventListener('click', () => writeHashParam('range', btn.dataset.range));
  });
}
