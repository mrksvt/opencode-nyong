---
name: whatsvault
description: Pipeline WhatsVault (modul Xposed WhatsApp). Subperintah "new" - tambah dukungan versi WhatsApp baru (original + business): pull APK dari HP -> .target/ -> decompile -> diff anchor DexKit -> fallback hook tanpa replace existing -> update arrays.xml -> build -> commit & push -> rebuild -> install. Subperintah "port" - port commit WaEnhancer upstream ke fork: tentukan rentang commit, adaptasi YukiHookAPI ke legacy de.robv.android.xposed, package com.wmods.wppenhacer ke com.mrksvt.waen, verifikasi build, update changelog.txt + FeaturesGap.md, commit & push. Subperintah "release" - publish GitHub Release: build 4 varian (Whatsapp/Business x Debug/Release), susun changelog [FIXED]/[ADDED]/[UPDATED] dari git log antar tag, upload semua APK via gh. Gunakan setiap kali user minta "tambah support versi WhatsApp x.x.x.x", "/whatsvault new 2.26.36.87", "bump WA support", "/whatsvault port", "port upstream WaEnhancer", "sinkron fix upstream", "/whatsvault release", "buat release", "upload release", atau saat WhatsVault menolak WhatsApp terbaru karena unsupported. Panggil dari root repo WhatsVault.
---

# Skill: whatsvault

## Trigger
Tiga subperintah:
- `/whatsvault new <VERSI_WA>` - atau teks bebas "tambah support 2.26.37.5",
  "bump support whatsapp terbaru". Jalankan section "Pipeline new" di bawah.
- `/whatsvault port` - atau "port upstream", "port WaEnhancer", "sinkron
  fix upstream", "tarik perubahan WaEnhancer". Jalankan section "Pipeline
  port" di bawah.
- `/whatsvault release` - atau "buat release", "rilis github", "upload release".
  Jalankan section "Pipeline release" di bawah.

## Prasyarat (cek duluan, gagal -> berhenti + laporan)
- CWD adalah root repo WhatsVault: ada `app/build.gradle.kts` + `AGENTS.md`
  + `app/src/main/java/com/mrksvt/waen/`. Kalau tidak ada, minta user
  `cd` ke repo.
- `adb`, `aapt2`, `baksmali`, `jadx` tersedia. (Cek `which`.)
- Ada remote git `origin`. Cek `git remote -v`.
- `gradle` wrapper executable (`./gradlew`).
- File kunci:
  - `app/src/main/res/values/arrays.xml` (`supported_versions_wpp`,
    `supported_versions_business`)
  - `app/src/main/java/com/mrksvt/waen/xposed/core/devkit/Unobfuscator.kt`
    (DexKit anchor)
  - Baseline pool lama: `.target/wa_last_supported_strings.txt` (opsional,
    dibuat di run pertama jika belum ada).

## Argument parsing
- `<VERSI_WA>` = `x.y.z.w` mis. `2.26.36.87`. Kalau kosong, ambil dari HP
  (`dumpsys package com.whatsapp | grep versionName`).
- Nama prefix entri support = 3 segmen pertama + `.xx` -> `2.26.36.xx`.

## Device availability policy (WAJIB)
Sebelum setiap langkah yang butuh HP, cek `adb devices`. Kalau tidak ada
device:
1. Gunakan tool `question` untuk minta user hubungkan HP (USB debugging on,
   authorize).
2. Tunggu, cek ulang. Ulangi max 3 kali.
3. Setelah 3x gagal tanpa device: hentikan pipeline, laporkan bagian mana
   yang belum selesai, minta user jalankan ulang `/whatsvault new <VER>`
   nanti.
4. Simpan state intermediate ke `.target/wv_state.json` supaya run kedua
   bisa lanjut (pull done, analysis done, build pending, dll).

## Pipeline

### 0. Snapshot state
```bash
mkdir -p .target
python3 ~/.config/opencode/skills/whatsvault/scripts/state.py init <VERSI_WA>
```
(state.py opsional; implement simple if/append.)

