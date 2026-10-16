// Minimal ISF host: parse the JSON header, declare uniforms from INPUTS, compile and render each .fs in WebGL.
const { chromium } = require(process.env.PWPATH);
const fs = require('fs'); const path = require('path');
const dir = process.argv[2], outDir = process.argv[3];
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 520, height: 520 } });
  await p.setContent('<canvas id="c" width="480" height="480"></canvas>');
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.fs')).sort()) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = src.match(/^\/\*([\s\S]*?)\*\//); const meta = JSON.parse(m[1]); const body = src.slice(m[0].length);
    const decl = meta.INPUTS.map(i => `uniform ${i.TYPE === 'bool' ? 'bool' : 'float'} ${i.NAME};`).join('\n');
    const frag = `precision highp float;\nuniform float TIME;\nuniform vec2 RENDERSIZE;\n${decl}\n${body}`;
    const res = await p.evaluate(({ frag, inputs }) => {
      const c = document.getElementById('c'); const gl = c.getContext('webgl', { preserveDrawingBuffer: true });
      const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
      try {
        const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}')); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, frag)); gl.linkProgram(pr);
        if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
        gl.useProgram(pr); const bf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
        const a = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
        gl.uniform1f(gl.getUniformLocation(pr, 'TIME'), 3.7); gl.uniform2f(gl.getUniformLocation(pr, 'RENDERSIZE'), 480, 480);
        for (const i of inputs) { const l = gl.getUniformLocation(pr, i.NAME); if (!l) continue; if (i.TYPE === 'bool') gl.uniform1i(l, i.DEFAULT ? 1 : 0); else gl.uniform1f(l, i.DEFAULT); }
        gl.viewport(0, 0, 480, 480); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); return 'ok';
      } catch (e) { return 'ERROR ' + e.message; }
    }, { frag, inputs: meta.INPUTS });
    console.log(f, res);
    await (await p.$('#c')).screenshot({ path: path.join(outDir, f.replace('.fs', '.png')) });
  }
  await b.close();
})();
