import { api, fmt, agentBadge } from '/web/app.js';

export default async function (root) {
  const [tips, rec] = await Promise.all([
    api('/api/tips'),
    api('/api/recommendations'),
  ]);
  root.innerHTML = `
    <div class="card">
      <h2>Suggestions</h2>
      ${tips.length === 0
        ? '<p class="muted">No suggestions right now. Token Dashboard surfaces patterns weekly — check back after more activity.</p>'
        : `<p class="muted" style="margin:-8px 0 14px">Rule-based pattern detection over the last 7 days. Dismissed tips re-appear after 14 days.</p>`}
      ${tips.map(t => `
        <div class="tip">
          <div class="tip-head">
            ${agentBadge(t.source)}
            <span class="badge">${fmt.htmlSafe(t.category)}</span>
            <strong>${fmt.htmlSafe(t.title)}</strong>
            <span class="spacer"></span>
            <button class="ghost" data-key="${fmt.htmlSafe(t.key)}">dismiss</button>
          </div>
          <p class="tip-body">${fmt.htmlSafe(t.body)}</p>
        </div>`).join('')}
    </div>
    ${rec.markdown ? `
    <div class="card" style="margin-top:16px">
      <h2>Draft CLAUDE.md Recommendations</h2>
      <p class="muted" style="margin:-8px 0 14px">Built from the suggestions above — nothing is written automatically. Review it, then merge whatever you agree with into your own <code>~/.claude/CLAUDE.md</code>.</p>
      <pre id="rec-md" style="white-space:pre-wrap;background:var(--panel-2);border:1px solid var(--border);border-radius:8px;padding:14px;font-size:12px;line-height:1.55">${fmt.htmlSafe(rec.markdown)}</pre>
      <button id="copy-rec" style="margin-top:10px">Copy to clipboard</button>
    </div>` : ''}
  `;
  root.querySelectorAll('button[data-key]').forEach(b => {
    b.addEventListener('click', async () => {
      await fetch('/api/tips/dismiss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: b.dataset.key }),
      });
      location.reload();
    });
  });
  const copyBtn = root.querySelector('#copy-rec');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      await navigator.clipboard.writeText(rec.markdown);
      copyBtn.textContent = 'Copied!';
      setTimeout(() => { copyBtn.textContent = 'Copy to clipboard'; }, 1500);
    });
  }
}
