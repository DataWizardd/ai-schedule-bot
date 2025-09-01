"""
한국 시간대(KST) 및 상대 날짜 유틸리티
"""
import re
import pytz
from datetime import datetime, timedelta, date
from typing import Union, Optional


class KSTTimeUtil:
    """한국 시간대(KST) 유틸리티"""

    KST = pytz.timezone('Asia/Seoul')

    @classmethod
    def now(cls) -> datetime:
        """현재 KST 시간 반환"""
        return datetime.now(cls.KST)

    @classmethod
    def today(cls) -> date:
        """오늘 KST 날짜 반환"""
        return cls.now().date()

    @classmethod
    def to_kst(cls, dt: datetime) -> datetime:
        """datetime을 KST로 변환"""
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.astimezone(cls.KST)

    @classmethod
    def from_kst(cls, dt: datetime) -> datetime:
        """KST datetime을 UTC로 변환"""
        if dt.tzinfo is None:
            dt = cls.KST.localize(dt)
        return dt.astimezone(pytz.UTC)

    @classmethod
    def format_datetime(cls, dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
        """KST datetime을 문자열로 포맷"""
        kst_dt = cls.to_kst(dt) if dt.tzinfo else dt
        return kst_dt.strftime(format_str)

    @classmethod
    def format_date(cls, dt: Union[datetime, date], format_str: str = "%Y-%m-%d") -> str:
        """날짜를 문자열로 포맷"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.strftime(format_str)

    @classmethod
    def parse_datetime(cls, date_str: str, time_str: str = "00:00") -> datetime:
        """날짜와 시간 문자열을 KST datetime으로 파싱"""
        try:
            dt_str = f"{date_str} {time_str}"
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return cls.KST.localize(dt)
        except ValueError:
            raise ValueError(f"잘못된 날짜/시간 형식: {date_str} {time_str}")


def now_kst() -> datetime:
    """현재 KST datetime 반환"""
    return KSTTimeUtil.now()


def today_kst() -> str:
    """현재 KST 기준의 오늘 날짜를 YYYY-MM-DD 문자열로 반환"""
    return KSTTimeUtil.format_date(KSTTimeUtil.today(), "%Y-%m-%d")


class RelativeDateParser:
    """상대 날짜 파서"""

    @staticmethod
    def parse_relative_date(text: str, base_date: Optional[date] = None) -> Optional[date]:
        """상대 날짜 텍스트를 파싱하여 실제 날짜 반환"""
        if base_date is None:
            base_date = KSTTimeUtil.today()

        text = text.lower().strip()

        # 오늘
        if text in ['오늘', 'today', '금일']:
            return base_date

        # 내일
        if text in ['내일', 'tomorrow', '명일']:
            return base_date + timedelta(days=1)

        # 모레
        if text in ['모레', 'day after tomorrow']:
            return base_date + timedelta(days=2)

        # 어제
        if text in ['어제', 'yesterday']:
            return base_date - timedelta(days=1)

        # 이번 주 (월요일 기준)
        if text in ['이번주', '이번 주', 'this week']:
            days_since_monday = base_date.weekday()
            return base_date - timedelta(days=days_since_monday)

        # 다음 주 (월요일 기준)
        if text in ['다음주', '다음 주', 'next week']:
            days_since_monday = base_date.weekday()
            monday = base_date - timedelta(days=days_since_monday)
            return monday + timedelta(days=7)

        # 이번 달 1일
        if text in ['이번달', '이번 달', 'this month']:
            return base_date.replace(day=1)

        # 다음 달 1일
        if text in ['다음달', '다음 달', 'next month']:
            if base_date.month == 12:
                return base_date.replace(year=base_date.year + 1, month=1, day=1)
            else:
                return base_date.replace(month=base_date.month + 1, day=1)

        # N일 후/전
        day_pattern = r'(\d+)일\s*(후|전)'
        match = re.search(day_pattern, text)
        if match:
            days = int(match.group(1))
            direction = match.group(2)
            return base_date + timedelta(days=days) if direction == '후' else base_date - timedelta(days=days)

        # N주 후/전
        week_pattern = r'(\d+)주\s*(후|전)'
        match = re.search(week_pattern, text)
        if match:
            weeks = int(match.group(1))
            direction = match.group(2)
            return base_date + timedelta(weeks=weeks) if direction == '후' else base_date - timedelta(weeks=weeks)

        return None

    @staticmethod
    def parse_time(text: str) -> Optional[tuple]:
        """시간 텍스트를 파싱하여 (hour, minute) 반환"""
        text = text.lower().strip()

        # 24시간 형식: 14:30, 9:00
        time_pattern = r'(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)

        # 12시간 형식: 오후 2시 30분, 오전 9시
        am_pm_pattern = r'(오전|오후|am|pm)\s*(\d{1,2})시\s*(\d{2})?분?'
        match = re.search(am_pm_pattern, text)
        if match:
            am_pm = match.group(1)
            hour = int(match.group(2))
            minute = int(match.group(3)) if match.group(3) else 0

            if am_pm in ['오후', 'pm'] and hour != 12:
                hour += 12
            elif am_pm in ['오전', 'am'] and hour == 12:
                hour = 0

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)

        # 단순 시간: 2시, 14시
        simple_pattern = r'(\d{1,2})시\s*(\d{2})?분?'
        match = re.search(simple_pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)

        return None


def get_relative_date_info(target_date: date) -> str:
    """목표 날짜에 대한 상대적 정보 반환"""
    today = KSTTimeUtil.today()
    delta = target_date - today

    if delta.days == 0:
        return "오늘"
    elif delta.days == 1:
        return "내일"
    elif delta.days == 2:
        return "모레"
    elif delta.days == -1:
        return "어제"
    elif delta.days > 0:
        if delta.days <= 7:
            return f"{delta.days}일 후"
        else:
            weeks = delta.days // 7
            days = delta.days % 7
            return f"{weeks}주 후" if days == 0 else f"{weeks}주 {days}일 후"
    else:
        abs_days = abs(delta.days)
        if abs_days <= 7:
            return f"{abs_days}일 전"
        else:
            weeks = abs_days // 7
            days = abs_days % 7
            return f"{weeks}주 전" if days == 0 else f"{weeks}주 {days}일 전"
