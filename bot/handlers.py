class Handlers:
    ...
    async def start(self, update, context):
        cmds = ["/add [자연어]", "/add_ai [자연어]", "/list", "/today", "/delete [id]", "/suggest [키워드]", "/analyze"]
        await update.message.reply_text("AI 일정 관리 봇입니다.\n" + "\n".join(cmds))

    async def add(self, update, context):
        if not context.args:
            await update.message.reply_text("사용법: /add [일정]")
            return
        text = " ".join(context.args)
        title, time, date = self.kparser.parse(text)
        sid = self.repo.add(update.effective_user.id, title, "", date, time)
        await update.message.reply_text(f"등록 완료(ID:{sid}) - {date} {time or ''} {title}")

    async def add_ai(self, update, context):
        if not self.ai.ai.available():
            await update.message.reply_text("OpenAI 키가 없어 AI 기능을 사용할 수 없습니다.")
            return
        if not context.args:
            await update.message.reply_text("사용법: /add_ai [일정]")
            return
        text = " ".join(context.args)
        sch = self.ai.parse_with_ai(text)
        sid = self.repo.add(update.effective_user.id, sch.title, sch.description, sch.date, sch.time)
        await update.message.reply_text(f"AI 등록 완료(ID:{sid}) - {sch.date} {sch.time or ''} {sch.title}")
