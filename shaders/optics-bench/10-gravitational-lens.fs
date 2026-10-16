/*{
  "DESCRIPTION": "A stark starfield bent around a black hole. The bright ring is where stars line up behind it.",
  "CREDIT": "Optics Bench",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Optics Bench"
  ],
  "INPUTS": [
    {
      "NAME": "paramA",
      "LABEL": "Lens mass",
      "TYPE": "float",
      "DEFAULT": 0.55,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramB",
      "LABEL": "Shadow size",
      "TYPE": "float",
      "DEFAULT": 0.35,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramC",
      "LABEL": "Star color",
      "TYPE": "float",
      "DEFAULT": 0.25,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "hueAmount",
      "LABEL": "Hue shift",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": -0.5,
      "MAX": 0.5
    },
    {
      "NAME": "loopSeconds",
      "LABEL": "Loop length (s)",
      "TYPE": "float",
      "DEFAULT": 40,
      "MIN": 2,
      "MAX": 60
    },
    {
      "NAME": "useManualPhase",
      "LABEL": "Drive phase manually",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "manualPhase",
      "LABEL": "Phase (0-1, BPM-sync this)",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "circleMask",
      "LABEL": "Circle mask",
      "TYPE": "bool",
      "DEFAULT": true
    }
  ]
}*/

// Gravitational lens: A stark starfield bent around a black hole. The bright ring is where stars line up behind it.
// Generated from Optics Bench. Phase runs 0..1 once per loop; every frame of the loop is exact.
#define uRes RENDERSIZE
#define uPhase (useManualPhase ? fract(manualPhase) : fract(TIME / max(loopSeconds, 0.1)))
#define uA paramA
#define uB paramB
#define uC paramC
#define uHue hueAmount
#define uMask (circleMask ? 1.0 : 0.0)

#define TAU 6.28318530718
#define PI 3.14159265359
float hash12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float hash13(vec3 p3){ p3=fract(p3*.1031); p3+=dot(p3,p3.zyx+31.32); return fract((p3.x+p3.y)*p3.z); }
float noise3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(mix(hash13(i),hash13(i+vec3(1,0,0)),f.x),mix(hash13(i+vec3(0,1,0)),hash13(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(hash13(i+vec3(0,0,1)),hash13(i+vec3(1,0,1)),f.x),mix(hash13(i+vec3(0,1,1)),hash13(i+vec3(1,1,1)),f.x),f.y),f.z); }
float fbm3(vec3 p){ float s=0., a=.5; for(int i=0;i<5;i++){ s+=a*noise3(p); p=p*2.03+vec3(1.7,9.2,3.1); a*=.5; } return s; }
// noise periodic in y with integer period P (lattice units)
float noiseP(vec3 p, float P){ vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  float y0=mod(i.y,P), y1=mod(i.y+1.,P);
  vec3 a=vec3(i.x,y0,i.z), b=vec3(i.x,y1,i.z);
  return mix(mix(mix(hash13(a),hash13(a+vec3(1,0,0)),f.x),mix(hash13(b),hash13(b+vec3(1,0,0)),f.x),f.y),
             mix(mix(hash13(a+vec3(0,0,1)),hash13(a+vec3(1,0,1)),f.x),mix(hash13(b+vec3(0,0,1)),hash13(b+vec3(1,0,1)),f.x),f.y),f.z); }
float fbmP(vec3 p, float P){ float s=0., a=.5; for(int i=0;i<4;i++){ s+=a*noiseP(p,P); p*=2.; P*=2.; a*=.45; } return s; }
vec3 loopOff(float r){ float a=uPhase*TAU; return r*vec3(cos(a), 0.4*sin(a), sin(a)); }
vec2 rot(vec2 p, float a){ float c=cos(a), s=sin(a); return vec2(c*p.x-s*p.y, s*p.x+c*p.y); }
vec3 hueShift(vec3 c, float h){ const vec3 k=vec3(0.57735); float ca=cos(h*TAU); return c*ca+cross(k,c)*sin(h*TAU)+k*dot(k,c)*(1.-ca); }
vec3 blackbody(float t){ t/=100.; float r,g,b;
  r = t<=66. ? 1. : clamp(1.29293618606*pow(t-60.,-0.1332047592),0.,1.);
  g = t<=66. ? clamp(0.390081578769*log(t)-0.631841443788,0.,1.) : clamp(1.12989086089*pow(t-60.,-0.0755148492),0.,1.);
  b = t>=66. ? 1. : (t<=19. ? 0. : clamp(0.543206789110*log(t-10.)-1.19625408914,0.,1.));
  return vec3(r,g,b); }
vec2 screenUV(){ return (gl_FragCoord.xy-0.5*uRes)/(0.5*min(uRes.x,uRes.y)); }
vec4 finish(vec3 col, vec2 uv){ col=max(col,0.); col=1.-exp(-col*1.15); col=pow(col,vec3(0.92));
  float r=length(uv); if(uMask>0.5) col*=smoothstep(1.0,0.992,r); return vec4(col,1.); }

vec3 stars(vec2 q){ vec3 col=vec3(0.);
  for(int L=0;L<3;L++){ float s= L==0?18.:L==1?42.:95.; vec2 g=q*s; vec2 i=floor(g), f=fract(g)-.5;
    float h=hash12(i+float(L)*17.); if(h>.82){ vec2 o=vec2(hash12(i+3.),hash12(i+5.))-.5; float d=length(f-o*.7);
      float b=pow((h-.82)/.18,1.8)*(L==0?3.:L==1?1.8:1.1);
      vec3 c=mix(vec3(1.),blackbody(2800.+9000.*hash12(i+11.)),uC);
      col+=c*b*exp(-d*d*(L==0?120.:L==1?260.:500.)); } }
  float band=fbm3(vec3(rot(q,.5)*vec2(1.4,5.),2.)); col+=vec3(.16,.15,.14)*smoothstep(.4,.8,band)*max(1.-abs(rot(q,.5).y)*.9,0.);
  return col; }
void main(){ vec2 uv=screenUV(); float b=length(uv);
  float rs=mix(.06,.3,uB); float tE=rs*mix(1.2,2.2,uA);
  vec3 col=vec3(0.);
  if(b>rs){ float beta=b-tE*tE/b; vec2 dir=uv/b;
    vec2 src=rot(dir*beta, TAU*uPhase);
    float mag=clamp(abs((b/max(abs(beta),1e-3))*(1.+tE*tE/(b*b)))*.5,0.,6.);
    col=stars(src)*mag;
    col+=hueShift(vec3(1.,.95,.88),uHue)*exp(-pow((b-rs*1.08)*90./rs*.05,2.))*.35;
  }
  gl_FragColor=finish(col,uv); }
