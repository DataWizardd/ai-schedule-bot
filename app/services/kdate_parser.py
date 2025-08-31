import regex as re
import pendulum
from typing import Optional, Tuple

class KDateParser:
    def __init__(self, tz: str = "Asia/Seoul"):
        self.tz = tz

    def parse(self, text: str) -> Tuple[str, Optional[str], str]:
        """return (title, time, date) title은 본문 정리용에서 사용 안 하니 date/time만 주로"""
        today = pendulum.now(self.tz).date()
        date = self._extract_date(text, today)
        time = self._extract_time(text)
        clean = self._remove_date_time(text)
        title, desc = self._split_title_desc(clean)
        return title or "일정", time, date

    def _extract_date(self, text: str, today) -> str:
        t = text
        # 상대표현
        patterns = [
            (r"(오늘)", 0),
            (r"(내일)", 1),
            (r"(모레)", 2),
            (r"(어제)", -1),
        ]
        for pat, delta in patterns:
            if re.search(pat, t):
                return today.add(days=delta).to_date_string()

        # YYYY-MM-DD
        m = re.search(r"(\d{4})[./-]\s?(\d{1,2})[./-]\s?(\d{1,2})", t)
        if m:
            y, mo, d = map(int, m.groups())
            return pendulum.date(y, mo, d).to_date_string()

        # M월 D일
        m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
        if m:
            mo, d = map(int, m.groups())
            y = today.year + (1 if mo < today.month else 0)
            return pendulum.date(y, mo, d).to_date_string()

        # D일
        m = re.search(r"(\d{1,2})\s*일", t)
        if m:
            d = int(m.group(1))
            y, mo = today.year, today.month
            try:
                return pendulum.date(y, mo, d).to_date_string()
            except Exception:
                mo = 1 if mo == 12 else mo + 1
                y = y + 1 if mo == 1 else y
                return pendulum.date(y, mo, d).to_date_string()

        return today.to_date_string()

    def _extract_time(self, text: str) -> Optional[str]:
        t = text
        if re.search(r"정오", t):
            return "12:00"
        if re.search(r"자정", t):
            return "00:00"

        # 오전/오후 H시 M분
        m = re.search(r"(오전|오후)\s*(\d{1,2})\s*시\s*(\d{1,2})?\s*분?", t)
        if m:
            ap, h, mm = m.groups()
            h = int(h); mm = int(mm) if mm else 0
            if ap == "오후" and h != 12: h += 12
            if ap == "오전" and h == 12: h = 0
            return f"{h:02d}:{mm:02d}"

        # H시 M분
        m = re.search(r"(\d{1,2})\s*시\s*(\d{1,2})\s*분?", t)
        if m:
            h, mm = map(int, m.groups())
            return f"{h:02d}:{mm:02d}"

        # 오전/오후 H시
        m = re.search(r"(오전|오후)\s*(\d{1,2})\s*시", t)
        if m:
            ap, h = m.groups()
            h = int(h)
            if ap == "오후" and h != 12: h += 12
            if ap == "오전" and h == 12: h = 0
            return f"{h:02d}:00"

        # H시
        m = re.search(r"(\d{1,2})\s*시", t)
        if m:
            h = int(m.group(1))
            return f"{h:02d}:00"
        return None

    def _remove_date_time(self, text: str) -> str:
        t = re.sub(r"(오늘|내일|모레|어제|이번주|다음주)", " ", text)
        t = re.sub(r"\d{4}[./-]\s?\d{1,2}[./-]\s?\d{1,2}", " ", t)
        t = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일", " ", t)
        t = re.sub(r"\d{1,2}\s*일", " ", t)
        t = re.sub(r"(정오|자정|오전|오후)\s*\d{1,2}\s*시(\s*\d{1,2}\s*분?)?", " ", t)
        t = re.sub(r"\d{1,2}\s*시(\s*\d{1,2}\s*분?)?", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _split_title_desc(self, clean: str):
        if not clean:
            return ("일정", "")
        parts = clean.split(" ", 1)
        title = parts[0]
        desc = parts[1] if len(parts) > 1 else ""
        return (title, desc)
