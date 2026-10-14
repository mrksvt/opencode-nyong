# opencode-nyong

Koleksi **23 skill** untuk [opencode](https://opencode.ai) — dipakai sebagai dokumentasi dan sumber instalasi.

Repo ini berisi skill pilihan yang dipakai sehari-hari: pipeline kerja ber-role (Planner → Executor → QC → Auditor → Reviewer), disiplin engineering (TDD, debugging, review), utilitas dokumen & diagram, dan tooling design/UI.

---

## Katalog skill

### 1. Pipeline kerja (role-based)

Pipeline state-driven: rencanakan → kerjakan → audit → review.

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 1 | `orchestrator` | `skills/Orchestrator/` | Autopilot pipeline. Terima konteks/PRD/tujuan, lalu gerakkan lifecycle Planner → Executor → QC → Auditor → Reviewer secara state-driven. Tidak menulis kode. |
| 2 | `planner` | `skills/Planner/` | Susun artifact PLAN berisi work package (WP): todo checkbox, traceability matrix, dependensi, risiko. Dipakai sebelum WP pertama, tiap 3 WP selesai, atau saat PRD berubah. |
| 3 | `executor` | `skills/Executor/` | Kerjakan **tepat satu** WP dari PLAN.md: klaim `wip`, implementasi, jalankan gerbang mutu, catat Log, flip ke `qc`. |
| 4 | `qc` | `skills/QC/` | Audit independen satu WP berstatus `qc`: buktikan tiap checklist dengan perintah sendiri, audit kepatuhan + keamanan + hygiene, tulis laporan, flip `done`/`rework`. Dilarang menulis kode. |
| 5 | `auditor` | `skills/Auditor/` | Audit validitas proses, evidence, coverage, dan kesimpulan QC secara independen. Dipanggil setelah semua WP wajib melewati QC. |
| 6 | `reviewer` | `skills/Reviewer/` | Final review seluruh delivery: consistency, requirement coverage, unresolved risk, evidence sufficiency, acceptance readiness. |


### 2. Disiplin engineering

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 7 | `test-driven-development` | `skills/test-driven-development/` | Tulis test dulu sebelum kode implementasi — untuk fitur maupun bugfix. |
| 8 | `systematic-debugging` | `skills/systematic-debugging/` | Hadapi bug, test failure, atau perilaku tak terduga secara sistematis **sebelum** mengusulkan perbaikan. |
| 9 | `verification-before-completion` | `skills/verification-before-completion/` | Jalankan perintah verifikasi dan konfirmasi output sebelum mengklaim selesai/fixed/passing. Bukti sebelum klaim. |
| 10 | `receiving-code-review` | `skills/receiving-code-review/` | Terima feedback code review dengan rigor teknis — verifikasi dulu, jangan implementasi buta atau setuju performatif. |
| 11 | `staff-engineer-review` | `skills/staff-engineer-review/` | Review kode mendalam level Staff+: kualitas, keputusan arsitektur, kesesuaian dengan plan, feedback actionable. |
| 12 | `writing-plans` | `skills/writing-plans/` | Punya spec/requirement multi-step? Tulis plan dulu sebelum menyentuh kode. |
| 13 | `using-git-worktrees` | `skills/using-git-worktrees/` | Buat workspace terisolasi (worktree) sebelum mulai fitur atau mengeksekusi plan implementasi. |

### 3. Dokumen, diagram & pengetahuan

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 14 | `plantuml-skill` | `skills/plantuml-skill/` | Diagram (flowchart, sequence, class, component, ER, architecture) dari kode atau Markdown. Generate `.puml`, export PNG/SVG via Kroki API (tanpa install lokal). |
| 15 | `graphify` | `skills/graphify/` | Ubah input apa pun (kode, dokumen, paper, gambar, video) jadi knowledge graph persisten: god nodes, community detection, query/path/explain. |
| 16 | `init-work` | `skills/init-work/` | Bikin/update folder `.work/` (PRD.md, Architecture.md, Design.md, Schema.md, Rules.md, INDEX.md) dari analisa project nyata. |
| 17 | `no-ai-slop` | `skills/no-ai-slop/` | Edit draft jadi lebih tajam & manusiawi tanpa menghilangkan suara penulis, atau deteksi pola AI-slop tanpa menulis ulang. |

### 4. Design & UI

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 18 | `ui-styling` | `skills/ui-styling/` | UI cantik & aksesibel dengan shadcn/ui + Tailwind + desain berbasis canvas. Layout responsif, komponen aksesibel, dark mode, form, tabel. |
| 19 | `ui-ux-pro-max` | `skills/ui-ux-pro-max/` | Intelijen desain UI/UX dengan database yang bisa dicari (font, palet, gaya, tipografi, stack). |
| 20 | `slides` | `skills/slides/` | Presentasi HTML strategis: Chart.js, design token, layout responsif, formula copywriting, strategi slide kontekstual. |

### 5. Tooling & otomasi

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 21 | `playwright-cli` | `skills/playwright-cli/` | Otomasi interaksi browser, test web page, dan kerja dengan Playwright. |
| 22 | `web-security-testing` | `skills/security-test/` | Metodologi pentest defensif untuk aplikasi web milik sendiri: auth, injection, XSS, CSRF, access control, security header, upload file, rate limiting, verifikasi dua arah. |

### 6. Spesifik project

| No | Skill | Folder | Deskripsi |
|----|-------|--------|-----------|
| 23 | `whatsvault` | `skills/whatsvault/` | Pipeline rilis WhatsVault (modul Xposed WhatsApp): tambah dukungan versi WA baru, build, commit & push, publish GitHub Release. |

> Catatan: `security-test/` nama foldernya `security-test`, tapi `name` di frontmatter adalah `web-security-testing`. Ini disengaja.

---

## Struktur repo

```
opencode-nyong/
├── README.md
├── INSTALL.md
└── skills/
    ├── Auditor/SKILL.md
    ├── Executor/SKILL.md
    ├── Orchestrator/SKILL.md
    ├── Planner/SKILL.md
    ├── QC/SKILL.md
    ├── Reviewer/SKILL.md
    ├── graphify/
    ├── init-work/
    ├── no-ai-slop/
    ├── plantuml-skill/
    ├── playwright-cli/
    ├── receiving-code-review/SKILL.md
    ├── security-test/
    ├── slides/
    ├── staff-engineer-review/SKILL.md
    ├── systematic-debugging/
    ├── test-driven-development/
    ├── ui-styling/
    ├── ui-ux-pro-max/
    ├── using-git-worktrees/SKILL.md
    ├── verification-before-completion/SKILL.md
    ├── whatsvault/
    └── writing-plans/
```

## Instalasi

Lihat **[INSTALL.md](./INSTALL.md)** — berisi langkah yang bisa dieksekusi langsung oleh agent setelah repo ini di-clone.

## Lisensi

Kumpulan skill ini bersumber dari berbagai pihak (termasuk skill bawaan opencode, paket komunitas, dan skill yang ditulis sendiri). Perhatikan lisensi masing-masing skill bila akan didistribusikan ulang. `plantuml-skill` menyertakan `LICENSE` di dalam foldernya.
