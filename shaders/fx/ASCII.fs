/*{
  "DESCRIPTION": "ASCII art effect: turns the input into a grid of glowing text characters. Size sets the character size, Glow adds a soft bloom around each character.",
  "CREDIT": "Upward Spiral Visuals (CC BY 4.0 media, MIT code)",
  "ISFVSN": "2",
  "CATEGORIES": ["Stylize"],
  "INPUTS": [
    { "NAME": "inputImage", "TYPE": "image" },
    { "NAME": "charSize", "LABEL": "Size", "TYPE": "float", "DEFAULT": 12.0, "MIN": 4.0, "MAX": 64.0 },
    { "NAME": "glow", "LABEL": "Glow", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0 },
    { "NAME": "charset", "LABEL": "Characters", "TYPE": "long", "DEFAULT": 0,
      "VALUES": [0, 1, 2, 3], "LABELS": ["Classic  .:-=+*#%@", "Minimal  .+#@", "Binary  0 1", "Blocks"] },
    { "NAME": "colorMode", "LABEL": "Color", "TYPE": "long", "DEFAULT": 0,
      "VALUES": [0, 1, 2], "LABELS": ["Source colors", "Tint (mono)", "Source x Tint"] },
    { "NAME": "tint", "LABEL": "Tint color", "TYPE": "color", "DEFAULT": [0.55, 1.0, 0.62, 1.0] },
    { "NAME": "bgColor", "LABEL": "Background", "TYPE": "color", "DEFAULT": [0.0, 0.0, 0.0, 1.0] },
    { "NAME": "sourceBehind", "LABEL": "Source behind", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0 },
    { "NAME": "contrast", "LABEL": "Contrast", "TYPE": "float", "DEFAULT": 1.2, "MIN": 0.2, "MAX": 3.0 },
    { "NAME": "brightness", "LABEL": "Brightness", "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5 },
    { "NAME": "invert", "LABEL": "Invert", "TYPE": "bool", "DEFAULT": false },
    { "NAME": "scramble", "LABEL": "Scramble", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0 }
  ]
}*/

// Each character cell is 6 x 8 "dots": a 5 x 7 glyph plus one dot of spacing.
// A glyph is two floats holding 5-bit rows: x = rows 0-3, y = rows 4-6 (row 0 is the top).

const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

vec2 cellSize() {
  return vec2(charSize, charSize * 8.0 / 6.0);
}

float levels() {
  if (charset == 0) return 10.0;
  if (charset == 1) return 5.0;
  if (charset == 2) return 3.0;
  return 5.0;
}

vec2 glyph(float i) {
  if (charset == 0) {
    if (i < 0.5) return vec2(0.0, 0.0);              // space
    if (i < 1.5) return vec2(0.0, 396.0);            // .
    if (i < 2.5) return vec2(12672.0, 12672.0);      // :
    if (i < 3.5) return vec2(14.0, 0.0);             // -
    if (i < 4.5) return vec2(992.0, 31744.0);        // =
    if (i < 5.5) return vec2(4255.0, 4224.0);        // +
    if (i < 6.5) return vec2(4782.0, 21632.0);       // *
    if (i < 7.5) return vec2(338922.0, 32074.0);     // #
    if (i < 8.5) return vec2(845892.0, 8563.0);      // %
    return vec2(476917.0, 24079.0);                  // @
  }
  if (charset == 1) {
    if (i < 0.5) return vec2(0.0, 0.0);
    if (i < 1.5) return vec2(0.0, 396.0);
    if (i < 2.5) return vec2(4255.0, 4224.0);
    if (i < 3.5) return vec2(338922.0, 32074.0);
    return vec2(476917.0, 24079.0);
  }
  // Binary: dark cells stay empty, mid cells are 0, bright cells are 1
  if (i < 0.5) return vec2(0.0, 0.0);
  if (i < 1.5) return vec2(476789.0, 26158.0);
  return vec2(143492.0, 4238.0);
}

