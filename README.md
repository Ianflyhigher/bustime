# 청사출발 최단 리무진

인천공항공사 청사에서 출발할 때, 제1여객터미널에서 가장 빨리 탈 수 있는 공항 리무진을 찾아주는 웹앱입니다.
목적지나 노선번호를 넣으면 셔틀 시각, 리무진 출발시각, 버스 번호, 승차홈을 알려줍니다.

- 시간표: 인천공항 공식 버스·04번 셔틀 시간표 기준. 매주 월요일 아침 자동으로 갱신합니다 (`.github/workflows/update.yml`).
- 홈 화면에 추가하면 앱처럼 열립니다.
- 실제 운행은 교통 상황에 따라 다를 수 있습니다.

## 수동 갱신
```
python3 update/update.py && python3 update/build_site.py
```

© 2026 SungKyu Lee. All rights reserved.
