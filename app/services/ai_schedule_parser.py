# app/services/ai_schedule_parser.py
import json, re, datetime
from typing import Optional
from app.services.kdate_parser import KDateParser

KST = datetime.timezone(datetime.timedelta(hours=9))

class ParsedSchedule:
    def __init__(self, title: str, date: str, time: Optional[str], description: str):
        self.title = title
        self.date = date       # YYYY-MM-DD
        self.time = time       # HH:MM or None
        self.description = description

class AIScheduleParser:
    """
    1) OpenAI로 JSON 스키마 강제 파싱 (한국어 자연어 → 구조화)
    2) 모델이 준 날짜/시간을 검증하고 부족하면 보정
    3) 실패하면 규칙 파서(KDateParser)로 폴백
    """
    def __init__(self, ai_client, kparser: KDateParser):
        self.ai = ai_client
        self.kparser = kparser

    def available(self) -> bool:
        return bool(self.ai and self.ai.available)

    def _today_ymd_kst(self) -> str:
        return datetime.datetime.now(tz=KST).date().strftime("%Y-%m-%d")

    def parse_with_ai(self, text: str) -> ParsedSchedule:
        # 기본값
        fallback_title, fallback_time, fallback_date = self.kparser.parse(text)

        if self.available():
            try:
                sys = (
                    "너는 한국어 자연어 일정을 JSON으로 구조화하는 일정 파서야. "
                    "출력은 오직 하나의 JSON 객체만 반환해. 어떠한 설명/문장도 넣지 마. "
                    "규칙:\n"
                    "1) date는 Asia/Seoul 기준 오늘 날짜를 기준으로 해석한 절대 날짜(YYYY-MM-DD)\n"
                    "2) time은 HH:MM(24h) 또는 null\n"
                    "3) title은 간결한 명사형으로(예: '오픽 결과 발표', '고객 미팅')\n"
                    "4) description은 있으면 짧게, 없으면 빈 문자열\n"
                )
                user = (
                    f"오늘(Asia/Seoul) 날짜: {self._today_ymd_kst()}\n"
                    f'사용자 입력: "{text}"\n'
                    "반드시 아래 스키마로만 JSON을 출력하라:\n"
                    '{ "title": "string", "date": "YYYY-MM-DD", "time": "HH:MM" | null, "description": "string" }'
                )

                res = self.ai.chat(
                    [{"role": "system", "content": sys},
                     {"role": "user", "content": user}],
                    model="gpt-4o-mini",
                    temperature=0.1,
                    max_tokens=300,
                )
                content = (res.choices[0].message.content or "").strip()
                m = re.search(r"\{.*\}", content, re.DOTALL)
                data = json.loads(m.group()) if m else {}

                title = (data.get("title") or "").strip() or fallback_title or "일정"
                date = (data.get("date") or "").strip()
                time = data.get("time", None)
                if isinstance(time, str):
                    time = time.strip() or None
                description = (data.get("description") or "").strip()

                # 검증 & 보정
                if not _is_valid_ymd(date):
                    # 모델이 상대일을 놓쳤을 때 대비해 규칙 파서 폴백
                    title2, time2, date2 = self.kparser.parse(text)
                    if not date:
                        date = date2
                    if not title or title == "일정":
                        title = title2
                    if not time:
                        time = time2

                if time and not _is_valid_hm(time):
                    time = None

                # 제목에서 남은 날짜/시간 토큰 제거(모델이 섞어놨을 가능성)
                title = _strip_date_time_tokens(title) or "일정"

                return ParsedSchedule(title=title, date=date, time=time, description=description)
            except Exception:
                pass  # 실패 시 폴백

        # 폴백: 규칙 파서 결과 사용
        return ParsedSchedule(
            title=_strip_date_time_tokens(fallback_title) or "일정",
            date=fallback_date,
            time=fallback_time if _is_valid_hm(fallback_time) else None,
            description=""
        )

def _is_valid_ymd(s: Optional[str]) -> bool:
    if not s: return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except Exception:
        return False

def _is_valid_hm(s: Optional[str]) -> bool:
    if not s: return False
    try:
        datetime.datetime.strptime(s, "%H:%M")
        return True
    except Exception:
        return False

_DATE_TIME_TOKENS = re.compile(
    r"(내일\s*모레|내일모레|모레|내일|오늘|이번주|다음주|오전|오후|\d{1,2}\s*시(\s*\d{1,2}\s*분)?|\d{1,2}:\d{2})"
)

def _strip_date_time_tokens(title: str) -> str:
    t = _DATE_TIME_TOKENS.sub(" ", title or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t