// 1.0 if dot (col, row) of character i is lit
float dotLit(float i, float col, float row) {
  if (col > 4.5 || row > 6.5) return 0.0;
  if (charset == 3) {
    // shade blocks: empty, light, medium, dark, full
    if (i < 0.5) return 0.0;
    if (i < 1.5) return mod(col + 2.0 * row, 4.0) < 0.5 ? 1.0 : 0.0;
    if (i < 2.5) return mod(col + row, 2.0) < 0.5 ? 1.0 : 0.0;
    if (i < 3.5) return mod(col + 2.0 * row, 4.0) < 0.5 ? 0.0 : 1.0;
    return 1.0;
  }
  vec2 g = glyph(i);
  float bits = row < 3.5 ? g.x : g.y;
  float r = row < 3.5 ? row : row - 4.0;
  float lastRow = row < 3.5 ? 3.0 : 2.0;
  float rowBits = floor(mod(bits / pow(32.0, lastRow - r), 32.0));
  return floor(mod(rowBits / pow(2.0, 4.0 - col), 2.0));
}

vec3 cellColor(vec2 cell) {
  vec2 uv = (cell + 0.5) * cellSize() / RENDERSIZE;
  return IMG_NORM_PIXEL(inputImage, clamp(uv, 0.0, 1.0)).rgb;
}

float cellIndex(vec2 cell, vec3 c) {
  // perceptual brightness: blend luma with the brightest channel so saturated colors still read
  float l = pow(mix(dot(c, LUMA), max(c.r, max(c.g, c.b)), 0.5), 0.75);
  l = clamp((l - 0.5) * contrast + 0.5 + brightness, 0.0, 1.0);
  if (invert) l = 1.0 - l;
  float n = levels();
  float i = floor(l * (n - 0.001));
  if (scramble > 0.0 && i > 0.5) {
    float t = floor(TIME * (2.0 + 10.0 * scramble));
    float h = hash(cell + t * 0.37);
    if (h < scramble) i = clamp(i + floor((hash(cell * 1.7 + t) - 0.5) * 5.0), 1.0, n - 1.0);
  }
  return i;
}

vec3 inkColor(vec3 c) {
  vec3 src = clamp(c * 1.25, 0.0, 1.0);
  float l = dot(c, LUMA);
  if (colorMode == 1) return tint.rgb * (0.45 + 0.55 * l);
  if (colorMode == 2) return src * tint.rgb * 1.4;
  return src;
}

void main() {
  vec2 px = gl_FragCoord.xy;
  vec2 cs = cellSize();
  vec2 cell = floor(px / cs);
  vec2 local = fract(px / cs) * vec2(6.0, 8.0);    // dot space, y up
  vec2 dotPos = vec2(local.x, 8.0 - local.y);       // y down, row 0 at the top
  float col = floor(dotPos.x), row = floor(dotPos.y);

  vec3 c = cellColor(cell);
  float i = cellIndex(cell, c);
  vec3 ink = inkColor(c);

  // crisp, anti-aliased square dots
  vec2 f = fract(dotPos) - 0.5;
  float aa = 6.0 / cs.x;
  float box = 1.0 - smoothstep(0.5 - aa, 0.5 + aa, max(abs(f.x), abs(f.y)));
  float lit = dotLit(i, col, row) * box;

  vec3 bg = mix(bgColor.rgb, c * 0.5, sourceBehind);
  vec3 outc = mix(bg, ink, lit);

  if (glow > 0.0) {
    // soft bloom: every lit dot in this cell and its 8 neighbours adds a gaussian halo
    float radius = 0.7 + 0.8 * glow;               // in dots
    float k = 1.0 / (radius * radius);
    vec3 halo = vec3(0.0);
    for (int cy = -1; cy <= 1; cy++) {
      for (int cx = -1; cx <= 1; cx++) {
        vec2 nc = cell + vec2(float(cx), float(cy));
        vec3 ncol = cellColor(nc);
        float ni = cellIndex(nc, ncol);
        if (ni < 0.5) continue;
        vec2 origin = vec2(float(cx) * 6.0, -float(cy) * 8.0);   // neighbour offset in dot space (y down)
        float sum = 0.0;
        for (int r = 0; r < 7; r++) {
          for (int q = 0; q < 5; q++) {
            float on = dotLit(ni, float(q), float(r));
            if (on < 0.5) continue;
            vec2 d = dotPos - (origin + vec2(float(q), float(r)) + 0.5);
            sum += exp(-dot(d, d) * k);
          }
        }
        halo += inkColor(ncol) * sum;
      }
    }
    outc += halo * glow * 0.12;
  }

  gl_FragColor = vec4(outc, 1.0);
}
