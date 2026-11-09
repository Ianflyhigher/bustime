"""청사출발 리무진 앱 시간표 갱신 스크립트.
사용: python3 update.py  (같은 폴더에 template.html 필요, 결과는 ../청사출발리무진.html)
필요 네트워크: www.airport.kr
"""
import re, html, json, subprocess, time, sys, os, base64, urllib.parse, datetime, tempfile
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); TMP = tempfile.mkdtemp()
def curl(url, data=None):
    out = os.path.join(TMP, str(abs(hash((url, str(data))))))
    for i in range(6):
        args = ["curl", "-sS", "-L", "-m", "40", "-o", out]
        if data:
            args += ["-X", "POST"]
            for k, v in data.items(): args += ["--data-urlencode", f"{k}={v}"]
        if subprocess.run(args + [url]).returncode == 0 and os.path.getsize(out) > 500:
            return open(out, encoding="utf-8", errors="ignore").read()
        time.sleep(2 + i)
    raise RuntimeError("fetch failed: " + url)
C = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
# 1) route list per region
routes, seen = [], set()
for a, nm in {1:"서울",2:"경기",3:"인천",4:"강원",5:"충청",7:"전라",6:"경상"}.items():
    inner = urllib.parse.quote(f"/bus/ap_ko/busRouteList.do?siteId=ap_ko&routeArea={a}&searchVal=&", safe="")
    enc = urllib.parse.quote(base64.b64encode(("fnct1|@@|" + inner).encode()).decode(), safe="")
    h = curl(f"https://www.airport.kr/ap_ko/976/subview.do?enc={enc}")
    for rid, name in re.findall(r"getBusInfoDetail\('(\d+)'\);\">(.*?)</a>", h):
        if rid not in seen: seen.add(rid); routes.append((nm, rid, html.unescape(name).strip()))
# 2) route details
def detail(r): return r, curl("https://www.airport.kr/bus/ap_ko/busInfoDetail.do", {"routeId": r[1]})
with ThreadPoolExecutor(4) as ex: details = list(ex.map(detail, routes))
def mins(t):
    h, m = map(int, t.split(":")); v = h*60+m
    return v + 1440 if h < 4 else v
out = []
for (anm, rid, name), h in details:
    t = C(h)
    tt = {}
    for k in ["T1/평일", "T1/주말"]:
        mm = re.search(r"버스 시간표\(" + k + r"\)(.*?)(버스 시간표\(|노선정보|$)", t)
        tt[k] = re.findall(r"\b\d{2}:\d{2}\b", mm.group(1)) if mm else []
    if not tt["T1/평일"]: continue
    m = re.match(r"^\s*(N?\d+[A-Z\-0-9]*)", name); no = m.group(1) if m else name.split("(")[0]
    stops = [C(x) for x in re.findall(r'route-bus-line-list-article">\s*<div class="box">(.*?)</div>', h, re.S)]
    stops = [s for s in stops if "공항1터미널" not in s.replace(" ", "") and "공항2터미널" not in s.replace(" ", "")]
    loc = re.search(r"제1 여객터미널 승차위치 \( (.*?) \)", t); fare = re.search(r"₩[\d,]+", t)
    op = re.search(r"₩[\d,]+ (.*?)(?: / 홈페이지)? 노선 시간표", t); op = op.group(1).strip() if op else ""
    wk = sorted(set(map(mins, tt["T1/평일"]))); we = sorted(set(map(mins, tt["T1/주말"]))) if tt["T1/주말"] else wk
    rec = {"n": no, "l": name, "a": anm, "o": re.sub(r"\(.*?\)", "", op).strip(), "tel": (re.search(r"\((.*?)\)", op) or [None, ""])[1],
           "f": fare.group(0) if fare else "", "p": (loc.group(1) if loc else "").replace(" ", ""), "s": stops, "wk": wk}
    if we != wk: rec["we"] = we
    if no in ("6001", "6002", "6015"): rec["nt"] = 1
    out.append(rec)
# 3) shuttle 04 at 국제업무단지 (D00048)
sh_html = curl("https://www.airport.kr/shtbus/ap_ko/getShtbusInfo.do", {"shtbusCd": "D00048"})
sh, hh = [], None
for tok in re.findall(r"\d+[시분]", C(sh_html).split("엑셀 다운로드")[1]):
    if tok.endswith("시"): hh = int(tok[:-1])
    else: sh.append(hh*60 + int(tok[:-1]))
# keep 공항리무진 platform codes from previous build if present
prev = os.path.join(HERE, "platforms.json")
if os.path.exists(prev):
    pl = json.load(open(prev))
    for r in out:
        if r["n"] in pl: r["p2"] = pl[r["n"]]
data = {"routes": out, "shuttle": sorted(sh)}
assert len(out) > 100 and len(sh) > 50, "too little data, aborting"
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
coords = open(os.path.join(HERE, "coords.json"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "coords.json")) else "{}"
page = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))).replace("__COORDS__", coords).replace("__DATE__", f"{today.year}.{today.month}.{today.day}")
open(os.environ.get("LIMO_OUT") or os.path.join(HERE, "..", "청사출발리무진.html"), "w", encoding="utf-8").write(page)
json.dump(data, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False)
print(f"routes={len(out)} shuttle={len(sh)} requests={7+len(routes)+1}")
