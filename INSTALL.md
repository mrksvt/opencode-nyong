# INSTALL.md

Panduan instalasi skill dari repo ini ke [opencode](https://opencode.ai).

> **Untuk agent:** ikuti langkah di bawah berurutan. Setiap langkah punya perintah yang bisa langsung dijalankan, dan diakhiri perintah verifikasi. Jangan menebak lokasi folder — pakai variabel `REPO` dan `SKILLS_DIR` yang sudah didefinisikan di Langkah 1.

---

## Prasyarat

Prasyarat:
- `opencode` terinstall
- `git`
- Linux/macOS (perintah `sed`/`ln` di bawah memakai sintaks POSIX). Untuk Windows, pakai Git Bash atau WSL.

---

## Langkah 1 — clone repo

```bash
REPO="$HOME/Documents/Github/opencode-nyong"
git clone git@github.com-mrksvt/opencode-nyong.git "$REPO" 2>/dev/null \
  || git clone https://github.com/mrksvt/opencode-nyong.git "$REPO"
```

Verifikasi — harus ada 23 folder skill:

```bash
cd "$REPO"
ls -1 skills | wc -l   # expect: 23
```

Kalau hanya `git clone` SSH yang gagal (permission denied), pakai URL HTTPS di atas.

---

## Langkah 2 — pilih metode instalasi

Pilih **satu** dari tiga metode di bawah. Jangan jalankan lebih dari satu.

### Metode A — symlink per-skill (disarankan)

Skill di repo tetap bisa di-`git pull` tanpa menyalin ulang. Cocok kalau kamu mau repo ini jadi sumber kebenaran tunggal.

```bash
cd "$REPO"
SKILLS_DIR="$HOME/.config/opencode/skills"
mkdir -p "$SKILLS_DIR"

# Hapus entri lama dengan nama yang sama, lalu buat symlink baru
for d in "$REPO"/skills/*/; do
  name=$(basename "$d")
  target="$SKILLS_DIR/$name"
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "  ada entri lama: $target"
    rm -rf "$target"
  fi
  ln -s "$d" "$target"
  echo "linked: $name"
done
```

> **Peringatan — `rm -rf` di script ini destruktif.** Baris `rm -rf "$target"` menghapus apa pun yang sudah ada di `$SKILLS_DIR/<nama>`, termasuk direktori skill asli beserta isinya (bukan hanya symlink). Script mencetak `ada entri lama:` sebelum menghapus — baca output itu. Kalau kamu punya skill versi modifikasi di lokasi tersebut dan tidak punya backup, **backup dulu** sebelum menjalankan Metode A:
>
> ```bash
> tar -czf "$HOME/opencode-skills-backup-$(date +%F-%H%M%S).tar.gz" -C "$HOME/.config/opencode" skills
> ```
>
> Hindari `ln -sf` (tanpa `-n`) untuk kasus ini: saat target adalah symlink ke sebuah direktori, `ln -sf` akan membuat link **di dalam** direktori yang ditunjuk, bukan mengganti symlink-nya. Pola `rm` lalu `ln -s` di atas menghindari jebakan itu.

### Metode B — copy penuh (portabel, tanpa symlink)

Skill jadi salinan independen. Repo boleh dihapus setelahnya, dan jalan di environment tanpa symlink.

```bash
cd "$REPO"
SKILLS_DIR="$HOME/.config/opencode/skills"
mkdir -p "$SKILLS_DIR"
cp -r "$REPO"/skills/* "$SKILLS_DIR"/
```

Untuk refresh pembaruan dari repo: hapus folder skill lama di `$SKILLS_DIR`, lalu jalankan ulang perintah di atas.

### Metode C — daftarkan path di `opencode.json` (tanpa menyentuh folder skill global)

Skill dimuat langsung dari lokasi repo. Berguna kalau punya beberapa repo skill dan tidak ingin mencampur semuanya ke satu folder.

```bash
REPO="$HOME/Documents/Github/opencode-nyong"
```

Lalu edit `~/.config/opencode/opencode.json` dan tambahkan:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["/home/mrksvt/Documents/Github/opencode-nyong/skills"]
  }
}
```

Ganti path absolut sesuai lokasi clone kamu. Kalau `skills.paths` sudah ada, tambahkan path ini ke array yang ada — jangan menimpa.

---

## Langkah 3 — restart opencode

opencode membaca konfigurasi sekali saat start, **tidak** hot-reload. Setelah mengubah file config atau menambah skill:

1. tutup semua sesi opencode
2. jalankan `opencode` lagi

---

## Langkah 4 — verifikasi

Pastikan semua skill terbaca. Di dalam sesi opencode, minta:

```
list semua skill yang tersedia
```

Lalu cocokkan dengan daftar di [README.md](./README.md) — harusnya ada 23 nama dari katalog.

Verifikasi tambahan dari terminal:

```bash
SKILLS_DIR="$HOME/.config/opencode/skills"
found=0
for d in "$REPO"/skills/*/; do
  name=$(basename "$d")
  if [ -f "$SKILLS_DIR/$name/SKILL.md" ] || [ -L "$SKILLS_DIR/$name" ]; then
    found=$((found+1))
  else
    echo "MISSING: $name"
  fi
done
echo "installed: $found / 23"
```

---

## Peringatan: symlink rusak di `~/.config/opencode/skills`

Kalau sebelumnya sudah ada symlink ke `../../.agents/skills/<name>`, symlink itu **rusak** — path tersebut mengarah ke `~/.config/.agents/skills/` yang tidak ada. Seharusnya tiga tingkat ke atas (`../../../.agents/skills/`).

Symlink rusak ini tidak berasal dari repo ini, tapi bisa membingungkan karena `~/.agents/skills` juga di-scan otomatis oleh opencode — skill tetap termuat dari sana lewat jalur lain, bukan lewat symlink config yang rusak.

Perbaikannya:

```bash
cd "$HOME/.config/opencode/skills"
for link in */; do
  link="${link%/}"
  if [ -L "$link" ]; then
    target=$(readlink "$link")
    if [ ! -e "$link" ]; then
      corrected=$(printf '%s' "$target" | sed 's#^\.\./\.\./\.agents/#../../../.agents/#')
      rm "$link"
      ln -s "$corrected" "$link"
      echo "fixed: $link -> $corrected"
    fi
  fi