### 1. Pull APK WhatsApp dari HP

Cek device + WA terpasang versi target:
```bash
adb devices
adb shell dumpsys package com.whatsapp | grep -E 'versionName|versionCode'
adb shell dumpsys package com.whatsapp.w4b 2>/dev/null | grep -E 'versionName' || echo "no business"
```
Kalau `versionName` di HP **bukan** target user -> laporkan mismatch, tanya
lanjut pakai versi yang terpasang atau user perlu install dulu.

Ambil path base.apk (pakai `split APK` juga untuk w4b):
```bash
PATH_WA=$(adb shell pm path com.whatsapp | awk -F: '{print $2}' | head -1 | tr -d '\r')
adb pull "$PATH_WA" .target/com.whatsapp_<VERSI_WA>_base.apk
PATH_WB=$(adb shell pm path com.whatsapp.w4b 2>/dev/null | awk -F: '{print $2}' | head -1 | tr -d '\r')
[ -n "$PATH_WB" ] && adb pull "$PATH_WB" .target/com.whatsapp.w4b_<VERSI_WA>_base.apk
```

Ukuran ~130MB; verifikasi `ls -l .target/`. Gagal pull = device hilang ->
policy no-device di atas.

### 2. Dekompilasi + dump pool

```bash
# resource string pool
aapt2 dump resources .target/com.whatsapp_<VER>_base.apk > /tmp/arsc_<VER>.txt || \
  aapt dump resources .target/com.whatsapp_<VER>_base.apk > /tmp/arsc_<VER>.txt

# dex string pool (anchor DexKit)
mkdir -p .target/smali_<VER>
python3 ~/.config/opencode/skills/whatsvault/scripts/dex_strings.py \
  .target/com.whatsapp_<VER>_base.apk .target/wa_<VER>_strings.txt

# baseline pool lama (untuk diff)
if [ ! -f .target/wa_last_supported_strings.txt ]; then
  # pakai versi tertinggi yang sudah ada di arrays.xml, cari APK-nya di .target
  echo "baseline belum ada; langkah 3 akan skip diff vs baseline"
fi
```

Full decompile (opsional, lambat ~10-20 menit, hanya bila perlu lihat Java):
```bash
jadx --no-imports --no-res --no-debug-info \
     -d .target/jadx_<VER> .target/com.whatsapp_<VER>_base.apk &
```

### 3. Analisis regresi anchor

Jalankan diff script. Kalau `.target/wa_last_supported_strings.txt` belum
ada, generate dari pool versi tertinggi di `arrays.xml` yang punya APK cache
di `.target/`. Kalau tidak ada sama sekali, operasikan tanpa baseline
(semua literal = NO-BASELINE review manual):
```bash
BASE_OPT=""
[ -f .target/wa_last_supported_strings.txt ] && \
  BASE_OPT=".target/wa_last_supported_strings.txt"
python3 ~/.config/opencode/skills/whatsvault/scripts/check_anchors.py \
  app/src/main/java/com/mrksvt/waen/xposed/core/devkit/Unobfuscator.kt \
  .target/wa_<VER>_strings.txt $BASE_OPT | tee /tmp/anchor_diff_<VER>.txt
echo exit=$?
```
- Exit 0 = clean (semua anchor OK / OK-CONTAINS / DEAD)
- Exit 2 = REGRESSION -> lanjut langkah 4 (tambah fallback)
- Exit 3 = butuh review manual

Untuk setiap REGRESSION literal: buka `Unobfuscator.kt` di baris yang
dilaporkan, baca fungsi `load<...>()` tempat dia dipakai, lalu tentukan
anchor pengganti yang tepat dengan cari string lain yang kemungkinan
besar tetap ada di versi baru. Gunakan `grep -F` ke pool baru. Kalau
tidak yakin, cek smali/jadx decompiled.

### 4. Tambah fallback anchor (JANGAN replace)

Pola yang dipakai repo ini (lihat `loadMediaQualitySelectionMethod`
sebagai referensi): chain `if (found.isEmpty())` dengan anchor kedua,
jangan hapus anchor lama. Anchor lama tetap jalan kalau user downgrade
atau install versi lain.

