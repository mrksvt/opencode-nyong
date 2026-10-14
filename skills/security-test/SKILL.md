---
name: web-security-testing
description: Metodologi pengujian keamanan (pentest defensif) untuk aplikasi web milik sendiri sebelum/sesudah deploy mencakup autentikasi, injection, XSS, CSRF, access control, security headers, upload file, rate limiting, dan verifikasi dua arah (serangan dari luar + monitoring dari dalam server via SSH). Gunakan skill ini setiap kali user minta "tes keamanan", "pentest", "audit security", "cek celah keamanan", atau minta dibuatkan AGENTS.md/checklist untuk menguji web app/API terhadap serangan baik untuk aplikasi Node/Express, PHP, atau framework web lain. Selalu cek dulu apakah user adalah pemilik/pengelola sistem yang dites (bukan target pihak ketiga) sebelum menjalankan langkah apa pun.
---

# Web Security Testing

Skill ini untuk menyusun DAN menjalankan pengujian keamanan defensif
terhadap aplikasi web yang **dimiliki/dikelola oleh user sendiri** bukan
untuk menyerang sistem pihak ketiga. Selalu pastikan otorisasi jelas
(lihat "Cek Otorisasi" di bawah) sebelum lanjut.

## Cek Otorisasi (wajib, sebelum langkah lain)

Sebelum menulis atau menjalankan pengujian apa pun, pastikan minimal salah
satu dari ini jelas dari konteks percakapan:
- User menunjukkan akses langsung ke source code / repo lokal aplikasi tsb
- User menunjukkan akses server (SSH, panel hosting, pm2/systemd status, dsb.)
- User secara eksplisit menyatakan ini proyek/produk yang mereka
  bangun/kelola (freelance, kerja, tugas kuliah, dsb.)

Kalau tidak ada satu pun sinyal ini misalnya user cuma kasih nama domain
orang lain dan minta "coba tes keamanannya" jangan lanjutkan. Jelaskan
bahwa pengujian keamanan cuma bisa dibantu untuk sistem yang user sendiri
punya otorisasi mengujinya, dan sebagai gantinya bisa jelaskan konsep/
metodologi secara umum saja.

## Alur Kerja

1. **Kumpulkan konteks proyek**: stack (bahasa/framework backend & frontend),
   ORM/database, lokasi repo, apakah sudah deploy (domain publik/tunnel) atau
   masih lokal, apakah ada akses SSH ke server, fitur-fitur sensitif yang ada
   (login, upload file, pembayaran, export data, dsb.), dan proteksi yang
   *sudah* diklaim ada (rate limiter, CSRF, WAF, dll jangan asumsikan
   sendiri, tanya atau baca kode).
2. **Susun/tulis dokumen pengujian** (biasanya `AGENTS.md` atau
   `SECURITY-TESTING.md` di root repo user) memakai kerangka di bagian
   "Kerangka Kategori Pengujian" di bawah, disesuaikan stack & fitur yang
   benar-benar ada jangan copy-paste kategori yang tidak relevan (mis.
   jangan sertakan bagian upload file kalau app-nya tidak punya fitur upload).
3. **Selalu sertakan bagian "Aturan Main"** (lihat template) di paling atas
   dokumen ini bukan opsional, karena mengatur batas non-destruktif dan
   scope.
4. **Kalau user minta eksekusi langsung** (bukan cuma dokumen), jalankan
   kategori demi kategori, catat temuan ke `SECURITY-FINDINGS.md` sebelum
   pindah ke kategori berikutnya jangan tunda pelaporan sampai akhir.
   Sebelum menulis test baru dari nol untuk suatu kategori, cek dulu
   `scripts/` (lihat "Script Pengujian Reusable" di bawah) kalau sudah
   ada script yang cocok, pakai/adaptasi itu daripada generate ulang.
5. **Kalau sistem sudah deploy dan user beri akses SSH**, terapkan pola
   Verifikasi Dua Arah (§Kerangka) jangan cuma menyerang dari luar tanpa
   konfirmasi dari log/proses server.

## Script Pengujian Reusable (hemat token)

Supaya tiap sesi pengujian tidak menulis ulang script dari nol, skill ini
menyimpan script test sebagai file nyata di folder tempat skill ini dimuat
(sejajar dengan `SKILL.md`), bukan cuma menulis kode sekali pakai di chat:

