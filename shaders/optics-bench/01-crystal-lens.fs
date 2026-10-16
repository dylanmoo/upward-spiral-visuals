/*{
  "DESCRIPTION": "The screen as a glass sphere: inverted, magnified, split into color at the rim.",
  "CREDIT": "Optics Bench",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Optics Bench"
  ],
  "INPUTS": [
    {
      "NAME": "paramA",
      "LABEL": "Refraction",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramB",
      "LABEL": "Lens size",
      "TYPE": "float",
      "DEFAULT": 0.92,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "paramC",
      "LABEL": "Dispersion",
      "TYPE": "float",
      "DEFAULT": 0.5,
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
      "DEFAULT": 16,
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

// Crystal lens: The screen as a glass sphere: inverted, magnified, split into color at the rim.
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

vec3 pal(float h){ vec3 c = h<.25? vec3(1.,.72,.38) : h<.5? vec3(.35,.8,1.) : h<.75? vec3(1.,.35,.6) : vec3(.95,.95,.9); return hueShift(c,uHue); }
vec3 scene(vec2 q){
  float sp=.28; float x=q.x/sp+uPhase*4.; float id=floor(x); float fx=fract(x)-.5;
  vec3 col=pal(hash12(vec2(id,3.)))*exp(-fx*fx*70.)*(.45+.55*sin(q.y*2.3+id*1.7+uPhase*TAU))*1.4;
  vec2 g=q*5.+vec2(0.,uPhase*10.); vec2 gi=floor(g), gf=fract(g)-.5; float h=hash12(gi+7.);
  vec2 o=vec2(hash12(gi+1.),hash12(gi+2.))-.5; col+=pal(h)*smoothstep(.18,.0,length(gf-o*.6))*step(.72,h)*1.6;
  col+=vec3(.02,.025,.04)*(1.-q.y*.3);
  return col; }
void main(){ vec2 uv=screenUV(); float R=mix(.45,1.,uB); float r=length(uv);
  vec3 col;
  if(r<R){ float z=sqrt(max(1.-(r/R)*(r/R),0.)); vec3 n=vec3(uv/R,z);
    float k=mix(.25,1.,uA); float d=uC*.12;
    vec2 base=-uv*k/(z*.65+.35);
    col=vec3(scene(base*(1.-d)).r, scene(base).g, scene(base*(1.+d)).b);
    float F=.04+.96*pow(1.-z,5.);
    vec3 refl=vec3(.55,.6,.7)*smoothstep(.2,1.,n.y*.5+.5)*.35;
    col=mix(col,refl,F*.8);
    col+=vec3(1.)*pow(max(dot(normalize(n),normalize(vec3(-.4,.5,.75))),0.),120.)*1.4;
    col*=smoothstep(1.,.965,r/R)*.85+.15;
  } else { col=scene(uv)*.55; }
  gl_FragColor=finish(col,uv); }
