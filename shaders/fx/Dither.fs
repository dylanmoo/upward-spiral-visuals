/*{
  "DESCRIPTION": "Retro dither effect: pixelates the input and reduces it to a few colors with an ordered (Bayer), noise, halftone or line pattern. Palettes include duotone, Game Boy, CGA and Ladybug.",
  "CREDIT": "Upward Spiral Visuals (CC BY 4.0 media, MIT code)",
  "ISFVSN": "2",
  "CATEGORIES": ["Stylize"],
  "INPUTS": [
    { "NAME": "inputImage", "TYPE": "image" },
    { "NAME": "pixelSize", "LABEL": "Size", "TYPE": "float", "DEFAULT": 3.0, "MIN": 1.0, "MAX": 24.0 },
    { "NAME": "pattern", "LABEL": "Pattern", "TYPE": "long", "DEFAULT": 2,
      "VALUES": [0, 1, 2, 3, 4, 5, 6], "LABELS": ["Bayer 2x2", "Bayer 4x4", "Bayer 8x8", "White noise", "Blue-ish noise", "Halftone dots", "Lines"] },
    { "NAME": "palette", "LABEL": "Palette", "TYPE": "long", "DEFAULT": 1,
      "VALUES": [0, 1, 2, 3, 4], "LABELS": ["Source colors", "Duotone (Dark/Light)", "Game Boy", "CGA", "Ladybug"] },
    { "NAME": "levels", "LABEL": "Levels", "TYPE": "float", "DEFAULT": 2.0, "MIN": 2.0, "MAX": 8.0 },
    { "NAME": "darkColor", "LABEL": "Dark", "TYPE": "color", "DEFAULT": [0.05, 0.04, 0.08, 1.0] },
    { "NAME": "lightColor", "LABEL": "Light", "TYPE": "color", "DEFAULT": [0.96, 0.92, 0.84, 1.0] },
    { "NAME": "spread", "LABEL": "Dither strength", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.5 },
    { "NAME": "contrast", "LABEL": "Contrast", "TYPE": "float", "DEFAULT": 1.1, "MIN": 0.2, "MAX": 3.0 },
    { "NAME": "brightness", "LABEL": "Brightness", "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5 },
    { "NAME": "patternAngle", "LABEL": "Halftone/line angle", "TYPE": "float", "DEFAULT": 45.0, "MIN": 0.0, "MAX": 180.0 },
    { "NAME": "shimmer", "LABEL": "Shimmer", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0 }
  ]
}*/

const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);

// Ordered dither thresholds in [0, 1) without bit operations
float bayer2(vec2 a) {
  a = floor(a);
  return fract(a.x / 2.0 + a.y * a.y * 0.75);
}
float bayer4(vec2 a) { return bayer2(0.5 * a) * 0.25 + bayer2(a); }
float bayer8(vec2 a) { return bayer4(0.5 * a) * 0.25 + bayer2(a); }

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float threshold(vec2 cell) {
  vec2 jitter = shimmer > 0.0 ? vec2(floor(TIME * (2.0 + 22.0 * shimmer))) * vec2(5.0, 3.0) : vec2(0.0);
  if (pattern == 0) return bayer2(cell + jitter) + 0.125;
  if (pattern == 1) return bayer4(cell + jitter) + 0.03125;
  if (pattern == 2) return bayer8(cell + jitter) + 0.0078;
  if (pattern == 3) return hash(cell + jitter * 7.13);
  if (pattern == 4) return fract(52.9829189 * fract(dot(cell + jitter, vec2(0.06711056, 0.00583715))));
  float a = radians(patternAngle);
  vec2 p = mat2(cos(a), -sin(a), sin(a), cos(a)) * cell / 4.0;   // 4-pixel screen
  if (pattern == 5) return clamp(length(fract(p) - 0.5) * 1.4142, 0.0, 1.0);
  return abs(fract(p.y) - 0.5) * 2.0;
}

vec3 fixedPalette(float i) {
  if (palette == 2) {   // Game Boy
    if (i < 0.5) return vec3(0.059, 0.220, 0.059);
    if (i < 1.5) return vec3(0.188, 0.384, 0.188);
    if (i < 2.5) return vec3(0.545, 0.675, 0.059);
    return vec3(0.608, 0.737, 0.059);
  }
  if (palette == 3) {   // CGA mode 4, palette 1
    if (i < 0.5) return vec3(0.0);
    if (i < 1.5) return vec3(0.333, 1.0, 1.0);
    if (i < 2.5) return vec3(1.0, 0.333, 1.0);
    return vec3(1.0);
  }
  // Ladybug: black, deep red, red, cream
  if (i < 0.5) return vec3(0.035, 0.03, 0.03);
  if (i < 1.5) return vec3(0.52, 0.06, 0.07);
  if (i < 2.5) return vec3(0.89, 0.17, 0.14);
  return vec3(0.97, 0.92, 0.82);
}

void main() {
  vec2 cell = floor(gl_FragCoord.xy / pixelSize);
  vec2 uv = (cell + 0.5) * pixelSize / RENDERSIZE;
  vec3 c = IMG_NORM_PIXEL(inputImage, clamp(uv, 0.0, 1.0)).rgb;
  c = clamp((c - 0.5) * contrast + 0.5 + brightness, 0.0, 1.0);

  float t = 0.5 + (threshold(cell) - 0.5) * spread;
  vec3 outc;

  if (palette == 0) {
    float n = floor(levels + 0.5) - 1.0;
    outc = floor(c * n + t) / n;
  } else if (palette == 1) {
    float n = floor(levels + 0.5) - 1.0;
    float q = floor(dot(c, LUMA) * n + t) / n;
    outc = mix(darkColor.rgb, lightColor.rgb, clamp(q, 0.0, 1.0));
  } else {
    float q = clamp(floor(dot(c, LUMA) * 3.0 + t), 0.0, 3.0);   // 4 fixed colors
    outc = fixedPalette(q);
  }

  gl_FragColor = vec4(clamp(outc, 0.0, 1.0), 1.0);
}