Bila fitur hanya ter-guard `try/catch` (mis. `VoipCall` class yang sudah
hilang di banyak versi), tidak perlu apa-apa: catch Throwable sudah
meng-handle, itu bukan regresi baru. Konfirmasi dulu dengan cek baseline
pool lama; kalau anchor SUDAH DEAD di baseline, skip.

Contoh transform (pola DexKit `addUsingString` + fallback):
```kotlin
var methodData = bridge.findMethod {
    matcher { addUsingString("OLD_ANCHOR"); /* ... */ }
}
if (methodData.isEmpty()) {
    methodData = bridge.findMethod {
        matcher { addUsingString("NEW_ANCHOR"); /* ... same shape ... */ }
    }
}
```
Setelah semua fallback ditambah, jalankan ulang check_anchors.py sampai
exit != 2.

### 5. Tambah entri array versi support

```bash
python3 ~/.config/opencode/skills/whatsvault/scripts/update_arrays.py \
  app/src/main/res/values/arrays.xml <VERSI_WA>
git diff --stat app/src/main/res/values/arrays.xml
```
Script idempotent, tidak dobel kalau sudah ada.

Update cache baseline pool supaya run berikutnya bandingkan vs versi ini:
```bash
cp .target/wa_<VER>_strings.txt .target/wa_last_supported_strings.txt
```

### 6. Build (kedua flavor)

```bash
./gradlew assembleWhatsappDebug --console=plain
./gradlew assembleBusinessDebug --console=plain 2>&1 | tail -20
```
Kalau flavor Business tidak dipakai (tidak ada perubahan resource khusus
business), tetap jalankan untuk validasi. Timeout 20 menit. BUILD FAILED ->
perbaiki kode, ulangi; jangan commit.

### 7. Commit & push

- Jangan commit artefak `.target/`, `jadx_*`, `smali_*`, `log.txt`,
  `docs/` perubahan whitespace unrelated. Stage eksplisit saja:
  `git add app/src/main/res/values/arrays.xml` + setiap file source yang
  diubah untuk fallback.
- Pesan commit format repo ini (lihat `git log --oneline`):
  `feat: support WhatsApp <VERSI_WA> + <VERSI_WA_BUSINESS (if differs)>`
  Body (opsional) daftar anchor yang ditambah sebagai fallback.
- `git commit -m "..." && git push` (branch aktif: biasanya `main`).
- Push gagal (auth/network): laporkan, user perlu selesaikan manual;
  lanjut ke langkah 8 tetap jalan (hash lokal sudah berubah).

### 8. Rebuild untuk refresh git hash

`app/build.gradle.kts:23` membaca `git rev-parse HEAD` 8 char pertama ->
entry ke `versionName`. Setelah commit di langkah 7, HEAD berubah, jadi
build ulang agar APK memuat hash baru:
```bash
./gradlew assembleWhatsappDebug --console=plain
```
APK keluaran:
`app/build/outputs/apk/whatsapp/debug/WhatsVault-<v> (<HASH>)_mrksvt.apk`
Verifikasi `HASH` baru di nama file.

> Flavor `assembleBusinessDebug` hanya perlu dibangun kalau ingin module
> `com.mrksvt.waen.w4b` berdiri sendiri (pemisahan config module, bukan
> target runtime). Untuk hooking ke `com.whatsapp` + `com.whatsapp.w4b`,
> cukup `com.mrksvt.waen` saja - module ini sudah hook kedua package.

### 9. Install + smoke test

```bash
APK=$(ls -t app/build/outputs/apk/whatsapp/debug/*.apk | head -1)
adb install -r "$APK"
adb shell am force-stop com.whatsapp
adb logcat -c
adb shell monkey -p com.whatsapp -c android.intent.category.LAUNCHER 1 >/dev/null
sleep 40
adb logcat -d | grep -E "LSPosed-Bridge.*(version|Hook|hookIncoming|Loaded Plugin|Unsupported|WaeIIFace|VoiceTTS|Notification)" \
  | head -20
```
Harus terlihat: versi = target, no `Unsupported`, `Loaded Plugin
VoiceTTSFeature` (atau minimal `hookIncomingMessages:`) muncul.

