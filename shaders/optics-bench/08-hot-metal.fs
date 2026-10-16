/*{
  "DESCRIPTION": "A torch path on hammered steel. Color follows real blackbody temperature, with temper colors left behind as it cools.",
  "CREDIT": "Optics Bench",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Optics Bench"
  ],
  "INPUTS": [
    {
      "NAME": "paramA",
      "LABEL": "Heat",
      "TYPE": "float",
      "DEFAULT": 0.75,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramB",
      "LABEL": "Temper colors",
      "TYPE": "float",
      "DEFAULT": 0.55,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramC",
      "LABEL": "Hammer texture",
      "TYPE": "float",
      "DEFAULT": 0.3,
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
      "DEFAULT": 14,
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

// Hot metal: A torch path on hammered steel. Color follows real blackbody temperature, with temper colors left behind as it cools.
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

float dimples(vec2 p){ p*=14.; vec2 i=floor(p), f=fract(p); float m=1.;
  for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++){ vec2 g=vec2(float(x),float(y)); vec2 o=vec2(hash12(i+g),hash12(i+g+9.));
    m=min(m,length(g+o-f)); } return m; }
void main(){ vec2 uv=screenUV(); float r=length(uv);
  float a=TAU*uPhase; vec2 spot=.48*vec2(cos(a),sin(a));
  float ang=atan(uv.y,uv.x); float behind=fract((a-ang)/TAU);
  float ring=exp(-pow((r-.48)*11.,2.));
  float flick=fbm3(vec3(uv*4.,0.)+loopOff(1.2));
  float trail=exp(-behind*3.2)*smoothstep(0.,.05,behind);
  float T=exp(-dot(uv-spot,uv-spot)*28.)*1.05 + ring*trail*.75;
  T*=mix(.8,1.15,flick); T*=uA*1.15;
  float e=.004; float d0=dimples(uv), dx=dimples(uv+vec2(e,0.)), dy=dimples(uv+vec2(0.,e));
  vec3 n=normalize(vec3(-(dx-d0)/e*uC*.04, -(dy-d0)/e*uC*.04, 1.));
  vec3 L=normalize(vec3(-.4,.55,.7)); float spec=pow(max(dot(reflect(-L,n),vec3(0,0,1)),0.),40.);
  vec3 steel=vec3(.11,.115,.125)*(.6+.4*n.z)+vec3(.8,.85,.9)*spec*.5;
  float tint=exp(-pow((r-.48)*6.,2.))*clamp(1.-behind*1.1,0.,1.)*smoothstep(0.,.05,behind)+exp(-dot(uv-spot,uv-spot)*14.);
  float tt=clamp(tint*1.6,0.,1.);
  vec3 temper = tt<.2?mix(steel,vec3(.85,.75,.45),tt/.2): tt<.45?mix(vec3(.85,.75,.45),vec3(.65,.38,.18),(tt-.2)/.25):
                tt<.7?mix(vec3(.65,.38,.18),vec3(.42,.2,.5),(tt-.45)/.25): mix(vec3(.42,.2,.5),vec3(.18,.32,.72),(tt-.7)/.3);
  vec3 col=mix(steel,temper*(.55+.45*n.z)+vec3(.6)*spec*.3,uB*smoothstep(.02,.15,tint));
  float K=650.+5600.*clamp(T,0.,1.);
  float glow=smoothstep(.12,.35,T)*pow(clamp(T,0.,1.3),3.)*2.2;
  col=col*(1.-clamp(glow,0.,1.)*.9)+hueShift(blackbody(K),uHue)*glow;
  gl_FragColor=finish(col,uv); }
