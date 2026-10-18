// Minimal ISF effect host: compiles each .fs effect in WebGL, feeds it a test image and renders previews.
// Usage: PWPATH=<path to playwright> node isf_fx_test.js <fx_dir> <test_image> <out_dir> [variants.json]
// variants.json maps a shader file name to a list of {name, inputs:{NAME: value}} overrides of the defaults.
const { chromium } = require(process.env.PWPATH);
const fs = require('fs'); const path = require('path');
const [dir, img, outDir, variantsFile] = process.argv.slice(2);
const variants = variantsFile ? JSON.parse(fs.readFileSync(variantsFile, 'utf8')) : {};
const SIZE = 720;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: SIZE + 40, height: SIZE + 40 } });
  const imgData = 'data:image/jpeg;base64,' + fs.readFileSync(img).toString('base64');
  await p.setContent(`<canvas id="c" width="${SIZE}" height="${SIZE}"></canvas><img id="src" src="${imgData}">`);
  await p.waitForFunction(() => document.getElementById('src').complete);
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.fs')).sort()) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = src.match(/^\/\*([\s\S]*?)\*\//); const meta = JSON.parse(m[1]); const body = src.slice(m[0].length);
    const type = t => ({ image: 'sampler2D', bool: 'bool', long: 'int', color: 'vec4', point2D: 'vec2' }[t] || 'float');
    const decl = meta.INPUTS.map(i => `uniform ${type(i.TYPE)} ${i.NAME};`).join('\n');
    const frag = `precision highp float;\nuniform float TIME;\nuniform vec2 RENDERSIZE;\nvarying vec2 isf_FragNormCoord;\n` +
      `#define IMG_NORM_PIXEL(i, uv) texture2D(i, uv)\n#define IMG_PIXEL(i, px) texture2D(i, (px) / RENDERSIZE)\n` +
      `#define IMG_THIS_PIXEL(i) texture2D(i, isf_FragNormCoord)\n${decl}\n${body}`;
    for (const v of [{ name: 'default', inputs: {} }, ...(variants[f] || [])]) {
      const res = await p.evaluate(({ frag, inputs, over, SIZE }) => {
        const c = document.getElementById('c'); const gl = c.getContext('webgl', { preserveDrawingBuffer: true });
        const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
        try {
          const pr = gl.createProgram();
          gl.attachShader(pr, sh(gl.VERTEX_SHADER, 'attribute vec2 p;varying vec2 isf_FragNormCoord;void main(){isf_FragNormCoord=p*.5+.5;gl_Position=vec4(p,0.,1.);}'));
          gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, frag)); gl.linkProgram(pr);
          if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
          gl.useProgram(pr);
          const bf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
          const a = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
          const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
          gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, document.getElementById('src'));
          for (const [k, val] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, val);
          gl.uniform1f(gl.getUniformLocation(pr, 'TIME'), 3.7); gl.uniform2f(gl.getUniformLocation(pr, 'RENDERSIZE'), SIZE, SIZE);
          for (const i of inputs) {
            const l = gl.getUniformLocation(pr, i.NAME); if (!l) continue;
            const val = i.NAME in over ? over[i.NAME] : i.DEFAULT;
            if (i.TYPE === 'image') gl.uniform1i(l, 0);
            else if (i.TYPE === 'bool') gl.uniform1i(l, val ? 1 : 0);
            else if (i.TYPE === 'long') gl.uniform1i(l, val);
            else if (i.TYPE === 'color') gl.uniform4fv(l, val);
            else gl.uniform1f(l, val);
          }
          gl.viewport(0, 0, SIZE, SIZE); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); return 'ok';
        } catch (e) { return 'ERROR ' + e.message; }
      }, { frag, inputs: meta.INPUTS, over: v.inputs, SIZE });
      console.log(f, v.name, res);
      await (await p.$('#c')).screenshot({ path: path.join(outDir, `${f.replace('.fs', '')}-${v.name}.png`) });
    }
  }
  await b.close();
})();