Kalau device terkunci atau logcat kosong: minta user buka HP + unlock,
ulangi cek. Ini BUKAN langkah pipeline utama; laporkan saja status.

## Pipeline port (`/whatsvault port`)

Port commit fitur/fix dari WaEnhancer upstream
(`Dev4Mod/WaEnhancer`, package `com.wmods.wppenhacer`, YukiHookAPI) ke fork
WhatsVault (`com.mrksvt.waen`, legacy `de.robv.android.xposed`).

### P0. Prasyarat
- Repo upstream tersedia lokal. Default `OriginalWaEnhancer/WaEnhancer`
  (sibling di dalam repo fork). Kalau tidak ada, tanya user path-nya atau
  clone ke `.target/upstream` (jangan commit).
- Cek: `git -C <UP> remote -v` dan `git -C <UP> status --short`.
- Ambil commit terakhir yang sudah diport dari `.target/wv_port_state.json`
  (`{"ported_until": "<sha>"}`). Kalau file tidak ada, pakai grep commit
  message fork terakhir: `git log --oneline | grep -i waen\|port upstream`.
- Fetch upstream: `git -C <UP> fetch origin`.
- Device TIDAK dibutuhkan untuk pipeline ini.

### P1. Tentukan rentang commit
```bash
UP=OriginalWaEnhancer/WaEnhancer
FROM=$(python3 -c "import json;print(json.load(open('.target/wv_port_state.json'))['ported_until'])" 2>/dev/null || echo <SHA_TERAKHIR>)
git -C $UP log --oneline $FROM..origin/master
```
- Rentang kosong = tidak ada yang perlu diport, lapor dan berhenti.
- Catat target akhir `<SHA_TARGET>` = `git -C $UP rev-parse origin/master`.

### P2. Klasifikasi commit (wajib, sebelum menulis kode)
Untuk tiap commit, baca diff nyata. JANGAN pakai `git show <sha>` polos
(compactor bisa memotong body / memicu pager):
```bash
git --no-pager -C $UP diff <sha>~1 <sha> --stat
git --no-pager -C $UP diff <sha>~1 <sha> -- <path>
```
Kelompokkan jadi tiga:

| Kelas | Aksi |
|---|---|
| `feat`/`fix`/`perf` yang menyentuh `app/src/main/java` atau `app/src/main/res` | PORT |
| chore changelog, version bump, README, CI workflow, dependency upgrade (YukiHookAPI, libxposed), repo cleanup | N/A, catat alasannya |
| refactor kosmetik tanpa perubahan perilaku | evaluasi: port hanya kalau menyentuh file yang sudah diport |

Tandai N/A secara eksplisit. Jangan pernah memaksa port kode yang
bergantung pada API yang tidak ada di fork.

### P3. Pemetaan ke fork (wajib konsisten)
| Upstream | Fork |
|---|---|
| `import com.wmods.wppenhacer.*` | `import com.mrksvt.waen.*` |
| `hook { before {} }` / `after {}` | `XposedBridge.hookMethod(m, object : XC_MethodHook() { beforeHookedMethod / afterHookedMethod })` |
| `this.intercept { v }` | `XC_MethodReplacement.returnConstant(v)` |
| `instance`, `args`, `result` | `param.thisObject`, `param.args`, `param.result` |
| `instance<T>()` | `param.thisObject as? T ?: return` |
| `invokeOriginal()` | `XposedBridge.invokeOriginalMethod(param.method, param.thisObject, param.args)` |
| `xprefs` | `prefs` |
| `YLog` / `YukiLog` | `logDebug(...)` atau `XposedBridge.log(...)` |
| KavaRef `resolve()`, `firstMethod`, `toClass()` | `ReflectionUtils.findMethodUsingFilter*`, `XposedHelpers.findClass` |
| `context`/`ctx` di provider | `((ContentProvider) param.thisObject).getContext()` |