done
```

---

## Catatan per-skill

### `plantuml-skill` — `bin/plantuml.jar` tidak disertakan

Repo ini sengaja **tidak** menyertakan `bin/plantuml.jar` (29 MB). Yang tersedia adalah `SKILL.md`, `references/`, dan dokumentasi. Render diagram tetap bisa dilakukan lewat **Kroki API** (default, tanpa install lokal) sesuai instruksi di dalam skill.

Kalau kamu memang butuh render PlantUML lokal:

1. unduh `plantuml.jar` dari <https://github.com/plantuml/plantuml/releases>
2. simpan ke `skills/plantuml-skill/bin/plantuml.jar`
3. pastikan Java + Graphviz terinstall

Skill akan mendeteksi file itu dan memakainya sebagai fallback lokal.

### `security-test` — nama skill saat dipanggil

Nama di frontmatter adalah `web-security-testing`, bukan `security-test`. Kalau trigger-nya tidak ketemu, panggil dengan nama `web-security-testing`.

### Skill pipeline saling memanggil

`Orchestrator` memanggil `Planner`, `Executor`, `QC`, `Auditor`, dan `Reviewer` sesuai state di `PLAN.md`. Kalau hanya pasang sebagian dari 6 role itu, lifecycle akan berhenti di tengah. Untuk memakai pipeline, pasang keenamnya.

### `whatsvault` — khusus repo WhatsVault

Skill ini memanggil `git`, `gh`, dan Gradle di dalam root repo WhatsVault. Jangan aktifkan kalau kamu tidak punya repo itu di disk.

---

## Uninstall

Hapus symlink atau folder skill yang terpasang:

```bash
SKILLS_DIR="$HOME/.config/opencode/skills"
for d in "$HOME/Documents/Github/opencode-nyong"/skills/*/; do
  rm -rf "$SKILLS_DIR/$(basename "$d")"
done
```

Kalau pakai Metode C, hapus path dari `skills.paths` di `~/.config/opencode/opencode.json`. Restart opencode setelahnya.