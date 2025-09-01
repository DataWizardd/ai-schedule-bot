from telegram.ext import ApplicationBuilder
print("building...")
app = ApplicationBuilder().token("123456789:INVALID_TOKEN_FOR_SMOKETEST").build()
print("OK: Application built (token invalid is fine)")
