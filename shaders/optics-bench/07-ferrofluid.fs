/*{
  "DESCRIPTION": "Black liquid metal spiking on a magnet. Spikes pulse on a 4-beat kick across each loop.",
  "CREDIT": "Optics Bench",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Optics Bench"
  ],
  "INPUTS": [
    {
      "NAME": "paramA",
      "LABEL": "Spike height",
      "TYPE": "float",
      "DEFAULT": 0.75,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramB",
      "LABEL": "Spike density",
      "TYPE": "float",
      "DEFAULT": 0.45,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramC",
      "LABEL": "Kicks per loop",
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
      "DEFAULT": 8,
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

// Ferrofluid: Black liquid metal spiking on a magnet. Spikes pulse on a 4-beat kick across each loop.
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

vec4 hexC(vec2 p){ vec2 s=vec2(1.,1.7320508); vec4 hC=floor(vec4(p,p-vec2(.5,1.))/s.xyxy)+.5;
  vec4 h=vec4(p-hC.xy*s, p-(hC.zw+.5)*s); return dot(h.xy,h.xy)<dot(h.zw,h.zw)?vec4(h.xy,hC.xy):vec4(h.zw,hC.zw+.5); }
float kicks(){ float n=floor(mix(1.,8.99,uC)); return exp(-fract(uPhase*n)*5.); }
float height(vec2 p){ float r=length(p);
  vec2 q=rot(p, TAU*uPhase/6.)*mix(5.,13.,uB);
  vec4 h=hexC(q); float d=length(h.xy);
  float amp=uA*(.35+.65*kicks())*smoothstep(.95,.05,r);
  float spike=amp*pow(max(1.-d/.48,0.),1.15)*.75/mix(5.,13.,uB)*8.;
  float pool=smoothstep(1.,.15,r)*.08;
  return pool+spike; }
vec3 env(vec3 d){ vec3 c=vec3(.01)+vec3(.04,.045,.05)*max(d.y,0.);
  c+=hueShift(vec3(1.,.97,.92),uHue)*smoothstep(.75,.95,dot(d,normalize(vec3(-.5,.55,.65))))*2.5;
  c+=hueShift(vec3(.6,.75,1.),uHue)*smoothstep(.85,.97,dot(d,normalize(vec3(.6,-.3,.75))))*1.2;
  c+=vec3(.9)*smoothstep(.04,0.,abs(d.y-.2))*smoothstep(.2,.9,d.z)*.25;
  return c; }
void main(){ vec2 uv=screenUV(); float e=.0025;
  float hx=(height(uv+vec2(e,0.))-height(uv-vec2(e,0.)))/(2.*e);
  float hy=(height(uv+vec2(0.,e))-height(uv-vec2(0.,e)))/(2.*e);
  vec3 n=normalize(vec3(-hx,-hy,1.));
  vec3 rd=reflect(vec3(0.,0.,-1.),n);
  float fres=.05+.95*pow(1.-n.z,4.);
  vec3 col=vec3(.004)+env(rd)*mix(.3,1.2,fres);
  gl_FragColor=finish(col,uv); }