```
web-security-testing/
├── SKILL.md
└── scripts/
    ├── auth/          # brute force, rate-limit probe, session/JWT check
    ├── injection/      # SQLi/NoSQLi/command injection payload runner
    ├── xss/            # stored/reflected/DOM XSS probe
    ├── access-control/ # IDOR & role-bypass tester
    ├── csrf/           # CSRF token validator
    ├── headers/        # security header checker
    ├── upload/         # auth-bypass-first upload tester
    ├── exposure/        # node_modules/.git/.env exposure scanner
    └── dual-verify/     # helper korelasi timestamp luar + log SSH dalam
```

Aturan penggunaan:
- **Sebelum membuat script baru**, cek isi `scripts/<kategori>/` kalau
  sudah ada script untuk kategori & jenis target itu (mis. `scripts/auth/
  bruteforce_probe.sh`), baca dan pakai/adaptasi itu, jangan tulis ulang
  dari nol.
- **Script harus generic/parameterized**, bukan hardcode ke satu proyek
  target URL, header, endpoint path, dan kredensial diambil dari argumen
  CLI atau file `.env`/config lokal (yang di-gitignore), supaya script yang
  sama bisa dipakai lintas proyek tanpa diedit ulang.
- **Setelah menulis/mengubah script**, simpan permanen di `scripts/<kategori>/`
  dengan nama deskriptif (bukan `test1.sh`, `tmp.js`, dsb.) dan tambahkan
  komentar singkat di baris atas: apa fungsinya, argumen yang diterima,
  contoh pemanggilan.
- **Jangan commit kredensial/token nyata** ke dalam script pakai
  placeholder/env var, dan pastikan `scripts/**/*.local.*` atau file config
  berisi secret masuk `.gitignore` kalau folder skill ini ikut di-track git.
- Kalau target/stack beda signifikan dari script yang ada (mis. GraphQL vs
  REST) dan script lama tidak bisa diadaptasi murah, baru tulis script baru
 tapi tetap simpan ke `scripts/` biar jadi modal buat sesi berikutnya.
- Update `scripts/README.md` (buat kalau belum ada) tiap kali menambah
  script baru: satu baris per script nama, kategori, kapan dipakai.

## Aturan Main (selalu masuk ke dokumen yang dibuat)

- Target harus eksplisit disebutkan (domain, IP, atau `localhost` + port)
  jangan biarkan ambigu.
- Kalau server sama dipakai untuk layanan/proyek lain, sebutkan eksplisit
  layanan mana yang di luar scope dan tidak boleh disentuh/direstart.
- **Non-destruktif secara default**: pengujian boleh membaca, mengetes,
  memantau, dan melaporkan. TIDAK boleh menghapus, mengubah, atau
  "memperbaiki" file/script/data secara langsung kecuali user memberi izin
  eksplisit untuk langkah remediasi tertentu remediasi tetap keputusan
  manusia, bukan otomatis.
- Rate-limit sendiri saat menguji sistem yang sudah live (jeda antar-request)
  supaya pengujian tidak berubah jadi DoS tidak sengaja, apalagi kalau
  aksesnya lewat tunnel/proxy pihak ketiga (Cloudflare, ngrok, dsb.) yang
  punya kuota.
- Backup data sebelum test yang menulis/mengubah state (seed ulang setelah
  selesai).
- Setiap temuan dicatat dengan format konsisten:
  `[Severity] Judul lokasi (file:baris/endpoint) langkah reproduksi saran perbaikan`.
  Severity: Critical / High / Medium / Low / Info.

## Kerangka Kategori Pengujian

Pilih yang relevan dengan fitur aplikasi user jangan sertakan semua
secara membabi buta.

**Autentikasi & Sesi**
- Brute force / credential stuffing → cek rate limiter jalan (dan tidak
  gampang dilewati dengan spoof header seperti `X-Forwarded-For`)
- Kalau ada CAPTCHA: verifikasi token dicek di server, bukan cuma client;
  token sekali pakai (tidak bisa replay)
