"""template.html + data.json -> ../index.html (standalone web app page).
사용: python3 update/build_site.py [YYYY.M.D]   (날짜를 안 주면 오늘, 한국시간)
"""
import os, sys, re, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(os.path.join(HERE, n), encoding="utf-8").read()
tpl, data = rd("template.html"), rd("data.json")
coords = rd("coords.json") if os.path.exists(os.path.join(HERE, "coords.json")) else "{}"
if len(sys.argv) > 1: date = sys.argv[1]
else:
    t = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))); date = f"{t.year}.{t.month}.{t.day}"
body = tpl.replace("__DATA__", data).replace("__COORDS__", coords).replace("__DATE__", date)
m = re.search(r"<title>.*?</title>\s*", body); title = m.group(0).strip(); body = body.replace(m.group(0), "", 1)
body = re.sub(r'<meta name="claude:[^>]*>\s*', "", body)
head = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{title}
<meta name="description" content="인천공항공사 청사에서 출발해 가장 빨리 탈 수 있는 공항 리무진을 찾아줍니다.">
<meta name="theme-color" content="#0e7c83">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="청사리무진">
<style>html,body{{margin:0}}</style>
</head>
<body>
"""
tail = """
<script>if('serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}))}</script>
</body>
</html>
"""
open(os.path.join(HERE, "..", "index.html"), "w", encoding="utf-8").write(head + body + tail)
print("index.html built,", date)
