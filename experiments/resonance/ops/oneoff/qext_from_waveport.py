import csv, math
def rows(p):
    with open(p) as f:
        rd=csv.reader(f); h=[x.strip() for x in next(rd)]
        return h,[[float(x) for x in r] for r in rd if r]
def col(h,n): return next(i for i,x in enumerate(h) if x.startswith(n))
hs,S = rows("/tmp/coaxq/port-S.csv")
f  = [r[col(hs,"f (GHz)")] for r in S]
ph = [r[col(hs,"arg(S[1][1])")] for r in S]
# unwrap
un, off = [], 0.0
for i,p in enumerate(ph):
    if i and p-ph[i-1] >  180: off -= 360
    elif i and p-ph[i-1] < -180: off += 360
    un.append(p+off)
# resonance = steepest phase slope
sl = [(abs((un[i+1]-un[i-1])/(f[i+1]-f[i-1])), i) for i in range(1,len(f)-1)]
smax, k = max(sl)
f0 = f[k]
print("  resonance (steepest phase) : f0 = %.6f GHz" % f0)
def cross(target):
    for i in range(len(f)-1):
        a,b = un[i]-un[k], un[i+1]-un[k]
        if (a-target)*(b-target) <= 0 and a != b:
            return f[i] + (f[i+1]-f[i])*(target-a)/(b-a)
    return None
lo, hi = cross(+90.0), cross(-90.0)
if lo and hi:
    bw = abs(hi-lo)
    print("  +-90 deg points            : %.6f / %.6f GHz  ->  BW = %.1f kHz" % (lo,hi,bw*1e6))
    print("  Q_ext = f0/BW              : %.0f" % (f0/bw))
print("  phase slope |dphi/df|      : %.4g deg/GHz = %.4g rad/GHz"
      % (smax, smax*math.pi/180))
print("  Q_ext = f0*|dphi/df|/4     : %.0f   (one-port, dphi/domega = 4Q/omega0)"
      % (f0*smax*math.pi/180/4))
print("\n  mid-arc-fed reference: Q_ext = 13,977 (lossy walls, lumped port)")
