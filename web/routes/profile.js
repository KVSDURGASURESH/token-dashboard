import { api, fmt } from '/web/app.js';

const DIMENSIONS = [
  { key: 'steering',    label: 'Steering' },
  { key: 'execution',   label: 'Execution' },
  { key: 'engineering', label: 'Engineering' },
  { key: 'planning',    label: 'Planning' },
];

export default async function (root) {
  const profile = await api('/api/profile');

  if (profile.insufficient_data) {
    root.innerHTML = `
      <div class="card">
        <h2>Builder Profile</h2>
        <p class="muted">Not enough data yet — ${fmt.int(profile.turns)} of ${fmt.int(profile.minimum)} prompts needed. Keep using Claude Code and check back.</p>
      </div>`;
    return;
  }

  root.innerHTML = `
    <div class="card">
      <h2>Builder Profile</h2>
      <p class="muted" style="margin:-8px 0 4px">Archetype: <strong style="color:var(--accent)">${fmt.htmlSafe(profile.archetype)}</strong></p>
      <p class="muted" style="font-size:11px;margin:0 0 18px">Rule-based signals from your own session history — not a comparison to other users.</p>
      ${DIMENSIONS.map(d => `
        <div class="score-row">
          <span class="dim-label">${d.label}</span>
          <span class="score-bar-track"><span class="score-bar-fill" style="width:${profile.scores[d.key]}%"></span></span>
          <span class="dim-value">${fmt.int(profile.scores[d.key])}</span>
        </div>`).join('')}
    </div>`;
}
