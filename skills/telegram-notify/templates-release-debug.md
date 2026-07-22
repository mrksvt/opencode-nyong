# Telegram Message Templates — Release & Debug

Template format pesan untuk notifikasi release dan debug via Telegram Bot API.

## Config

```bash
export TELEGRAM_BOT_TOKEN="<your-bot-token>"
export TELEGRAM_CHAT_ID="<your-chat-id>"
```

## Format Pesan Release

### Release Started
```
🚀 <b>RELEASE STARTED</b>

📦 <b>Version:</b> v1.2.3
🌿 <b>Branch:</b> main
👤 <b>Author:</b> @username
🕐 <b>Time:</b> 2026-07-19 10:30:00

📋 <b>Changelog:</b>
• feat: new camera filter
• fix: audio stream crash
• perf: reduce GPU memory usage
```

### Release Success
```
✅ <b>RELEASE SUCCESS</b>

📦 <b>Version:</b> v1.2.3
🏷️ <b>Tag:</b> v1.2.3
📍 <b>Commit:</b> abc1234
🕐 <b>Duration:</b> 2m 34s

📊 <b>Build Info:</b>
• APK Size: 12.4 MB
• Min SDK: 24
• Target SDK: 34

🔗 <b>Artifacts:</b>
• app-release.apk
• mapping.txt
```

### Release Failed
```
❌ <b>RELEASE FAILED</b>

📦 <b>Version:</b> v1.2.3
📍 <b>Stage:</b> build | test | deploy
🕐 <b>Duration:</b> 1m 12s

💥 <b>Error:</b>
<code>Execution failed for task ':app:compileReleaseKotlin'.
> Unresolved reference: FilterPipeline</code>

📋 <b>Last 3 Logs:</b>
<code>> Task :app:compileReleaseKotlin FAILED
> e: MainActivity.kt:142: Unresolved reference
> BUILD FAILED in 1m 12s</code>

🔗 <b>Full Log:</b> https://ci.example.com/build/123
```

## Format Pesan Debug

### Debug Session Started
```
🔍 <b>DEBUG SESSION STARTED</b>

🐛 <b>Issue:</b> Camera preview black screen
📱 <b>Device:</b> Pixel 7 (API 34)
🌿 <b>Branch:</b> fix/camera-preview
👤 <b>Investigator:</b> @username

📋 <b>Symptoms:</b>
• Preview shows black after switching camera
• Works on first launch, fails on resume
• Affects front camera only
```

### Debug Step Completed
```
🔧 <b>DEBUG STEP</b> [2/4]

📍 <b>Phase:</b> Isolate
✅ <b>Done:</b> Reproduced on emulator
⏳ <b>Next:</b> Check CameraX lifecycle

💡 <b>Finding:</b>
Camera not re-binding after pause/resume cycle.
SurfaceProvider detached but not re-attached.

📁 <b>Files:</b>
• MainActivity.kt:234 — camera bind logic
• CameraManager.kt:89 — lifecycle observer
```

### Debug Root Cause Found
```
🎯 <b>ROOT CAUSE FOUND</b>

🐛 <b>Issue:</b> Camera preview black screen
📍 <b>Location:</b> MainActivity.kt:234
⏱️ <b>Time to Find:</b> 45 minutes

💥 <b>Root Cause:</b>
<code>CameraX.unbindAll() called in onPause()
but not re-bound in onResume() when
switching between front/back camera.</code>

🔧 <b>Fix:</b>
<code>override fun onResume() {
    super.onResume()
    if (isCameraSwitched) {
        bindCameraUseCases()
        isCameraSwitched = false
    }
}</code>

📁 <b>Affected Files:</b>
• MainActivity.kt — camera lifecycle
• CameraManager.kt — bind logic
```

### Debug Fix Verified
```
✅ <b>DEBUG FIX VERIFIED</b>

🐛 <b>Issue:</b> Camera preview black screen
📍 <b>Fix:</b> MainActivity.kt:234-245
🧪 <b>Tests:</b> 15/15 passed

📱 <b>Verified On:</b>
• Pixel 7 (API 34) ✅
• Samsung S23 (API 33) ✅
• Emulator (API 24) ✅

📊 <b>Impact:</b>
• No regression detected
• Performance: +2ms bind time (acceptable)
• Memory: no leak

🔗 <b>PR:</b> #142 — fix/camera-preview
```

### Debug Failed (Give Up)
```
⚠️ <b>DEBUG ESCALATED</b>

🐛 <b>Issue:</b> GPU filter memory leak
⏱️ <b>Time Spent:</b> 2 hours
🔄 <b>Attempts:</b> 3/3

📋 <b>What We Tried:</b>
1. ❌ Force GLContext cleanup — leak persists
2. ❌ Reduce texture cache size — still leaking
3. ❌ Replace FilterPipeline with stub — leak gone

💡 <b>Isolation:</b>
Leak originates in FilterManager.createTexture()
but GLTextureView lifecycle looks correct.

📁 <b>Evidence:</b>
• Heap dump: 47 leaked GL textures
• Allocation site: FilterManager.kt:156
• Retained by: GLTextureView.mSurface

🆘 <b>Next Steps:</b>
• Check OpenGL driver bug on Adreno 740
• Try alternative texture management
• Escalate to graphics team
```

## Usage Examples

### Bash — Send Release Success
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"${TELEGRAM_CHAT_ID}\",
    \"text\": \"✅ <b>RELEASE SUCCESS</b>\n\n📦 <b>Version:</b> v1.2.3\n🏷️ <b>Tag:</b> v1.2.3\n📍 <b>Commit:</b> abc1234\n🕐 <b>Duration:</b> 2m 34s\n\n📊 <b>Build Info:</b>\n• APK Size: 12.4 MB\n• Min SDK: 24\n• Target SDK: 34\",
    \"parse_mode\": \"HTML\"
  }"
```

### Bash — Send Debug Root Cause
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"${TELEGRAM_CHAT_ID}\",
    \"text\": \"🎯 <b>ROOT CAUSE FOUND</b>\n\n🐛 <b>Issue:</b> Camera preview black screen\n📍 <b>Location:</b> MainActivity.kt:234\n⏱️ <b>Time to Find:</b> 45 minutes\n\n💥 <b>Root Cause:</b>\n<code>CameraX.unbindAll() called in onPause()\nbut not re-bound in onResume()</code>\n\n🔧 <b>Fix:</b>\n<code>override fun onResume() {\n    super.onResume()\n    bindCameraUseCases()\n}</code>\",
    \"parse_mode\": \"HTML\"
  }"
```

## Guidelines

- **HTML parse_mode** — untuk formatting bold/code/italic
- **Code blocks** — gunakan `<code>` untuk error messages dan snippets
- **Emoji** — konsisten: 🚀 start, ✅ success, ❌ fail, 🔍 debug, 🎯 found
- **Structure** — field:value untuk metadata, bullet points untuk lists
- **Length** — max 4096 chars Telegram limit, truncate logs jika perlu
- **No secrets** — jangan kirim token, password, atau API keys
