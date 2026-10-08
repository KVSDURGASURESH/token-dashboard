import { api, fmt, agentBadges, seriesByAgent } from '/web/app.js';
import { stackedBarChart } from '/web/charts.js';
import { bindRangeTabs, rangeTabs, readRange, sinceIso, withSince } from '/web/range.js';

export default async function (root) {
  const range = readRange();
  const since = sinceIso(range);
  const skills = await api(withSince('/api/skills', since));

  const totalInvocations = skills.reduce((s, r) => s + r.invocations, 0);

  root.innerHTML = `
    <div class="flex" style="margin-bottom:14px">
      <h2 style="margin:0;font-size:16px;letter-spacing:-0.01em">Skills</h2>
      <span class="muted" style="font-size:12px">${range.days ? `last ${range.days} days` : 'all time'}</span>
      <div class="spacer"></div>
      ${rangeTabs(range)}
    </div>

    <div class="row cols-2">
      <div class="card kpi"><div class="label">Unique skills used</div><div class="value">${fmt.int(skills.length)}</div></div>
      <div class="card kpi"><div class="label">Total invocations</div><div class="value">${fmt.int(totalInvocations)}</div></div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Top skills (by invocations, split by agent)</h3>
      <div id="ch-skills" style="height:320px"></div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>All skills</h3>
      <p class="muted" style="margin:-4px 0 14px;font-size:12px">"Tokens per call" is the size of the skill's <code>SKILL.md</code> file — what the agent loads into context each time the skill is invoked (size measured from your Claude skills folder; shown "—" when unknown).</p>
      <table>
        <thead><tr>
          <th>skill</th>
          <th>agent (invocations)</th>
          <th class="num">invocations</th>
          <th class="num">tokens per call</th>
          <th class="num">sessions</th>
          <th>last used</th>
        </tr></thead>
        <tbody>
          ${skills.map(s => `
            <tr>
              <td><span class="badge">${fmt.htmlSafe(s.skill)}</span></td>
              <td>${agentBadges(s.by_agent, fmt.int)}</td>
              <td class="num">${fmt.int(s.invocations)}</td>
              <td class="num">${s.tokens_per_call == null ? '<span class="muted">—</span>' : fmt.int(s.tokens_per_call)}</td>
              <td class="num">${fmt.int(s.sessions)}</td>
              <td class="mono">${fmt.ts(s.last_used)}</td>
            </tr>`).join('') || '<tr><td colspan="6" class="muted">no skills invoked in this range</td></tr>'}
        </tbody>
      </table>
    </div>
  `;

  bindRangeTabs(root);

  const top = skills.slice(0, 12);
  stackedBarChart(document.getElementById('ch-skills'), {
    categories: top.map(t => t.skill.length > 26 ? t.skill.slice(0, 25) + '…' : t.skill),
    series: seriesByAgent(top),
  });
}