Aturan keras:
- DILARANG import `com.highcapable.*`. Fork tidak memakai YukiHookAPI.
- Jangan migrasi fork ke YukiHookAPI/libxposed sebagai bagian dari port.
- Pertahankan perilaku spesifik fork kalau upstream menghapusnya.
- `-dontobfuscate` di `app/proguard-rules.pro` dipertahankan (crash log harus
  terbaca). Optimasi/shrink boleh diaktifkan.
- Jangan sentuh `supported_versions_*` di pipeline port; itu tugas
  pipeline `new`.
- Tanpa em-dash (U+2014). Pakai hyphen.
- Tambah fallback anchor, jangan replace anchor DexKit yang sudah ada.

### P4. Pecah jadi WP
Satu WP per fitur atau per grup file yang berdiri sendiri. WP yang berbagi
file (mis. semua WP yang menambah loader di `Unobfuscator.kt`) WAJIB
berurutan, jangan paralel. Catat dependensi di PLAN sebelum eksekusi:

```
.work/PLAN-port-<upstream_ver>.md
```

Isi minimal: rentang commit, tabel commit -> status, daftar WP dengan file
target, acceptance criteria, item N/A beserta alasan.

### P5. Eksekusi + verifikasi build
Setelah semua WP ditulis:
```bash
./gradlew :app:compileWhatsappDebugKotlin --offline
./gradlew :app:assembleWhatsappDebug --offline
```
- Compile Kotlin bisa 10-20 menit. Jalankan di background, baca file log,
  JANGAN polling berulang.
- BUILD FAILED -> perbaiki error yang dilaporkan. Jangan commit.
- Error umum adaptasi: `ReflectionUtils.callMethod(obj, "x")` butuh
  `Method?` (pakai `XposedHelpers.callMethod` untuk nama), signature
  `getJSON`/helper yang berubah, tipe nullable dari Java interop.
- Jangan klaim PASS untuk hook yang belum pernah dijalankan di device.
  Verifikasi build = bukti kompilasi, bukan bukti runtime.

### P6. Dokumentasi wajib
- `changelog.txt`: entri baru di paling atas, bahasa Indonesia, section
  `[ADDED]`/`[IMPROVED]`/`[FIXED]`, tanpa em-dash, tulis dampak user bukan
  hash commit. Section kosong dihapus.
- `FeaturesGap.md`: tambah tabel status per commit upstream
  (`ported` / `adapted: <alasan>` / `N/A: <alasan>`).
- `.work/PLAN-port-*`: centang WP yang selesai.

### P7. Commit & push
- Stage eksplisit per file. Jangan `git add -A` dari home, jangan commit
  `.target/`, `jadx_*`, `smali_*`.
- Format pesan:
  `feat(WAPORT): port WaEnhancer <UPSTREAM_VER> upstream range <FROM>..<TO>`
  Body: ringkasan per fitur, daftar item N/A, dan hasil verifikasi build.
- `git push origin <branch_aktif>`. Push gagal -> laporkan, jangan
  force push.
- Setelah push, tulis state:
```bash
mkdir -p .target
printf '{"ported_until": "%s"}\n' "$(git -C $UP rev-parse origin/master)" > .target/wv_port_state.json
```

### P8. Output ke user
- Rentang commit yang diport + jumlah commit (ported vs N/A)
- Tabel fitur yang masuk + file yang diubah
- Status build (task + hasil), hash commit, status push
- Item N/A beserta alasan satu baris
- Risiko yang belum diuji di device (sebutkan eksplisit)

## Pipeline release (`/whatsvault release`)

Publish GitHub Release berisi 4 varian APK. Kerjakan SETELAH pipeline `new`
selesai (HEAD ter-commit + push), atau berdiri sendiri untuk release bugfix.

### R1. Prasyarat
- `gh auth status` OK (akun github). Fail -> minta user `gh auth login`.
- Working tree bersih & HEAD ter-push (`git status --porcelain` kosong,
  `git log origin/main..HEAD` kosong). Kalau ada diff uncommitted -> minta
  user commit/push dulu atau jalankan pipeline `new` step 7.
