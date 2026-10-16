/*{
  "DESCRIPTION": "A clear disc squeezed between polarizers. The colors are real stress fringes, computed per wavelength.",
  "CREDIT": "Optics Bench",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Optics Bench"
  ],
  "INPUTS": [
    {
      "NAME": "paramA",
      "LABEL": "Load",
      "TYPE": "float",
      "DEFAULT": 0.6,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramB",
      "LABEL": "Second load",
      "TYPE": "float",
      "DEFAULT": 0.25,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramC",
      "LABEL": "Fringe density",
      "TYPE": "float",
      "DEFAULT": 0.45,
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
      "DEFAULT": 20,
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

// Photoelastic disc: A clear disc squeezed between polarizers. The colors are real stress fringes, computed per wavelength.
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

void addLoad(inout vec3 s, vec2 x, vec2 P, vec2 d, float F){
  vec2 r=x-P; float rl=max(length(r),.004); vec2 rh=r/rl; float c=max(dot(rh,d),0.);
  float sr=-2.*F*c/(PI*rl); s+=vec3(sr*rh.x*rh.x, sr*rh.y*rh.y, sr*rh.x*rh.y); }
void main(){ vec2 uv=screenUV(); float R=.96; float r=length(uv);
  float th=PI*uPhase; float F=uA*(.8+.2*sin(TAU*uPhase*2.));
  vec2 P1=R*vec2(cos(th),sin(th)); vec3 s=vec3(0.);
  addLoad(s,uv,P1,-P1/R,F); addLoad(s,uv,-P1,P1/R,F);
  vec2 P2=R*vec2(cos(th+PI*.5),sin(th+PI*.5)); float F2=F*uB*(.6+.4*cos(TAU*uPhase*2.));
  addLoad(s,uv,P2,-P2/R,F2); addLoad(s,uv,-P2,P2/R,F2);
  float diff=sqrt((s.x-s.y)*(s.x-s.y)+4.*s.z*s.z);
  float N=min(diff*mix(.6,5.,uC),14.);
  vec3 col=vec3(0.); vec3 wsum=vec3(0.);
  for(int i=0;i<8;i++){ float fi=float(i); float lam=420.+fi*40.;
    vec3 w = fi<1.?vec3(.3,0.,.6):fi<2.?vec3(.1,.1,1.):fi<3.?vec3(0.,.6,.7):fi<4.?vec3(.2,1.,.1):fi<5.?vec3(.8,.9,0.):fi<6.?vec3(1.,.4,0.):fi<7.?vec3(.8,.05,0.):vec3(.4,0.,0.);
    float I=pow(sin(PI*N*560./lam),2.); col+=w*I; wsum+=w; }
  col/=wsum; col=hueShift(col,uHue);
  col*=smoothstep(R,R-.01,r);
  col+=vec3(.25,.28,.32)*exp(-pow((r-R)*90.,2.));
  gl_FragColor=finish(col*1.5,uv); }
