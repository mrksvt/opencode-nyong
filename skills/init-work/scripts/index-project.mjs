#!/usr/bin/env node
/**
 * index-project.mjs — Generate Maps Index (.work/INDEX.md)
 *
 * Menganalisis project dan menghasilkan indeks semua simbol kode:
 * pages/screens, routes, components, functions, hooks, classes,
 * interfaces/types, CSS classes/IDs, HTML IDs.
 *
 * Setiap entry berisi: nama file, nama simbol, baris awal-akhir,
 * deskripsi singkat, commit id.
 *
 * Usage:
 *   node index-project.mjs <project-root> [--dirs "frontend/src,backend/src"] [--out .work/INDEX.md]
 *
 * Default: auto-detect source dirs (root/src + subdir dengan package.json + src).
 * Output default: <root>/.work/INDEX.md
 */

import { readFileSync, readdirSync, statSync, existsSync, writeFileSync, mkdirSync } from 'node:fs'
import { join, relative, resolve, basename, extname, dirname, sep } from 'node:path'
import { execFileSync } from 'node:child_process'

// ---------- args ----------
const args = process.argv.slice(2)
let root = '.'
let explicitDirs = null
let outRel = '.work/INDEX.md'
let withClassUsage = false

for (let i = 0; i < args.length; i++) {
  const a = args[i]
  if (a === '--dirs') explicitDirs = args[++i].split(',').map(s => s.trim()).filter(Boolean)
  else if (a === '--out') outRel = args[++i]
  else if (a === '--class-usage') withClassUsage = true
  else if (!a.startsWith('-')) root = a
}

root = resolve(root)
const OUT = resolve(root, outRel)

// ---------- utils ----------
const SKIP_DIRS = new Set(['node_modules', 'dist', 'build', '.git', '.work', '.omo', '.next', '.nuxt', 'coverage', '.playwright-cli', 'public', 'vendor', 'assets'])
const CODE_EXT = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.vue', '.svelte'])
const CSS_EXT = new Set(['.css', '.scss', '.less', '.sass'])
const HTML_EXT = new Set(['.html', '.htm'])

function walk(dir, out = []) {
  let entries
  try { entries = readdirSync(dir) } catch { return out }
  for (const e of entries) {
    if (SKIP_DIRS.has(e) || e.startsWith('.')) continue
    const p = join(dir, e)
    let st
    try { st = statSync(p) } catch { continue }
    if (st.isDirectory()) walk(p, out)
    else out.push(p)
  }
  return out
}

function detectSrcDirs(rootDir) {
  const dirs = []
  const TEMPLATE_RE = /(template|example|demo|starter|boilerplate|free-|sample|vendor|tailadmin)/i
  // root/src
  if (existsSync(join(rootDir, 'src'))) dirs.push(join(rootDir, 'src'))
  // subdir dengan package.json + src
  for (const e of readdirSync(rootDir)) {
    if (SKIP_DIRS.has(e) || e.startsWith('.') || TEMPLATE_RE.test(e)) continue
    const sub = join(rootDir, e)
    if (!statSync(sub).isDirectory()) continue
    if (existsSync(join(sub, 'src')) && existsSync(join(sub, 'package.json'))) dirs.push(join(sub, 'src'))
  }
  return [...new Set(dirs)]
}