- Device TIDAK dibutuhkan untuk pipeline ini.

### R2. Tentukan versi + nama tag
```bash
BASE_VER=$(grep -m1 'versionName = ' app/build.gradle.kts | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
gh release list --limit 10   # lihat rilis existing + title-nya
```
- **Aturan penomoran title (konvensi user)**: hitungan suffix dot PER
  kombinasi base-version x latest-support. Rilis pertama `1.5.5` dengan
  support `2.26.36.xx` -> title `WhatsVault 1.5.5 2.26.36.xx`. Patch
  keduanya untuk support yang sama -> `WhatsVault 1.5.5.1 2.26.36.xx`,
  dst s/d `.9`. (Historis: `v1.5.5` dan `v1.5.5.1` sudah dipakai utk seri
  2.26.35.xx - tidak dihitung ulang utk seri 36.)
- Tag git harus unik vs `git tag -l` + `gh release view`. Kalau tag plain
  `v<base>` / `v<base>.N` sudah dipakai seri support lain, pakai tag
  ber-embed support: `v<base>-2.26.36`, berikutnya `v<base>.1-2.26.36`, dst.
- Versi WhatsVault inti (mis. 1.5.5 -> 1.5.6) hanya atas instruksi user
  (edit `versionCode`+`versionName` di `app/build.gradle.kts`, commit dulu).

### R3. Kumpulkan data changelog
```bash
PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || git tag --sort=-creatordate | head -2 | tail -1)
git log ${PREV_TAG}..HEAD --pretty=format:'%h %s' | grep -viE '^.* (chore|typo)' 
```
- Daftar support: baca SEMUA `<item>` di `supported_versions_wpp` arrays.xml.
- `LATEST_SUP` = item tertinggi (mis. `2.26.36.xx`).

### R4. Draf changelog (format WAJIB sama persis)
```
Support WA + WAB <semua versi arrays.xml, koma-separated>

Fix/Feat:
[FIXED]
• <ringkasan bug yang diperbaiki, 1 baris per bullet, spesifik>

[ADDED]
• Dukungan versi WA/WB <versi baru sejak PREV_TAG>
• <fitur baru>

[UPDATED]
• <perbaikan/penyempurnaan non-kritis, performa, logging>
```
- Sumber bullet = subjek commit `${PREV_TAG}..HEAD` + file yang berubah
  (`git show --stat`). Kelompokkan: `fix:` -> [FIXED], `feat:`/versi support
  -> [ADDED], sisanya (`perf:`, refactor, UI tweak) -> [UPDATED].
- Bahasa bullet: Indonesia ringkas seperti contoh rilis terdahulu
  (`gh release view v1.5.5.1 --json body -q .body` sebagai referensi gaya).
- Fitur besar baru yang belum matang WAJIB diberi penanda `(BETA)` di
  bullet [ADDED].
- Validasi tiap bullet ke user sebelum publish: commit `fix:` TIDAK otomatis
  berarti bug sudah hilang - kalau user bilang belum teratasi/ belum
  berfungsi, buang bulletnya (contoh nyata: fix "recordings Unknown" di
  commit 28e908d8 tapi runtime masih Unknown; tombol play notifikasi belum
  berfungsi; capture voice note masuk belum diuji). Hanya bullet yang
  **dikonfirmasi user** boleh masuk changelog. Jika sub-fitur TTS lain
  (capture voice note, popup balon, play notifikasi) belum diuji, jangan
  masukkan.
- Section yang kosong dihapus header-nya (jangan printed "[UPDATED]" tanpa
  isi). Jangan taruh dukungan versi WA di [UPDATED] - itu selalu [ADDED].
- JANGAN komit metadata AI/hasha commit ke dalam bullet; tulis dampak user.
- Tampilkan draf + tag + title ke user, MINTA PERSETUJUAN sebelum lanjut
  (rilis itu publik & sulit ditarik).

