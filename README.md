# 🤖 AI-Powered Telegram Schedule Bot

> **한국어 자연어로 일정을 관리하고 AI가 스마트하게 도와주는 텔레그램 봇**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT%204-10A74F.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 주요 기능

### 🎯 **스마트 일정 관리**
- **자연어 입력**: "내일 오후 3시에 회의" 같은 한국어로 일정 추가
- **AI 파싱**: OpenAI GPT로 복잡한 일정 정보 자동 추출
- **스마트 제안**: AI가 일정 시간과 우선순위를 제안
- **충돌 분석**: 일정 간 시간 충돌 자동 감지

### 🔔 **알림 시스템**
- **매일 리마인더**: 오늘의 일정을 아침에 자동 알림
- **즉시 알림**: 일정 추가 시 즉시 확인 메시지
- **개인화**: 사용자별 맞춤 알림 설정

### 🛠 **사용자 친화적 인터페이스**
- **인라인 키보드**: 직관적인 버튼 기반 조작
- **한국어 지원**: 완전한 한국어 인터페이스
- **간편한 명령어**: `/add`, `/list`, `/today` 등 직관적인 명령

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/DataWizardd/ai-schedule-bot.git
cd ai-schedule-bot
```

### 2. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_PATH=data/schedules.db
```

### 5. 봇 실행
```bash
python app/main.py
```

## 📱 사용법

### 기본 명령어
| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/start` | 봇 시작 및 도움말 | `/start` |
| `/add` | 일정 추가 | `/add 내일 오후 3시 회의` |
| `/add_ai` | AI로 일정 추가 | `/add_ai 다음주 월요일 오전 10시 팀 미팅` |
| `/list` | 전체 일정 목록 | `/list` |
| `/today` | 오늘 일정 확인 | `/today` |
| `/delete` | 일정 삭제 | `/delete` |
| `/suggest` | AI 일정 제안 | `/suggest` |
| `/analyze` | 일정 충돌 분석 | `/analyze` |

### AI 기능 사용법

#### 🧠 **스마트 일정 추가**
```
/add_ai 다음주 월요일 오전 10시에 팀 미팅, 중요도 높음
```
AI가 자동으로:
- 날짜: 다음주 월요일 → 2024-01-15
- 시간: 오전 10시 → 10:00
- 우선순위: 중요도 높음 → high
- 카테고리: 팀 미팅 → work

#### 💡 **일정 제안**
```
/suggest
```
AI가 현재 상황을 분석하여:
- 최적의 일정 시간 제안
- 우선순위 기반 스케줄링
- 개인 패턴 학습

#### ⚠️ **충돌 분석**
```
/analyze
```
AI가 일정 간:
- 시간 충돌 감지
- 해결 방안 제시
- 일정 재배치 제안

## 🏗️ 프로젝트 구조

```
ai-schedule-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # 🚀 엔트리포인트
│   ├── config.py            # ⚙️ 설정/환경변수
│   ├── logging_conf.py      # 📝 로깅 설정
│   ├── domain/              # 🏛️ 도메인 모델
│   │   ├── schedule.py      # 📅 일정 모델
│   │   └── suggestion.py    # 💡 제안 모델
│   ├── storage/             # 💾 저장소 계층
│   │   ├── db.py           # 🗄️ SQLite 연결
│   │   └── schedule_repo.py # 📊 일정 CRUD
│   ├── services/            # 🔧 비즈니스 로직
│   │   ├── timeutil.py     # ⏰ KST/상대날짜
│   │   ├── kdate_parser.py # 🇰🇷 한국어 파서
│   │   ├── ai_client.py    # 🤖 OpenAI 클라이언트
│   │   ├── ai_schedule_parser.py # 🧠 AI 파서
│   │   ├── reminder.py     # 🔔 리마인더 서비스
│   │   └── cache.py        # 🚀 제안 캐시
│   └── bot/                # 🤖 텔레그램 봇
│       ├── builder.py      # 🏗️ 앱 구성
│       ├── handlers.py     # 📱 명령어 핸들러
│       └── keyboards.py    # ⌨️ 인라인 키보드
├── .env.example            # 📋 환경변수 예시
├── requirements.txt        # 📦 의존성 목록
├── README.md              # 📖 프로젝트 문서
└── .gitignore             # 🚫 Git 제외 파일
```

## 🛠️ 기술 스택

### **Backend**
- **Python 3.8+**: 메인 프로그래밍 언어
- **python-telegram-bot**: 텔레그램 봇 API
- **SQLite**: 로컬 데이터베이스
- **APScheduler**: 비동기 스케줄링

### **AI & NLP**
- **OpenAI GPT-4**: 자연어 처리 및 일정 파싱
- **Pydantic**: 데이터 검증 및 모델링
- **한국어 규칙 기반 파서**: 기본 날짜/시간 파싱

### **Architecture**
- **Clean Architecture**: 도메인 중심 설계
- **Repository Pattern**: 데이터 접근 추상화
- **Service Layer**: 비즈니스 로직 분리
- **Dependency Injection**: 느슨한 결합

## 🔧 설정 옵션

### 환경변수
| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `BOT_TOKEN` | 텔레그램 봇 토큰 | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | - | ✅ |
| `DATABASE_PATH` | 데이터베이스 경로 | `data/schedules.db` | ❌ |

### 데이터베이스 스키마
```sql
-- 사용자 테이블
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY
);

-- 일정 테이블
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    schedule_date TEXT NOT NULL,
    schedule_time TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 배포 가이드

### 1. **로컬 개발**
```bash
python app/main.py
```

### 2. **서버 배포**
```bash
# 서버에 코드 업로드
git clone https://github.com/DataWizardd/ai-schedule-bot.git

# 환경변수 설정
nano .env

# 의존성 설치
pip install -r requirements.txt

# 백그라운드 실행
nohup python app/main.py > bot.log 2>&1 &
```

### 3. **Docker 배포** (선택사항)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app/main.py"]
```

## 🧪 테스트

### 단위 테스트
```bash
# 테스트 실행
python -m pytest tests/

# 커버리지 확인
python -m pytest --cov=app tests/
```

### 통합 테스트
```bash
# 봇 기능 테스트
python test_bot.py
```
