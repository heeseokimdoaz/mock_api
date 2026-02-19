# TapaCross Mock API (한국어)

## 왜 이렇게 만들었는가?

실제 TapaCross OracleEye API가 **2026-02-23 이후에나 사용 가능**하기 때문에, 그 전까지 개발이 멈추지 않도록 **Mock API를 먼저 만들었습니다.**

이렇게 한 이유:

- **프론트엔드/백엔드 개발이 외부 API 일정에 블로킹되지 않음** — 실제 API 없이도 전체 플로우를 개발하고 테스트할 수 있습니다.
- **요청/응답 포맷이 미리 확정됨** — 런칭일에 URL 하나만 바꾸면 됩니다. 코드 수정 없음.
- **데모와 테스트가 언제든 가능** — 실제 엑셀 데이터를 변환해서 현실적인 데이터로 테스트합니다.
- **신규 팀원 온보딩이 간단** — `docker-compose up` 한 줄이면 전체 스택이 로컬에서 뜹니다.

**프로덕션 전환 시 변경 사항: 환경변수 `TAPACROSS_API_URL` 하나만 바꾸면 됩니다.**

---

## 아키텍처

```
┌────────────────────┐     ┌──────────────────────┐     ┌────────────────────┐
│                    │     │                      │     │                    │
│   프론트엔드 (UI)    │────▶│   백엔드 (:3000)      │────▶│  Mock API (:8000)  │
│   Chart.js + HTML  │     │   FastAPI + httpx     │     │  FastAPI + JSON    │
│                    │     │                      │     │                    │
└────────────────────┘     └──────────────────────┘     └────────────────────┘
```

**왜 백엔드와 Mock API를 분리했는가?**

백엔드는 **게이트웨이/프록시 역할**입니다. `client_id`, `search_id` 같은 인증 정보를 갖고 있고, 프론트엔드의 단순한 요청을 TapaCross API 포맷으로 변환합니다. 프로덕션 전환 시 백엔드 코드는 그대로 — 대상 URL만 바뀝니다.

---

## 빠른 시작

```bash
git clone <repo-url>
cd mock_api
docker-compose up
```

이것만 하면 됩니다. 컨테이너 2개가 뜹니다:

| 서비스 | URL | 설명 |
|--------|-----|------|
| **프론트엔드** | http://localhost:3000 | 웹 대시보드 UI |
| **백엔드 API** | http://localhost:3000/api | API 프록시 레이어 |
| **Mock API** | http://localhost:8000 | TapaCross OracleEye Mock |

---

## Swagger / API 문서

FastAPI가 자동으로 Swagger 문서를 생성합니다:

| 문서 | URL |
|------|-----|
| **Mock API - Swagger UI** | http://localhost:8000/docs |
| **Mock API - ReDoc** | http://localhost:8000/redoc |
| **백엔드 - Swagger UI** | http://localhost:3000/docs |
| **백엔드 - ReDoc** | http://localhost:3000/redoc |

Swagger UI에서 "Try it out" 버튼을 누르면 파라미터를 채우고 바로 API를 호출해볼 수 있습니다.

---

## API 엔드포인트

### Mock API (포트 8000)

#### `GET /v1/oracleye/trend` — 트렌드 데이터

소스 타입별 일별 문서 수를 반환합니다.

| 파라미터 | 필수 | 포맷 | 설명 |
|----------|------|------|------|
| `client_id` | O | string | API 클라이언트 식별자 |
| `search_id` | O | integer | 검색 설정 ID |
| `from` | O | `yyyyMMddHHmmss` | 시작 일시 |
| `to` | O | `yyyyMMddHHmmss` | 종료 일시 |
| `site_type` | X | string | 필터: `media`, `comm`, `twitter`, `youtube` |

**응답 예시:**
```json
{
  "status": "success",
  "data": [
    { "create_date": "20260208", "site_type": "media", "doc_count": 15 },
    { "create_date": "20260208", "site_type": "twitter", "doc_count": 42 }
  ]
}
```

#### `GET /v1/oracleye/doc` — 문서(게시글) 데이터

개별 문서(뉴스, 트윗, 영상, 커뮤니티 글)를 반환합니다.

| 파라미터 | 필수 | 기본값 | 설명 |
|----------|------|--------|------|
| `client_id` | O | — | API 클라이언트 식별자 |
| `search_id` | O | — | 검색 설정 ID |
| `from` | O | — | 시작 일시 (`yyyyMMddHHmmss`) |
| `to` | O | — | 종료 일시 (`yyyyMMddHHmmss`) |
| `site_type` | X | — | 필터: `media`, `comm`, `twitter`, `youtube` |
| `offset` | X | `0` | 페이지네이션 오프셋 |
| `size` | X | `100` | 한 페이지당 결과 수 |

