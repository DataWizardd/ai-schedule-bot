# app/bot/handlers.py
from __future__ import annotations

import datetime
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import ContextTypes


def _dday_text(date_str: str) -> str:
    today = datetime.date.today()
    target = datetime.date.fromisoformat(date_str)
    delta = (target - today).days
    if delta == 0:
        return "(D-DAY)"
    return f"(D-{delta})" if delta > 0 else f"(D+{abs(delta)})"


def _offset_label(offset_minutes: int) -> str:
    if offset_minutes == 0:
        return "정각"
    if offset_minutes == 30:
        return "30분 전"
    if offset_minutes == 60:
        return "1시간 전"
    if offset_minutes == 1440:
        return "하루 전 09:00"
    if offset_minutes % 1440 == 0:
        d = offset_minutes // 1440
        return f"{d}일 전"
    if offset_minutes % 60 == 0:
        h = offset_minutes // 60
        return f"{h}시간 전"
    return f"{offset_minutes}분 전"


class Handlers:
    def __init__(self, repo, ai, kparser, reminder):
        self.repo = repo
        self.ai = ai
        self.kparser = kparser
        self.reminder = reminder

    # ====== 메뉴 (ReplyKeyboard + InlineKeyboard) ======
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_kb = ReplyKeyboardMarkup(
            [
                [KeyboardButton("/add"), KeyboardButton("/list")],
                [KeyboardButton("/today"), KeyboardButton("/remind")],
                [KeyboardButton("/reminders"), KeyboardButton("/delete_all")],
                [KeyboardButton("/menu")],
            ],
            resize_keyboard=True,
        )
        await update.message.reply_text("원하는 작업을 선택하세요 👇", reply_markup=reply_kb)
        await self.menu(update, context)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("➕ 일정 추가", callback_data="go:add")],
                [
                    InlineKeyboardButton("📋 전체 일정", callback_data="go:list"),
                    InlineKeyboardButton("📅 오늘 일정", callback_data="go:today"),
                ],
                [
                    InlineKeyboardButton("🔔 알림 프리셋", callback_data="go:remind"),
                    InlineKeyboardButton("⏰ 알림 목록", callback_data="go:reminders"),
                ],
                [InlineKeyboardButton("🧹 전체 삭제", callback_data="confirm:delete_all")],
            ]
        )
        msg = "메뉴를 선택하세요:"
        if getattr(update, "message", None):
            await update.message.reply_text(msg, reply_markup=kb)
        else:
            await update.effective_message.reply_text(msg, reply_markup=kb)

    # ====== 일정 추가 (/add: 항상 AI 경유) ======
    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "사용법: /add [자연어 일정]\n예) /add 다음주 월 10시 고객 미팅"
            )
            return

        text = " ".join(context.args)
        if self.ai.available():
            sch = self.ai.parse_with_ai(text)
            sid = self.repo.add(
                update.effective_user.id, sch.title, sch.description, sch.date, sch.time
            )
            dday = _dday_text(sch.date)
            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔔 알림 설정", callback_data=f"rmenu:{sid}"),
                        InlineKeyboardButton("🗑 되돌리기", callback_data=f"del:{sid}"),
                    ]
                ]
            )
            await update.message.reply_text(
                f"등록 완료: {sch.date} {sch.time or '시간 미정'} {sch.title} {dday}",
                reply_markup=kb,
            )
        else:
            title, time, date = self.kparser.parse(text)
            sid = self.repo.add(update.effective_user.id, title, "", date, time)
            dday = _dday_text(date)
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔔 알림 설정", callback_data=f"rmenu:{sid}")]]
            )
            await update.message.reply_text(
                f"등록 완료: {date} {time or '시간 미정'} {title} {dday}",
                reply_markup=kb,
            )

    async def list_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        rows = self.repo.list_all(update.effective_user.id)
        if not rows:
            await update.message.reply_text("등록된 일정이 없습니다.")
            return

        lines, kb_rows = [], []
        for sid, title, desc, dt, tm in rows[:10]:
            dday = _dday_text(dt)
            lines.append(f"• {dt} {tm or ''} {title} {dday}")
            kb_rows.append(
                [
                    InlineKeyboardButton("🔔 알림", callback_data=f"rmenu:{sid}"),
                    InlineKeyboardButton("ℹ️ 상세", callback_data=f"view:{sid}"),
                    InlineKeyboardButton("🗑 삭제", callback_data=f"del:{sid}"),
                ]
            )

        await update.message.reply_text(
            "\n".join(lines), reply_markup=InlineKeyboardMarkup(kb_rows)
        )

    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        rows = self.repo.today(update.effective_user.id, today_str)
        if not rows:
            await update.message.reply_text("오늘 일정 없음")
            return

        lines, kb_rows = [], []
        for sid, title, desc, dt, tm in rows:
            dday = _dday_text(dt)
            lines.append(f"• {tm or ''} {title} {dday}")
            kb_rows.append(
                [
                    InlineKeyboardButton("🔔 알림", callback_data=f"rmenu:{sid}"),
                    InlineKeyboardButton("🗑 삭제", callback_data=f"del:{sid}"),
                ]
            )

        await update.message.reply_text(
            "\n".join(lines), reply_markup=InlineKeyboardMarkup(kb_rows)
        )

    # ====== 삭제 ======
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("사용법: /delete [id]")
            return
        try:
            sid = int(context.args[0])
        except ValueError:
            await update.message.reply_text("올바른 숫자 ID를 입력하세요.")
            return

        try:
            self.repo.delete_reminders_for_schedule(update.effective_user.id, sid)
        except Exception:
            pass

        ok = self.repo.delete(update.effective_user.id, sid)
        await update.message.reply_text("삭제 완료" if ok else "삭제 실패/권한 없음")

    async def delete_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        cnt = self.repo.delete_all(update.effective_user.id)
        await update.message.reply_text(f"전체 삭제 완료 ({cnt}건)")

    # ====== 알림: 자연어/프리셋 ======
    async def remind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "매일 09:00 오늘 일정", callback_data="rem:daily:09:00:오늘 일정"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "매주 월 08:30 이번주 요약",
                            callback_data="remw:0:08:30:이번주 일정",
                        )
                    ],
                ]
            )
            await update.message.reply_text(
                "자연어로도 등록 가능: 예) /remind 매주 금요일 09:00 오늘 일정",
                reply_markup=kb,
            )
            return

        text = " ".join(context.args)
        try:
            job_info = await self.reminder.schedule_custom(update.effective_user.id, text)
            await update.message.reply_text(f"알림 등록 완료: {job_info}")
        except ValueError as e:
            await update.message.reply_text(f"알림 파싱 실패: {e}")

    # ====== 알림 목록/관리 ======
    async def reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        rows = self.repo.list_reminders_detailed(update.effective_user.id)
        if not rows:
            await update.message.reply_text("등록된 알림이 없습니다.")
            return

        # 묶어서 보여주되, 각 알림별 관리 버튼 제공
        lines = []
        kb_rows = []
        for rid, sid, off, title, desc, dt, tm in rows[:12]:
            dday = _dday_text(dt)
            label = _offset_label(off)
            time_part = tm or "시간 미정"
            lines.append(f"• {dt} {time_part} {title} {dday}  —  [{label}]")
            kb_rows.append(
                [
                    InlineKeyboardButton("🗑 알림삭제", callback_data=f"rdel:{rid}"),
                    InlineKeyboardButton("ℹ️ 일정보기", callback_data=f"view:{sid}"),
                    # InlineKeyboardButton("🗑 일정 알림 전체삭제", callback_data=f"rdelall:{sid}"),
                ]
            )

        # 마지막 줄에 새로고침/닫기
        kb_rows.append(
            [
                InlineKeyboardButton("🔄 새로고침", callback_data="rlist"),
                InlineKeyboardButton("닫기", callback_data="go:menu"),
            ]
        )

        await update.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb_rows))

    # ====== 콜백 처리 ======
    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        data = q.data or ""

        # 알림 설정 메뉴
        if data.startswith("rmenu:"):
            sid = int(data.split(":")[1])
            kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("⏰ 일정 시간", callback_data=f"rset:{sid}:0")],
                    [
                        InlineKeyboardButton("🕧 30분 전", callback_data=f"rset:{sid}:30"),
                        InlineKeyboardButton("🕐 1시간 전", callback_data=f"rset:{sid}:60"),
                    ],
                    [InlineKeyboardButton("🌙 하루 전 09:00", callback_data=f"rset:{sid}:1440")],
                    [InlineKeyboardButton("❌ 닫기", callback_data="go:menu")],
                ]
            )
            await q.edit_message_text("알림 시점을 선택하세요:", reply_markup=kb)
            return

        # 알림 설정 적용
        if data.startswith("rset:"):
            _, sid, off = data.split(":")
            sid = int(sid)
            offset = int(off)
            row = self.repo.get(q.from_user.id, sid)
            if not row:
                await q.edit_message_text("해당 일정을 찾을 수 없습니다.")
                return
            await self.reminder.schedule_for_schedule(q.from_user.id, row, offset)
            await q.edit_message_text(f"알림 설정 완료: {_offset_label(offset)}")
            return

        # 알림 목록 새로고침
        if data == "rlist":
            fake_update = Update(update.update_id, message=update.effective_message)
            await self.reminders(fake_update, context)
            return

        # 알림 단건 삭제
        if data.startswith("rdel:"):
            rid = int(data.split(":")[1])
            ok = self.repo.delete_reminder(q.from_user.id, rid)
            await q.edit_message_text("알림 삭제 완료" if ok else "알림 삭제 실패/권한 없음")
            return

        # 특정 일정의 모든 알림 삭제
        if data.startswith("rdelall:"):
            sid = int(data.split(":")[1])
            self.repo.delete_reminders_for_schedule(q.from_user.id, sid)
            await q.edit_message_text("해당 일정의 알림을 모두 삭제했습니다.")
            return

        # 일정 삭제
        if data.startswith("del:"):
            sid = int(data.split(":")[1])
            try:
                self.repo.delete_reminders_for_schedule(q.from_user.id, sid)
            except Exception:
                pass
            ok = self.repo.delete(q.from_user.id, sid)
            await q.edit_message_text("삭제 완료" if ok else "삭제 실패/권한 없음")
            return

        # 상세 보기
        if data.startswith("view:"):
            sid = int(data.split(":")[1])
            row = self.repo.get(q.from_user.id, sid)
            if not row:
                await q.edit_message_text("해당 일정을 찾을 수 없습니다.")
                return
            _, title, desc, dt, tm = row
            dday = _dday_text(dt)
            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔔 알림", callback_data=f"rmenu:{sid}"),
                        InlineKeyboardButton("🗑 삭제", callback_data=f"del:{sid}"),
                    ]
                ]
            )
            await q.edit_message_text(
                f"📅 {dt} {tm or ''}\n📝 {title}\n{desc or ''}\n{dday}", reply_markup=kb
            )
            return

        # 메뉴 라우팅
        if data == "go:add":
            await q.edit_message_text("일정을 자연어로 입력해주세요.\n예) 다음주 월 10시 고객 미팅")
            return

        if data == "go:list":
            fake_update = Update(update.update_id, message=update.effective_message)
            await self.list_all(fake_update, context)
            return

        if data == "go:today":
            fake_update = Update(update.update_id, message=update.effective_message)
            await self.today(fake_update, context)
            return

        if data == "go:remind":
            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "매일 09:00 오늘 일정", callback_data="rem:daily:09:00:오늘 일정"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "매주 월 08:30 이번주 요약",
                            callback_data="remw:0:08:30:이번주 일정",
                        )
                    ],
                    [InlineKeyboardButton("⏰ 알림 목록 보기", callback_data="rlist")],
                ]
            )
            await q.edit_message_text("알림 프리셋:", reply_markup=kb)
            return

        # 자연어 알림 프리셋
        if data.startswith("rem:"):
            _, mode, hm, msg = data.split(":", 3)
            hh, mm = map(int, hm.split(":"))
            await self.reminder.schedule_custom(
                q.from_user.id, f"매일 {hh:02d}:{mm:02d} {msg}"
            )
            await q.edit_message_text("알림 등록 완료")
            return

        if data.startswith("remw:"):
            _, wd, hh, mm, msg = data.split(":", 4)
            wd = int(wd)
            await self.reminder.schedule_custom(
                q.from_user.id, f"매주 {'월화수목금토일'[wd]} {hh}:{mm} {msg}"
            )
            await q.edit_message_text("알림 등록 완료")
            return

        # 전체 삭제 확인 & 실행
        if data == "confirm:delete_all":
            kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("✅ 예, 모두 삭제", callback_data="do:delete_all")],
                    [InlineKeyboardButton("❌ 취소", callback_data="go:menu")],
                ]
            )
            await q.edit_message_text("정말 모든 일정을 삭제할까요?", reply_markup=kb)
            return

        if data == "do:delete_all":
            cnt = self.repo.delete_all(q.from_user.id)
            await q.edit_message_text(f"전체 삭제 완료 ({cnt}건)")
            return

        if data == "go:menu":
            await self.menu(update, context)
            return
