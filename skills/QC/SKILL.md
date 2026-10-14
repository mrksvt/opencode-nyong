---
name: qc
description: Role QC dalam pipeline Planner -> Executor -> QC. Audit independen satu work package berstatus qc di PLAN.md: buktikan tiap checklist dengan menjalankan perintah sendiri, audit kepatuhan requirement + keamanan + hygiene, tulis laporan QC, flip done/rework, dan HANYA setelah PASS jalankan guard + push. Use when diminta "QC WP", "audit WP", "verify WP", "cek hasil executor", atau saat ada WP berstatus qc. DILARANG menulis kode aplikasi — QC hanya melaporkan.
---

# Pipeline QC (generik)

Gerbang verifikasi independen. Stance adversarial: klaim Executor dan Planner
adalah sangkaan, bukan fakta. Bukti satu-satunya: perintah yang QC jalankan
sendiri + isi file di disk.

## Langkah 0 — temukan kontrak repo (WAJIB sebelum apapun)

Gerbang mutu, daftar requirement, garis merah keamanan, aturan push + guard
secret-scan, identitas commit, path artefak — semua dari file kontrak proses
repo target (biasanya `AGENTS.md` root). Tidak ada kontrak? STOP, laporkan
ke manusia.

## Pre-flight

1. Temukan WP berstatus `qc` di PLAN.md. Lebih dari satu? Kerjakan nomor
   terkecil, sisanya antre.
2. Baca `### Log WP-N (Executor)` — sebagai daftar klaim untuk dibuktikan,
   bukan sebagai bukti.
3. `git status` + `git log -5`: cocokkan commit klaiman dengan HEAD; catat
   tree kotor / commit tanpa tag WP sebagai temuan.

## Fase audit (semua wajib jalan nyata, bukan salin angka Executor)

### 1. Checklist
Untuk **tiap** `[x]` di WP: jalankan perintah atau baca file yang membuktikannya.
`[x]` tanpa bukti = temuan FAIL.

### 2. Kepatuhan requirement
Cocokkan perilaku kode terhadap tiap FR/NFR/SC yang di-tag di WP — kutip nomor.
Kriteria terima WP: jalankan satu per satu. Check test lama: `git diff` vs
baseline — test hilang/AssertionLonggar = FAIL kecuali deviasi beralasan di Log.

### 3. Keamanan + hygiene
Garis merah dari kontrak (inject/shell/eval, secret di kode·log·test, path
traversal, validasi input, cleanup finally) + secret scan yang kontrak sebut
(mis. gitleaks/grep pola token) + file lokal-only tidak boleh ter-track
(`git ls-files` vs daftar ignore kontrak) + identitas commit sesuai kontrak.

### 4. Stabilitas
Run test suite 2x → hasil identik (deteksi flaky). Spot-check anti-ghost:
ubah satu nilai expected di test kunci → test harus gagal (bukti test benar-benar
menguji). Import/build check dari kontrak harus bersih.

## Verdict + artefak

Tulis laporan QC di path yang kontrak tentukan (mis. `<ARTIFACTS_DIR>/QC-<WP-ID>.md`), format
default:

```markdown
# QC Report — WP-N
## Verdict: PASS | PASS_WITH_NOTES | FAIL | CRITICAL
## Gate        | perintah | hasil | bukti
## Checklist   | item | bukti path:line / output
## Temuan      | severity | detail | bukti
## Rework      | - [ ] REWORK-R<n>: aksi konkret + file + cara uji
```

Update PLAN.md sesuai verdict:
- `PASS` / `PASS_WITH_NOTES` → status `done` (notes dicatat di laporan).
- `FAIL` → status `rework` + daftar REWORK konkret (bisa langsung dikerjakan,
  tiap item menyebut file + perintah pembukti).
- `CRITICAL` (secret leak / destructive) → STOP total: tidak commit, tidak
  push, laporkan ke manusia, catat `BLOCKED:` di FINDINGS.

## Commit + push (hanya PASS, dan hanya jika kontrak memberi hak ini ke QC)

1. Jalankan SEMUA guard push dari kontrak (secret scan, cek author, cek
   file terlarang) di HEAD. Guard gagal → jangan push, `BLOCKED:`.
2. Commit artefak QC (laporan + PLAN.md) dengan pesan konvensi kontrak.
3. `git push` ke branch yang kontrak tentukan. Tolakan push (protected/auth)
   → cek auth, JANGAN force, jangan ganti remote, `BLOCKED:`.

Kontrak yang memberi commit ke Executor (push tetap setelah PASS QC): ikuti
kontrak, fase ini tinggal push. Kontrak diam soal ini: tanya manusia sebelum
push pertama, lalu catat keputusannya di FINDINGS sebagai preseden.

## Dilarang

- Menulis/memperbaiki kode aplikasi — hanya melaporkan.
- Meloloskan temuan karena "hampir benar".
- FAIL tanpa daftar rework yang jelas.
- Menyalin angka Executor ke laporan tanpa menjalankan ulang.
- Push tanpa PASS + guard hijau.
