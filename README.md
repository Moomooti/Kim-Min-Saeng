<h1 align="center">✨ KIMMIMSAENG 프로젝트 구조 ✨</h1>

<details open>
<summary>📁 <b>폴더 트리 보기</b></summary>

<pre>
KIMMIMSAENG/
└── crawler/
    └── DB/
        ├── kimminsaeng.db        # 🎲 메인 데이터베이스
        ├── raw_results.sqlite    # 🗂️ 크롤 원본 DB
        ├── keywords.txt          # 🏷️  키워드 리스트
        ├── naver_crawler.py      # 🤖 네이버 크롤러
        └── seoul_food.py         # 🍜 서울 음식점 크롤러
</pre>
</details>


<details>
<summary>📄 <b>파일/폴더별 설명 자세히 보기</b></summary>

<table>
  <thead>
    <tr>
      <th>파일/폴더명</th>
      <th>설명</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>kimminsaeng.db</code></td>
      <td>🎲 <b>메인 데이터베이스 파일</b></td>
    </tr>
    <tr>
      <td><code>raw_results.sqlite</code></td>
      <td>🗂️ 크롤링 원본 백업용 DB</td>
    </tr>
    <tr>
      <td><code>keywords.txt</code></td>
      <td>🏷️  검색/분석 키워드 리스트</td>
    </tr>
    <tr>
      <td><code>naver_crawler.py</code></td>
      <td>🤖 네이버 지도/검색 자동 크롤러</td>
    </tr>
    <tr>
      <td><code>seoul_food.py</code></td>
      <td>🍜 서울시 음식점/사용처 데이터 크롤러</td>
    </tr>
  </tbody>
</table>
</details>