### R5. Build 4 varian
```bash
./gradlew assembleWhatsappDebug assembleWhatsappRelease \
        assembleBusinessDebug assembleBusinessRelease --console=plain
```
Tiap task R8 bisa 2-10 menit; semua harus BUILD SUCCESSFUL. Release variant
mengaktifkan `DONATUR=true` + token dari `donatur.properties` (verify file
ada jika fitur donatur dipakai).

### R6. Siapkan asset + buat rilis
```bash
STAGE=$(mktemp -d); HASH=$(git rev-parse --short=8 HEAD | tr 'a-z' 'A-Z')
for f in app/build/outputs/apk/*/*/WhatsVault*.apk; do
  cp "$f" "$STAGE/$(basename "$f" | sed 's/ (/./g; s/)/./g')"
done
ls "$STAGE"   # 4 file: whatsapp/business x debug/release
```
Nama asset mengikuti konvensi rilis lama (spasi+kurung -> titik, e.g.
`WhatsVault-1.5.5-debug.A94A2CE3._mrksvt.apk`).

```bash
gh release create v<VERSI> \
  --title "WhatsVault <VERSI> <LATEST_SUP>" \
  --notes-file /tmp/release_notes.md \
  --latest \
  "$STAGE"/*.apk
```
Verifikasi: `gh release view v<VERSI>` -> 4 asset ter-upload.

### R7. Install hasil (opsional, device tersambung)
Debug whatsapp tetap bisa di-install buat smoke test (`adb install -r
"$STAGE/WhatsVault-1.5.5-debug.<HASH>._mrksvt.apk"`), seperti langkah 9
pipeline `new`.

## Catatan penting
- **Jangan pernah** menghapus/mengganti anchor yang sudah ada, hanya
  tambah fallback chain. Ini aturan user eksplisit.
- **Port vs new**: pipeline `port` mengambil kode upstream, pipeline `new`
  mengambil versi WhatsApp. Jangan campur; kalau commit upstream membawa
  bump versi support, itu N/A di port dan dikerjakan lewat `new`.
- **Bukti sebelum klaim**: compile sukses bukan bukti hook jalan. Kalau
  belum diuji di device, tulis "belum diuji runtime" pada output.
- **Jangan** commit ke `.target/`, `jadx_*`, `smali_*` - sudah di
  `.gitignore` (line 16 `.target/`), tapi file hasil pipeline lain tetap
  jangan ke index.
- **Jangan** claim PASS pada langkah yang belum di-verifikasi runtime.
- Anchor `Contains` vs `Exact`: cek `StringMatchType` di call site.
  Default `addUsingString` = Contains -> substring cukup (lihat
  `check_anchors.py`).
- `X.*` class literal **tidak ada** di codebase ini (semua lewat
  DexKit). Kalau nemu di kode lain: hardcode itu bug, laporkan.
- Cache invalidation: `UnobfuscatorCache` keyed by module `versionName`
  (`app/build.gradle.kts`), jadi commit baru + rebuild otomatis force
  re-discovery DexKit saat runtime.
- Kalau user ingin versi WhatsVault sendiri berubah (mis. 1.5.5 -> 1.5.6),
  itu perubahan `versionCode`/`versionName` di `app/build.gradle.kts`
  terpisah - skill ini TIDAK otomatis bump; tanya user jika perlu.

## Output ke user (ringkas, terakhir)
- Versi WA yang sekarang supported: `2.26.<minor>.xx` untuk wpp + business
- Daftar anchor fallback yang ditambah (file + baris)
- File APK baru (path + size + versionName)
- Status commit: hash pendek + sudah push / perlu push manual
- Status install + logcat verify
- (release) URL `gh release view` + daftar 4 asset ter-upload

## Troubleshooting
- `adb pull` device offline -> policy retry 3x di atas.
- `jadx` makan RAM banyak; matikan (`pkill -f jadx`) kalau pipeline lanjut
  tanpa perlu full decompile.
- `check_anchors.py` timeout: pool >400k string, blob search Python
  ~10-30 detik; normal.
