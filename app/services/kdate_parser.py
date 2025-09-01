# app/services/kdate_parser.py
import re, datetime

class KDateParser:
    def parse(self, text: str):
        today = datetime.date.today()
        norm = re.sub(r"\s+", " ", text).strip()

        # --- 날짜 해석 ---
        date = today
        # 내일모레 / 내일 모레
        if re.search(r"(내일\s*모레|내일모레)", norm):
            date = today + datetime.timedelta(days=2)
        elif "모레" in norm:
            date = today + datetime.timedelta(days=2)
        elif "내일" in norm:
            date = today + datetime.timedelta(days=1)
        elif "오늘" in norm:
            date = today

        # --- 시간 해석 ---
        time = None
        m = re.search(r'오전\s*(\d{1,2})시', norm)
        if m:
            hour = int(m.group(1)) % 12  # 오전 12시는 0시
            time = f"{hour:02d}:00"
        m = re.search(r'오후\s*(\d{1,2})시', norm) if time is None else None
        if m:
            hour = int(m.group(1))
            if hour != 12: hour += 12
            time = f"{hour:02d}:00"
        m = re.search(r'(\d{1,2})시', norm) if time is None else None
        if m and time is None:
            hour = int(m.group(1))
            time = f"{hour:02d}:00"

        # 제목 정리: 날짜/시간 토큰 제거
        title = re.sub(r"(내일\s*모레|내일모레|모레|내일|오늘|오전|오후|\d+시|\d+\s*시)", "", norm)
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            title = "일정"

        return title, time, date.strftime("%Y-%m-%d")