> **감성 분석 (polarity):** `"0"` = 중립, `"1"` = 긍정, `"2"` = 부정

### 백엔드 (포트 3000)

| 엔드포인트 | 설명 | 주요 파라미터 |
|------------|------|---------------|
| `GET /api/trend` | 트렌드 데이터 (간소화된 파라미터) | `from_date`, `to_date`, `site_type` |
| `GET /api/documents` | 문서 목록 (페이지네이션) | `from_date`, `to_date`, `site_type`, `offset`, `size` |
| `GET /` | 프론트엔드 정적 파일 서빙 | — |

---

## 프로젝트 구조

```
mock_api/
├── docker-compose.yml         # 서비스 오케스트레이션
├── Dockerfile.mock-api        # Mock API 컨테이너 (Python 3.12)
├── Dockerfile.backend         # 백엔드 컨테이너 (Python 3.12)
├── requirements.txt           # Python 의존성
│
├── mock_api/                  # Mock API 애플리케이션
│   ├── main.py                # FastAPI 앱 초기화 + CORS 설정
│   ├── models.py              # Pydantic 응답 모델 (TrendItem, DocItem)
│   ├── data_store.py          # JSON 데이터 로딩 + 쿼리/필터 로직
│   └── routers/
│       ├── trend.py           # GET /v1/oracleye/trend
│       └── doc.py             # GET /v1/oracleye/doc
│
├── backend/                   # 백엔드 프록시
│   ├── app.py                 # FastAPI 앱 + 정적 파일 서빙
│   ├── api_client.py          # Mock API 호출용 httpx 클라이언트
│   └── config.py              # 환경변수 기반 설정 (URL 교체 포인트)
│
├── frontend/                  # 웹 대시보드
│   ├── index.html             # 메인 UI (날짜 선택, 필터, 테이블)
│   ├── js/app.js              # Chart.js 트렌드 그래프 + 문서 테이블
│   └── css/style.css          # 스타일
│
├── converter/                 # 데이터 파이프라인
│   └── convert_excel.py       # 엑셀 → JSON 변환기
│
└── data/converted/            # 변환된 Mock 데이터
    ├── trend_data.json        # 일별 집계 데이터
    └── all_documents.json     # 개별 문서 데이터
```

---

## 데이터 소스

4개의 엑셀 파일에서 변환된 Mock 데이터 (기간: **2026-02-08 ~ 2026-02-12**):

| 소스 파일 | `site_type` | 설명 |
|-----------|-------------|------|
| X(트위터).xlsx | `twitter` | 트위터/X 게시글 |
| 매스미디어.xlsx | `media` | 매스미디어 뉴스 |
| 유튜브 스크립트.xlsx | `youtube` | 유튜브 영상 스크립트 |
| 커뮤니티.xlsx | `comm` | 커뮤니티 게시글 |

엑셀 데이터를 업데이트한 후 JSON을 재생성하려면:

```bash
python converter/convert_excel.py
```

---

## 프로덕션 전환 방법

실제 TapaCross API가 준비되면, **환경변수 하나만 변경**:

```yaml
# docker-compose.yml
environment:
  - TAPACROSS_API_URL=https://real-tapacross-api.example.com  # 기존: http://mock-api:8000
```

코드 수정 없음. 백엔드 프록시 레이어가 나머지를 처리합니다.

---

## 기술 스택

| 레이어 | 기술 | 선택 이유 |
|--------|------|-----------|
| API | FastAPI (Python 3.12) | OpenAPI 문서 자동 생성, 비동기 지원, 빠름 |
| 서버 | Uvicorn | 고성능 ASGI 서버 |
| HTTP 클라이언트 | httpx | 비동기 HTTP 클라이언트 (백엔드 → API 호출) |
| 차트 | Chart.js 4.4.7 | 빌드 스텝 없이 간단한 차트 구현 |
| 프론트엔드 | Vanilla HTML/CSS/JS | 빌드 복잡도 제로, 누구나 바로 이해 가능 |
| 컨테이너 | Docker Compose | 한 줄 명령으로 전체 스택 구동 |
| 데이터 변환 | openpyxl | 엑셀 → JSON 변환 파이프라인 |
