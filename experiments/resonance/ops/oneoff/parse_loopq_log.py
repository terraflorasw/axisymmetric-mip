import re, sys
# 🔴 PAIR EACH RESULT WITH ITS OWN CASE. A paste of two greps misaligns the
# moment one case yields no result — which is exactly what a continuation
# break does, and it silently shifted every row after it.
cur, rows = None, []
for ln in open(sys.argv[1], errors="ignore"):
    m = re.search(r"--- loop AZIM standoff=([\d.]+) arc=([\d.]+).*?\((wire|strip [\dx.]+)\)", ln)
    if m:
        if cur:
            rows.append(cur + ("-", "-", "NO RESULT"))
        cur = (m.group(1), m.group(2), m.group(3))
        continue
    m = re.search(r"-> Q0= *([\d,]+) +Q_L= *([\d,]+) +Q_ext= *([\d,]+) +beta= *([\d.]+)", ln)
    if m and cur:
        rows.append(cur + (m.group(3), m.group(4), ""))
        cur = None
    if cur and "continuation BROKE" in ln:
        rows.append(cur + ("-", "-", "continuation BROKE"))
        cur = None
if cur:
    rows.append(cur + ("-", "-", "in progress"))
print(f"  {'standoff':>8} {'arc':>6} {'conductor':<12} {'Q_ext':>9} {'beta':>7}  note")
for r in rows:
    print(f"  {r[0]:>8} {r[1]:>6} {r[2]:<12} {r[3]:>9} {r[4]:>7}  {r[5]}")