- Kalau tidak ada CAPTCHA (mis. karena kebijakan internal user): pastikan
  rate limiter + CSRF jadi lapisan utama dan benar-benar diuji tuntas,
  termasuk scope-nya (per-IP saja vs per-akun)
- JWT/session: algoritma (`alg: none` harus ditolak), masa berlaku, secret
  tidak hardcode, session ID berubah setelah login (anti session fixation)
- Password: policy kompleksitas, hashing (bcrypt/argon2, bukan plaintext)
- User enumeration: pesan error login digeneralisasi

**Injection**
- SQL/NoSQL injection: cari raw query dengan string concatenation, tes
  payload standar (`' OR '1'='1`) hanya pada instance lokal/staging
- Command injection: cari `exec()`/`eval()` yang menerima input user
- Path traversal pada endpoint yang menerima nama file/path

**XSS**
- Stored (input tersimpan lalu dirender ulang), reflected (query string),
  DOM-based (`innerHTML`/`dangerouslySetInnerHTML` tanpa sanitasi)
- Cek header `Content-Security-Policy` terpasang

**Broken Access Control / IDOR**
- Login role rendah, coba akses endpoint role tinggi langsung via
  curl/Postman (bukan lewat UI)
- Ubah ID resource di URL/parameter untuk akses data user lain

**CSRF**
- Endpoint pengubah state (POST/PUT/DELETE) wajib token CSRF valid, token
  unik per sesi/form-load, tervalidasi di server

**Security Headers & Konfigurasi**
- `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`,
  `Content-Security-Policy`
- CORS tidak `*` untuk endpoint berkredensial
- Error/stack trace tidak bocor ke response saat production

**Upload File** (kalau fitur ini ada)
- **Urutan wajib**: (1) tes auth bypass ke endpoint upload dulu tanpa
  sesi, token invalid, role salah baru (2) kalau auth valid, tes upload
  file berbahaya (ekstensi ganda, spoof `Content-Type`, file valid berisi
  payload shell, `.php`/`.js` langsung), lalu (3) kalau berhasil terupload,
  cek apakah file itu bisa dieksekusi langsung dari URL-nya
- Validasi ukuran & MIME diterapkan di server, bukan cuma di frontend

**Eksposur File/Folder Sensitif**
- Coba akses langsung `node_modules/<paket>/package.json`, `.git/`, `.env`,
  folder `config/` lewat domain publik static file server yang salah
  konfigurasi kadang meng-expose ini semua

**Rate Limiting & Dependency**
- Endpoint publik (login, register, forgot-password, search) punya rate
  limit per IP dan idealnya per-akun
- `npm audit` (atau setara) untuk dependency High/Critical
- Versi runtime (Node.js, PHP, dll.) masih didukung/tidak EOL

**Verifikasi Dua Arah** (kalau sistem sudah deploy DAN user beri akses SSH)
- Jalankan test dari luar (via domain publik), catat timestamp presisi
  setiap request
- Dari SSH: cek log proses (`pm2 logs`, `journalctl`, dsb.) untuk
  korelasi apakah request test benar-benar sampai & tercatat
- Cek status proses sebelum/sesudah tiap kategori (restart count naik =
  indikasi crash akibat payload)
- Pantau CPU/RAM saat tes rate-limiting hentikan kalau melonjak drastis
- Satu temuan = satu pasang bukti (apa yang terlihat dari luar + apa yang
  terjadi di server), bukan asumsi sepihak

## Di Luar Cakupan (selalu tegaskan di dokumen)

- Serangan ke infrastruktur pihak ketiga (hosting/CDN/DNS provider itu
  sendiri) hanya aplikasi target yang diuji
- Layanan/proses lain di server yang sama tapi di luar scope
- DoS/stress test skala besar tanpa batas eksplisit
- Menghapus/mengubah file secara langsung sebagai "perbaikan otomatis"
- Social engineering terhadap staf/pengguna nyata

## Setelah Dokumen Dibuat

Jika user minta eksekusi, ingatkan bahwa temuan dicatat ke
`SECURITY-FINDINGS.md` per kategori (bukan ditumpuk di akhir), dan setiap
saran perbaikan yang butuh perubahan kode/config tetap perlu review manusia
sebelum diterapkan skill ini untuk *menemukan dan melaporkan*, bukan
mengeksekusi remediasi otomatis.