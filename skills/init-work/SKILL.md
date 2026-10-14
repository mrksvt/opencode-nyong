---
name: init-work
description: Buat atau update folder .work/ berisi PRD.md, Architecture.md, Design.md, Schema.md, Rules.md, INDEX.md (maps index kode) dari analisa project nyata. Use when user asks to init work, buat dokumentasi project, setup .work/, index kode project, atau sebelum mulai fitur besar. Brainstorm jika project belum ada, analisa otomatis jika sudah ada.
---

# Skill: init-work

## Deskripsi
Buat atau update folder `.work/` berisi 6 dokumen proyek: PRD.md, Architecture.md, Design.md, Schema.md, Rules.md, INDEX.md.

`INDEX.md` adalah **maps index kode** — hasil indexing otomatis semua simbol dalam project (function, class, interface, type, component, hook, page/screen, route, CSS class, CSS ID, HTML ID) lengkap dengan lokasi baris, deskripsi singkat, dan commit id. Agent TIDAK perlu membaca file source satu-satu; cukup baca INDEX.md.

## Trigger
- User minta buat dokumentasi proyek
- User minta update `.work/`
- User minta indexing kode / maps index / daftar function / class / route project
- Sebelum mulai fitur besar yang butuh konteks penuh

## Prosedur

### Jika proyek sudah ada di folder
1. Scan struktur proyek: `src/`, `package.json`, config files, routes, API, context, komponen
2. **Jalankan indexing otomatis** untuk menghasilkan maps index kode:
   ```
   node ~/.config/opencode/skills/init-work/scripts/index-project.mjs <root-proyek> [--dirs "frontend/src,backend/src"] [--class-usage]
   ```
   - Tanpa `--dirs`: auto-detect semua `<subdir>/src` yang punya `package.json` (template/example/demo otomatis di-skip)
   - `--class-usage`: tambahkan daftar class yang dipakai di `className="..."` (berisik, default off)
   - Hasil: `.work/INDEX.md` — berisi semua simbol: nama file, nama function/class/id/route, baris awal-akhir, deskripsi singkat, commit id
   - Tambahkan catatan `INDEX.md` ke Rules.md (daftar file wajib baca)
3. Tulis kelima file lain berdasarkan hasil analisa nyata — bukan template kosong
4. Tampilkan isi semua file ke user sebelum simpan
5. Tunggu persetujuan user
6. Baru simpan ke `.work/`

### Jika folder kosong / proyek baru
1. Brainstorming bersama user: tujuan, role, fitur utama
2. Proposal isi kelima file
3. Tunggu persetujuan
4. Simpan setelah disetujui
5. (INDEX.md di-generate belakangan saat kode sudah ada)

### Update INDEX.md (saat kode berubah)
Jalankan ulang script indexing:
```
node ~/.config/opencode/skills/init-work/scripts/index-project.mjs <root-proyek>
```
Index di-generate ulang → lokasi baris & commit selalu segar. Jalankan sebelum mulai fitur besar berikutnya.

## File yang Dibuat

| File | Isi |
|------|-----|
| `PRD.md` | Tujuan produk, role pengguna, fitur per role, flow utama |
| `Architecture.md` | Struktur folder, layer, routing, auth flow, state management, API pattern |
| `Design.md` | Stack UI, warna brand, tipografi, komponen reusable, pattern layout |
| `Schema.md` | Entitas data frontend (state shape, API response shape, context shape) |
| `Rules.md` | Konvensi koding, naming, pattern yang wajib diikuti, hal yang dilarang |
| `INDEX.md` | **Maps index kode** — semua simbol (function/class/id/css/route/page) + file + baris awal-akhir + deskripsi + commit id |

## Aturan Wajib
- JANGAN simpan file sebelum user setuju
- Isi harus dari analisa nyata, bukan generik
- Semua agent HARUS baca keenam file ini sebelum mulai kerja di proyek ini
- Agent TIDAK boleh membaca file source satu-satu untuk eksplorasi awal — baca INDEX.md dulu, buka file asli hanya untuk simbol spesifik yang deskripsinya kurang

## Cara Agent Membaca Dokumen Ini
Sebelum mulai tugas apapun di proyek ini, baca:
```
.work/INDEX.md        ← maps index: cari simbol (function/class/id/route/css) + lokasi baris + commit
.work/PRD.md
.work/Architecture.md
.work/Design.md
.work/Schema.md
.work/Rules.md
```

## Format INDEX.md
```
# Maps Index — <NamaProyek>

## Cara Pakai (untuk AGENT)
1. Baca file ini SEBELUM membaca file source satu-satu.
2. Cari simbol via grep (nama function/class/id/route).
3. Buka file asli HANYA jika deskripsi kurang — pakai baris awal-akhir.
4. Kolom Commit = commit terakhir yang menyentuh baris awal simbol.

## Pages & Screens
| Simbol | Lokasi (file:baris) | Deskripsi | Commit |

## Routes (Frontend) / API Routes (Backend)
## Components
## Functions & Hooks
## Classes / Interfaces & Types
## CSS Classes / CSS IDs / HTML IDs
```
