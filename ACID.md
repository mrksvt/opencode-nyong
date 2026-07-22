# ACID Code Discipline

Berlaku untuk setiap edit, create, debugging: semua operasi harus ACID.

## A — Atomicity
- Satu logical change = satu unit kerja. Jangan campur perubahan tidak terkait.
- Multi-step writes: wrapping in transaction (BEGIN/COMMIT/ROLLBACK).
- Debugging: isolasi satu penyebab per iterasi. Jangan shotgun.
- File edits: selesaikan satu todo sebelum mulai todo lain.

## C — Consistency
- Output harus konsisten dengan input dan state sebelumnya.
- Validasi invariant setelah setiap perubahan (lsp_diagnostics, build check).
- Database: constraints (FK, unique, check) harus terpenuhi. Jangan tinggalkan inconsistent state.

## I — Isolation
- Selalu asumsikan ada proses/request lain berjalan paralel.
- Race condition = musuh utama. Hindari read-modify-write tanpa lock/transaction.
- Database: pilih isolation level sesuai konteks (READ COMMITTED default, SERIALIZABLE untuk critical).
- File ops: jangan baca/tulis file yang sedang dimodifikasi proses lain.

## D — Durability
- Commit dulu, validasi kemudian, baru lapor selesai.
- Backup/rollback plan sebelum modifikasi konfigurasi/produksi.
- Logging state sebelum perubahan untuk recovery.

## Checklist (setiap task)

- [ ] Perubahan adalah unit atomic? (A)
- [ ] Invariant/constraint masih terpenuhi? (C)
- [ ] Tidak ada race condition dengan concurrent ops? (I)
- [ ] Perubahan survive setelah disimpan? (D)

Violation of any = rollback, fix, redo.