function stripQuotes(s) { return s.replace(/['"]/g, '') }

function cleanComment(line) {
  return line
    .replace(/^\s*\/\*\*?\s*/, '')
    .replace(/^\s*\*\s?/, '')
    .replace(/^\s*\/\/\s?/, '')
    .replace(/\s*\*\/\s*$/, '')
    .replace(/@\w+\s*:?\s*/, '')
    .trim()
}

/**
 * Ambil deskripsi singkat: komentar JSDoc/block/line di atas simbol,
 * fallback ke baris deklarasi itu sendiri.
 */
function describe(lines, startIdx) {
  // scan ke atas: komentar kontigu
  const commentLines = []
  for (let i = startIdx - 1; i >= 0 && i >= startIdx - 8; i--) {
    const t = lines[i].trim()
    if (t === '' || t === '/' || t === '*/') {
      if (commentLines.length > 0) break // blank setelah komentar
      continue
    }
    // separator dekoratif (─── Section ───, ===, ----, ####) → skip, bukan deskripsi
    const stripped = t.replace(/^\/\/\s*/, '').replace(/^\/\*\*?\s*/, '').replace(/^\*\s?/, '')
    if (/^[─═=#*_~\-]{2,}/.test(stripped) && /[─═=#*_~\-]{2,}$/.test(stripped) && stripped.length > 3) {
      continue
    }
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/**') || t.startsWith('/*')) {
      commentLines.unshift(t)
    } else if (commentLines.length > 0) {
      break
    } else {
      break
    }
  }
  if (commentLines.length > 0) {
    const joined = commentLines.map(cleanComment).filter(Boolean).join(' ').trim()
    if (joined) return joined.slice(0, 120)
  }
  // fallback: baris deklarasi
  const decl = lines[startIdx]
    .replace(/export\s+default\s*/, '')
    .replace(/export\s+/, '')
    .replace(/async\s+/, '')
    .replace(/function\s+/, '')
    .replace(/\s*:\s*[\w<>[\]|,&.\s]+(?==>|$)/, '')
    .trim()
  return decl.slice(0, 100)
}

/** Hitung baris akhir body (brace matching). Strip string/komentar dulu. */
function bodyEnd(lines, startIdx) {
  const sig = lines[startIdx]
  const openIdx = sig.indexOf('{')
  if (openIdx === -1) return startIdx // one-liner tanpa body brace
  let depth = 0
  let paren = 0
  let started = false
  for (let i = startIdx; i < lines.length; i++) {
    const cleaned = lines[i]
      .replace(/`[^`]*`/g, '``')
      .replace(/\/\/.*$/g, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
    for (const ch of cleaned) {
      if (ch === '(') paren++
      else if (ch === ')') paren = Math.max(0, paren - 1)
      else if (ch === '{') { if (paren === 0) { depth++; started = true } }
      else if (ch === '}') { if (paren === 0 && started) { depth--; if (depth === 0) return i } }
    }
  }
  return lines.length - 1
}

/** Single-line capture: `<Route path="x"` / `router.get('/x'` */
const ROUTE_RE = /<Route\s+path=["']([^"']+)["']/g
const API_ROUTE_RE = /\b(?:router|app|server|fastify|instance)\.(get|post|put|patch|delete|use)\s*\(\s*["']([^"']+)["']/g

// ---------- git blame: line -> commit ----------
function buildBlameMap(file) {
  try {
    const out = execFileSync('git', ['-C', root, 'blame', '--line-porcelain', relative(root, file)], {
      encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'],
    })
    const map = new Map()
    for (const line of out.split('\n')) {
      const m = line.match(/^([0-9a-f]{40}) (\d+) (\d+)(?: \d+)?$/)
      if (m) map.set(Number(m[3]), m[1].slice(0, 8))
    }
    return map
  } catch {
    // fallback: commit file-level
    try {
      const out = execFileSync('git', ['-C', root, 'log', '-1', '--format=%h', '--', relative(root, file)], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
      })
      const h = out.trim()
      return h ? new Map([[1, h]]) : new Map()
    } catch { return new Map() }
  }
}

// ---------- parse per file ----------
function parseFile(file) {
  const rel = relative(root, file).split(sep).join('/')
  const ext = extname(file).toLowerCase()
  const content = readFileSync(file, 'utf8')
  const lines = content.split('\n')
  const isTsx = ext === '.tsx' || ext === '.jsx'
  const isCss = CSS_EXT.has(ext)
  const isHtml = HTML_EXT.has(ext)
  const isCode = CODE_EXT.has(ext)
  const entries = []
  const seenClassNames = new Set()
  let blame = null

  const isPage = /\/pages\/|\/screens\/|\/views\//.test(rel)
  const isTest = /\.(test|spec)\./.test(rel)

  if (!isCode && !isCss && !isHtml) return entries

  // Page/screen entity
  if (isPage) {
    // desc: komentar teratas file, fallback basename
    let pdesc = '-'
    for (let k = 0; k < Math.min(6, lines.length); k++) {
      const ct = lines[k].trim()
      if (ct.startsWith('//') || ct.startsWith('*') || ct.startsWith('/*')) {
        const c = cleanComment(ct)
        if (c) { pdesc = c; break }
      } else if (ct !== '' && !ct.startsWith('import') && !ct.startsWith('{')) {
        break
      }
    }
    entries.push({
      type: 'page', name: basename(file, ext),
      start: 1, end: lines.length,
      desc: isTest ? 'test' : pdesc,
      file: rel,
    })
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const t = line.trim()
    if (!t || t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) continue

    if (isCode) {
      // --- class (React class component kalau ada render) ---
      let m = t.match(/^(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_$][\w$]*)/)
      if (m) {
        const name = m[1]
        const end = bodyEnd(lines, i)
        const body = lines.slice(i, end + 1).join('\n')
        const type = /\brender\s*\(/.test(body) ? 'component' : 'class'
        entries.push({ type, name, start: i + 1, end: end + 1, desc: describe(lines, i), file: rel })
        continue
      }

      // --- function declaration ---
      m = t.match(/^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(/)
      if (m) {
        const name = m[1]
        const end = bodyEnd(lines, i)
        const type = isTsx && /^[A-Z]/.test(name) ? 'component' : 'function'
        entries.push({ type, name, start: i + 1, end: end + 1, desc: describe(lines, i), file: rel })
        continue
      }

      // --- interface / type ---
      m = t.match(/^(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)/)
      if (m) {
        const name = m[1]
        const end = bodyEnd(lines, i)
        entries.push({ type: 'interface', name, start: i + 1, end: end + 1, desc: describe(lines, i), file: rel })
        continue
      }
      m = t.match(/^(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=/)
      if (m) {
        const name = m[1]
        const end = bodyEnd(lines, i)
        entries.push({ type: 'type', name, start: i + 1, end: end + 1, desc: describe(lines, i), file: rel })
        continue
      }

      // --- const arrow / component / hook ---
      m = t.match(/^(?:export\s+)?(?:default\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>/)
      if (m) {
        const name = m[1]
        const end = bodyEnd(lines, i)
        let type = 'function'
        if (/^use[A-Z]/.test(name)) type = 'hook'
        else if (isTsx && /^[A-Z]/.test(name)) type = 'component'
        entries.push({ type, name, start: i + 1, end: end + 1, desc: describe(lines, i), file: rel })
        continue
      }

      // --- export default anonymous arrow/function (named via component file) ---
      m = t.match(/^export\s+default\s+(?:async\s*)?(?:function\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>/)
      if (m && isTsx) {
        const name = basename(file, ext)
        const end = bodyEnd(lines, i)
        entries.push({ type: 'component', name, start: i + 1, end: end + 1, desc: 'default export — ' + describe(lines, i), file: rel })
        continue
      }

      // --- API routes (backend) ---
      API_ROUTE_RE.lastIndex = 0
      let rm
      while ((rm = API_ROUTE_RE.exec(t)) !== null) {
        const method = rm[1].toUpperCase()
        entries.push({ type: 'api-route', name: `${method} ${stripQuotes(rm[2])}`, start: i + 1, end: i + 1, desc: 'API route', file: rel })
      }
    }

    // --- frontend routes: <Route path="x" /> ---
    if (isTsx || isCode) {
      ROUTE_RE.lastIndex = 0
      let rm
      while ((rm = ROUTE_RE.exec(t)) !== null) {
        const path = stripQuotes(rm[1])
        entries.push({ type: 'route', name: path, start: i + 1, end: i + 1, desc: `Route ${path}`, file: rel })
      }
    }

    // --- HTML IDs (static string) ---
    if (isTsx || isHtml || isCode) {
      let m2
      const idRe = /\bid=["']([^"']+)["']/g
      while ((m2 = idRe.exec(t)) !== null) {
        entries.push({ type: 'html-id', name: m2[1], start: i + 1, end: i + 1, desc: `id="${m2[1]}"`, file: rel })
      }
      // className usage (dedupe per file, optional)
      const clsRe = /\bclassName=["']([^"']+)["']/g
      while ((m2 = clsRe.exec(t)) !== null) {
        if (!withClassUsage) break
        for (const c of m2[1].split(/\s+/)) {
          if (!c || seenClassNames.has(c)) continue
          seenClassNames.add(c)
          entries.push({ type: 'css-class-used', name: c, start: i + 1, end: i + 1, desc: 'className usage', file: rel })
        }
      }
    }

    // --- CSS definitions ---
    if (isCss) {
      let m2 = t.match(/^\.([\w-]+)\s*[,{]/)
      if (m2) {
        entries.push({ type: 'css-class', name: m2[1], start: i + 1, end: bodyEnd(lines, i) + 1, desc: describe(lines, i) || 'CSS class', file: rel })
        continue
      }
      m2 = t.match(/^#([\w-]+)\s*[,{]/)
      if (m2) {
        entries.push({ type: 'css-id', name: m2[1], start: i + 1, end: bodyEnd(lines, i) + 1, desc: describe(lines, i) || 'CSS ID', file: rel })
        continue
      }
      m2 = t.match(/^@keyframes\s+([\w-]+)/)
      if (m2) {
        entries.push({ type: 'css-keyframe', name: m2[1], start: i + 1, end: bodyEnd(lines, i) + 1, desc: 'keyframes', file: rel })
      }
    }
  }

  // attach commit per symbol (lazy blame per file)
  if (entries.length > 0) {
    blame = buildBlameMap(file)
    for (const e of entries) {
      e.commit = blame.get(e.start) || '-'
    }
  }

  return entries
}

// ---------- main ----------
const srcDirs = explicitDirs ? explicitDirs.map(d => resolve(root, d)) : detectSrcDirs(root)
if (srcDirs.length === 0) {
  console.error('No source dirs found. Pass --dirs "frontend/src,backend/src"')
  process.exit(1)
}

const files = []
for (const d of srcDirs) walk(d, files)
files.sort()

const all = []
for (const f of files) {
  try { all.push(...parseFile(f)) } catch (e) { console.error(`skip ${f}: ${e.message}`) }
}

// dedupe identical (file,name,start)
const seen = new Set()
const entries = []
for (const e of all) {
  const k = `${e.file}|${e.name}|${e.start}`
  if (seen.has(k)) continue
  seen.add(k)
  entries.push(e)
}

entries.sort((a, b) => {
  const order = ['page', 'route', 'api-route', 'component', 'function', 'hook', 'class', 'interface', 'type', 'css-class', 'css-class-used', 'css-id', 'css-keyframe', 'html-id']
  const ia = order.indexOf(a.type); const ib = order.indexOf(b.type)
  if (ia !== ib) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
  if (a.file !== b.file) return a.file.localeCompare(b.file)
  return a.start - b.start
})

// ---------- markdown ----------
function tableRows(items) {
  return items.map(e => {
    const loc = `${e.file}:${e.start}-${e.end}`
    const desc = (e.desc || '-').replace(/\|/g, '\\|')
    return `| \`${e.name}\` | \`${loc}\` | ${desc} | \`${e.commit}\` |`
  }).join('\n')
}

const date = new Date().toISOString().slice(0, 10)
const groups = {
  'Pages & Screens': entries.filter(e => e.type === 'page'),
  'Routes (Frontend)': entries.filter(e => e.type === 'route'),
  'API Routes (Backend)': entries.filter(e => e.type === 'api-route'),
  'Components': entries.filter(e => e.type === 'component'),
  'Functions & Hooks': entries.filter(e => e.type === 'function' || e.type === 'hook'),
  'Classes': entries.filter(e => e.type === 'class'),
  'Interfaces & Types': entries.filter(e => e.type === 'interface' || e.type === 'type'),
  'CSS Classes (defined)': entries.filter(e => e.type === 'css-class'),
  'CSS Classes (used in className)': entries.filter(e => e.type === 'css-class-used'),
  'CSS IDs & Keyframes': entries.filter(e => e.type === 'css-id' || e.type === 'css-keyframe'),
  'HTML IDs': entries.filter(e => e.type === 'html-id'),
}

const total = entries.length
let md = `# Maps Index — ${basename(root)}

> Generated: ${date} by \`init-work\` · Total: ${total} symbols · ${srcDirs.length} source dir(s)
> Regenerate: \`node ~/.config/opencode/skills/init-work/scripts/index-project.mjs ${root}\`

## Cara Pakai (untuk AGENT)
1. Baca file ini SEBELUM membaca file source satu-satu.
2. Cari simbol yang dibutuhkan via grep di file ini (nama function/class/id/route).
3. Buka file asli HANYA jika deskripsi di bawah belum cukup — pakai baris awal-akhir sebagai target.
4. Kolom Commit = commit terakhir yang menyentuh baris awal simbol.

## Ringkasan per Kategori
${Object.entries(groups).map(([g, items]) => `- ${g}: ${items.length}`).join('\n')}

---
`

for (const [title, items] of Object.entries(groups)) {
  if (items.length === 0) continue
  md += `\n## ${title}\n\n| Simbol | Lokasi (file:baris) | Deskripsi | Commit |\n|---|---|---|---|\n${tableRows(items)}\n`
}

mkdirSync(dirname(OUT), { recursive: true })
writeFileSync(OUT, md)

// summary ke stdout
console.log(`✓ INDEX.md → ${OUT}`)
console.log(`  ${total} symbols · ${files.length} files scanned`)
for (const [g, items] of Object.entries(groups)) {
  if (items.length > 0) console.log(`  ${g}: ${items.length}`)
}
