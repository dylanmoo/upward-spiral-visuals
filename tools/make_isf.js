// Extract HEADER + SHADERS from the Optics Bench page and write one ISF v2 generator per shader.
const fs = require('fs');
const [,, page, outDir] = process.argv;
const html = fs.readFileSync(page, 'utf8');
const start = html.indexOf('const HEADER =');
const end = html.indexOf('const VERT =');
const { HEADER, SHADERS } = new Function(html.slice(start, end) + '; return { HEADER, SHADERS };')();
const helpers = HEADER.split('\n').filter(l => !/^\s*(precision|uniform)\b/.test(l)).join('\n');
const slug = { lens: '01-crystal-lens', reed: '03-reeded-glass', photo: '05-photoelastic-disc', ferro: '07-ferrofluid',
  heat: '08-hot-metal', schlieren: '09-schlieren', lensing: '10-gravitational-lens', nebula: '11-nebula-dust' };
for (const s of SHADERS) {
  const f = (name, label, def, min, max) => ({ NAME: name, LABEL: label, TYPE: 'float', DEFAULT: def, MIN: min, MAX: max });
  const meta = {
    DESCRIPTION: s.note, CREDIT: 'Optics Bench', ISFVSN: '2', CATEGORIES: ['Generator', 'Optics Bench'],
    INPUTS: [
      f('paramA', s.params.A[0], s.params.A[1], 0, 1),
      f('paramB', s.params.B[0], s.params.B[1], 0, 1),
      f('paramC', s.params.C[0], s.params.C[1], 0, 1),
      f('hueAmount', 'Hue shift', s.hue, -0.5, 0.5),
      f('loopSeconds', 'Loop length (s)', s.loop, 2, 60),
      { NAME: 'useManualPhase', LABEL: 'Drive phase manually', TYPE: 'bool', DEFAULT: false },
      f('manualPhase', 'Phase (0-1, BPM-sync this)', 0, 0, 1),
      { NAME: 'circleMask', LABEL: 'Circle mask', TYPE: 'bool', DEFAULT: true },
    ],
  };
  const body = `/*${JSON.stringify(meta, null, 2)}*/

// ${s.name}: ${s.note}
// Generated from Optics Bench. Phase runs 0..1 once per loop; every frame of the loop is exact.
#define uRes RENDERSIZE
#define uPhase (useManualPhase ? fract(manualPhase) : fract(TIME / max(loopSeconds, 0.1)))
#define uA paramA
#define uB paramB
#define uC paramC
#define uHue hueAmount
#define uMask (circleMask ? 1.0 : 0.0)
${helpers}
${s.src.trim()}
`;
  fs.writeFileSync(`${outDir}/${slug[s.id]}.fs`, body);
  console.log('wrote', slug[s.id]);
}
