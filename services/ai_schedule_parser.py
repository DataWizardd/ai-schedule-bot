import json
from typing import Dict, List
from app.domain.schedule import Schedule
from app.domain.suggestion import Suggestion
from app.services.ai_client import AIClient
from app.services.kdate_parser import KDateParser
from app.services.timeutil import today_kst

SYSTEM = (
    "당신은 한국어 자연어를 분석하여 일정 정보를 추출하는 AI 어시스턴트입니다. "
    "반드시 JSON으로만 응답하세요."
)

SCHEDULE_USER_TPL = """
다음 텍스트에서 일정을 추출해 JSON으로만 응답하세요:
텍스트: "{text}"

필수 스키마:
{{
 "title": "일정 제목",
 "description": "일정 설명",
 "date": "YYYY-MM-DD",
 "time": "HH:MM 또는 null",
 "priority": "high|medium|low",
 "category": "work|personal|health|study|meeting|travel|etc",
 "recurring": true/false,
 "recurrence": "daily|weekly|monthly|etc 또는 null"
}}
기본 날짜 타임존은 Asia/Seoul입니다.
"""

SUGGEST_USER_TPL = """
사용자 입력: "{text}"
아래와 같은 연관 일정을 0~5개 제안하고 JSON 배열로만 응답하세요.
배열 원소 스키마:
{{
 "title": "제안 일정 제목",
 "description": "제안 이유",
 "suggested_date": "YYYY-MM-DD",
 "suggested_time": "HH:MM 또는 null",
 "priority": "high|medium|low",
 "category": "work|personal|health|study|etc"
}}
"""

class AIScheduleParser:
    def __init__(self, ai: AIClient, kparser: KDateParser):
        self.ai = ai
        self.kparser = kparser

    def parse_with_ai(self, text: str) -> Schedule:
        # 1) AI 시도
        if self.ai.available():
            raw = self.ai.json_response(
                model="gpt-4o-mini",
                system=SYSTEM,
                user=SCHEDULE_USER_TPL.format(text=text),
                temperature=0.2,
                max_tokens=400
            )
            try:
                sch = Schedule(**raw)
                return sch
            except Exception:
                pass

        # 2) 폴백(규칙 파서)
        title, time, date = self.kparser.parse(text)
        return Schedule(title=title, description="", date=date, time=time)

    def smart_suggestions(self, user_input: str) -> List[Suggestion]:
        if not self.ai.available():
            return []
        raw = self.ai.json_response(
            model="gpt-4o-mini",
            system="당신은 일정 관리 전문가입니다. JSON 배열만 응답하세요.",
            user=SUGGEST_USER_TPL.format(text=user_input),
            temperature=0.5,
            max_tokens=800
        )
        if not isinstance(raw, list):
            return []
        out = []
        for item in raw[:5]:
            try:
                out.append(Suggestion(**item))
            except Exception:
                continue
        return out
