# Gambling Content Detection - OSINT Scanning Skill

> **Purpose**: Detect gambling, betting, and casino content injected into legitimate websites (SEO spam hack detection)
> **Use Case**: Security audit, website compromise detection, content integrity verification
> **Method**: Open Source Intelligence (OSINT) - NO hacking, NO exploitation

---

## Table of Contents

1. [Overview](#overview)
2. [Scanning Techniques](#scanning-techniques)
3. [Google Dork Patterns](#google-dork-patterns)
4. [Gambling Keywords Database](#gambling-keywords-database)
5. [URL Pattern Analysis](#url-pattern-analysis)
6. [Indicators of Compromise (IoC)](#indicators-of-compromise)
7. [Multi-Language Detection](#multi-language-detection)
8. [Response Protocol](#response-protocol)
9. [Tools & Resources](#tools--resources)

---

## Overview

### What is SEO Spam Hack?

SEO spam hack (also called "Japanese Keyword Hack" or "Pharma Hack") is an attack where:

1. Attacker exploits vulnerability in website (usually WordPress)
2. Injects hidden pages with gambling/casino/pharmaceutical content
3. Leverages domain authority for search engine ranking
4. Victim's domain ranks for gambling keywords

### Attack Vector

```
Vulnerable WordPress Plugin/Theme
        ↓
Attacker gains access (SQL injection, file upload, etc.)
        ↓
Creates hidden pages/posts in database
        ↓
May add files to /wp-content/, /uploads/, etc.
        ↓
Google crawls and indexes injected content
        ↓
Domain reputation damaged
```

### Why This Matters for .ac.id Domains

- `.ac.id` domains have HIGH authority (educational institution)
- Google trusts these domains more
- Attacker exploits this trust for gambling SEO
- Impact: reputation damage, legal issues, accreditation risk

---

## Scanning Techniques

### Technique 1: Search Engine Dorking

**Principle**: Use search engine operators to find indexed gambling content

**How It Works**:
```
1. Search engine (Google/Bing) has already crawled the website
2. Injected pages are now in search engine index
3. We query the index using site: operator
4. Results show compromised pages with snippets
```

**Advantages**:
- No direct access to server needed
- Cannot be blocked by WAF/firewall
- Shows what public/users can see
- Historical data available

**Limitations**:
- Only shows indexed pages
- May miss recently injected content
- Delayed (depends on crawl frequency)

### Technique 2: Web Archive Analysis

**Principle**: Check historical snapshots for injection timeline

**Resources**:
- Wayback Machine: `https://web.archive.org/web/*/domain.com`
- Google Cache: `cache:domain.com/page`
- Bing Cache: Similar to Google

**Use Case**:
- Determine when hack started
- See progression of injection
- Document evidence for incident report

### Technique 3: Link Discovery

**Principle**: Find related compromised pages through link analysis

**Method**:
```
1. Find one compromised page via dork
2. Check sidebar/footer links on that page
3. Look for "Recent Posts" or "Archives" widgets
4. These often reveal other injected pages
```

### Technique 4: Sitemap Analysis

**Principle**: Check sitemap.xml for injected URLs

**Commands**:
```bash
# Fetch sitemap
curl https://domain.com/sitemap.xml

# Search for gambling keywords
curl -s https://domain.com/sitemap.xml | grep -i "slot\|casino\|judi"
```

---

## Google Dork Patterns

### Basic Domain Scan

```dork
# Scan entire domain for gambling
site:domain.com judi OR slot OR casino OR gambling OR betting

# Indonesian specific
site:domain.com judi OR slot OR togel OR poker OR kasino

# International brands
site:domain.com 1xbet OR bet365 OR 1win OR pinco OR vulkan
```

### Path-Specific Scans

```dork
# WordPress content injection
site:domain.com inurl:/wp-content/news/
site:domain.com inurl:/wp-content/uploads/
site:domain.com inurl:/wp-includes/

# Common injection paths
site:domain.com inurl:/articles/
site:domain.com inurl:/news/
site:domain.com inurl:/blog/
site:domain.com inurl:/pages/
```

### Content-Specific Scans

```dork
# RTP (Return to Player) content
site:domain.com "RTP" AND "slot" AND "gacor"

# Casino brands
site:domain.com "Pragmatic Play" OR "PG Soft" OR "Habanero"

# Betting terms
site:domain.com "maxwin" OR "jackpot" OR "free spin"

# Login pages
site:domain.com "login" AND ("1xbet" OR "1win" OR "bet365")
```

### Multi-Language Scans

```dork
# Russian gambling
site:domain.com казино OR слоты OR зеркало OR ставки

# Polish gambling
site:domain.com kasyno OR bukmacher OR zakłady

# German gambling
site:domain.com kasino OR wettanbieter OR wetten

# Spanish gambling
site:domain.com casino OR apuestas OR tragamonedas

# Azerbaijani gambling
site:domain.com kazino OR mərc OR slot
```

### Advanced Dorks

```dork
# Find hidden directories
site:domain.com ext:php inurl:/admin/
site:domain.com ext:html inurl:/news/article-

# Find injected files by date
site:domain.com after:2025-01-01 before:2025-12-31

# Find specific file patterns
site:domain.com inurl:/article-0000000
site:domain.com inurl:/post-0000000
```

---

## Gambling Keywords Database

### Indonesian Keywords (Bahasa Indonesia)

#### Generic Terms
| Keyword | Translation | Severity |
|---------|-------------|----------|
| judi | gambling | HIGH |
| judi online | online gambling | HIGH |
| slot | slot machine | HIGH |
| slot online | online slots | HIGH |
| togel | lottery | HIGH |
| poker | poker | MEDIUM |
| kasino | casino | HIGH |
| taruhan | betting | HIGH |
| bandar | bookie/dealer | HIGH |
| agen | agent | MEDIUM |
| maxwin | max win (slot term) | HIGH |
| gacor | frequently winning (slang) | HIGH |
| RTP | Return to Player | HIGH |
| free spin | free spin | MEDIUM |
| scatter | scatter symbol | MEDIUM |
| wild | wild symbol | LOW |
| jackpot | jackpot | MEDIUM |
| deposit | deposit | MEDIUM |
| withdraw | withdraw | MEDIUM |
| bonus | bonus | LOW |
| turnover | turnover | MEDIUM |
| cashback | cashback | LOW |
| referral | referral | LOW |
| daftar | register | MEDIUM |
| login | login | LOW |
| link alternatif | alternative link | HIGH |

#### Provider/Platform Names (Indonesian Context)
| Brand | Type | Severity |
|-------|------|----------|
| Pragmatic Play | Slot Provider | HIGH |
| PG Soft | Slot Provider | HIGH |
| Habanero | Slot Provider | HIGH |
| Joker123 | Slot Provider | HIGH |
| Spadegaming | Slot Provider | HIGH |
| Microgaming | Slot Provider | HIGH |
| Playtech | Slot Provider | HIGH |
| RTG Slots | Slot Provider | HIGH |
| Flow Gaming | Slot Provider | HIGH |
| CQ9 | Slot Provider | HIGH |
| Slot88 | Platform | HIGH |
| Pragmatic88 | Platform | HIGH |
| PragmaticID | Platform | HIGH |

### International Keywords

#### English
| Keyword | Severity |
|---------|----------|
| online casino | HIGH |
| online gambling | HIGH |
| slot machine | HIGH |
| sports betting | HIGH |
| poker room | HIGH |
| live casino | HIGH |
| bookmaker | HIGH |
| wagering | MEDIUM |
| payout | MEDIUM |
| house edge | MEDIUM |
| random number generator | LOW |

#### Russian (Русский)
| Keyword | Translation | Severity |
|---------|-------------|----------|
| казино | casino | HIGH |
| слоты | slots | HIGH |
| зеркало | mirror (site) | HIGH |
| ставки | bets | HIGH |
| букмекер | bookmaker | HIGH |
| покер | poker | MEDIUM |
| рулетка | roulette | HIGH |
| джекпот | jackpot | MEDIUM |
| фриспины | free spins | HIGH |
| бонус | bonus | LOW |
| регистрация | registration | MEDIUM |
| вход | login | LOW |
| вывод | withdrawal | MEDIUM |
| депозит | deposit | MEDIUM |

#### Polish (Polski)
| Keyword | Translation | Severity |
|---------|-------------|----------|
| kasyno | casino | HIGH |
| zakłady | bets | HIGH |
| bukmacher | bookmaker | HIGH |
| automaty | slots | HIGH |
| poker | poker | MEDIUM |
| ruletka | roulette | HIGH |
| bonus | bonus | LOW |
| rejestracja | registration | MEDIUM |
| wpłata | deposit | MEDIUM |
| wypłata | withdrawal | MEDIUM |
| legalnych | legal | MEDIUM |
| polskich | Polish | LOW |

#### German (Deutsch)
| Keyword | Translation | Severity |
|---------|-------------|----------|
| kasino | casino | HIGH |
| wettanbieter | betting provider | HIGH |
| wetten | bets | HIGH |
| spielautomaten | slot machines | HIGH |
| poker | poker | MEDIUM |
| roulette | roulette | HIGH |
| bonus | bonus | LOW |
| registrierung | registration | MEDIUM |
| einzahlung | deposit | MEDIUM |
| auszahlung | withdrawal | MEDIUM |
| ohne Lugas | without Lugas (license) | HIGH |

#### Azerbaijani
| Keyword | Translation | Severity |
|---------|-------------|----------|
| kazino | casino | HIGH |
| mərc | bet | HIGH |
| slot | slot | HIGH |
| poker | poker | MEDIUM |
| bonus | bonus | LOW |
| qeydiyyat | registration | MEDIUM |
| daxil ol | login | MEDIUM |
| ödəniş | payment | MEDIUM |

#### Spanish (Español)
| Keyword | Translation | Severity |
|---------|-------------|----------|
| casino | casino | HIGH |
| apuestas | bets | HIGH |
| tragamonedas | slot machines | HIGH |
| póker | poker | MEDIUM |
| ruleta | roulette | HIGH |
| bono | bonus | LOW |
| registro | registration | MEDIUM |
| depósito | deposit | MEDIUM |
| retiro | withdrawal | MEDIUM |

#### Portuguese (Português)
| Keyword | Translation | Severity |
|---------|-------------|----------|
| cassino | casino | HIGH |
| apostas | bets | HIGH |
| caça-níqueis | slot machines | HIGH |
| pôquer | poker | MEDIUM |
| roleta | roulette | HIGH |
| bônus | bonus | LOW |
| cadastro | registration | MEDIUM |
| depósito | deposit | MEDIUM |
| saque | withdrawal | MEDIUM |

### Gambling Brand Names (High Risk)

#### Online Casinos
| Brand | Domain Pattern | Severity |
|-------|----------------|----------|
| 1xBet | 1xbet, 1x-bet | HIGH |
| 1Win | 1win, 1-win | HIGH |
| Pinco | pinco, pinco-casino | HIGH |
| Bet365 | bet365 | HIGH |
| Betway | betway | HIGH |
| 888casino | 888casino | HIGH |
| Vulkan | vulkan, vulkan-vegas | HIGH |
| Mostbet | mostbet | HIGH |
| Stake | stake.com | HIGH |
| Roobet | roobet | HIGH |
| BC.Game | bc.game | HIGH |

#### Slot Providers
| Provider | Keywords | Severity |
|----------|----------|----------|
| Pragmatic Play | pragmatic, pragmaticplay | HIGH |
| PG Soft | pgsoft, pg-soft, pocket-games | HIGH |
| Habanero | habanero | HIGH |
| NetEnt | netent | HIGH |
| Microgaming | microgaming | HIGH |
| Playtech | playtech | HIGH |
| Evolution Gaming | evolution, evolution-gaming | HIGH |
| Play'n GO | playngo, play-n-go | HIGH |
| Yggdrasil | yggdrasil | HIGH |
| Red Tiger | redtiger, red-tiger | HIGH |
| NoLimit City | nolimitcity, nolimit | HIGH |
| Push Gaming | pushgaming | HIGH |
| Relax Gaming | relaxgaming | HIGH |
| Big Time Gaming | btg, bigtimegaming | HIGH |

### Gambling Game Names

#### Slot Games (Popular in Indonesia)
| Game | Provider | Severity |
|------|----------|----------|
| Gates of Olympus | Pragmatic Play | HIGH |
| Sweet Bonanza | Pragmatic Play | HIGH |
| Starlight Princess | Pragmatic Play | HIGH |
| Aztec Gems | Pragmatic Play | HIGH |
| Mahjong Ways | PG Soft | HIGH |
| Mahjong Ways 2 | PG Soft | HIGH |
| Lucky Neko | PG Soft | HIGH |
| Wild Bandito | PG Soft | HIGH |
| Koi Gate | Habanero | HIGH |
| Fa Cai Shen | Habanero | HIGH |

#### Table Games
| Game | Keywords | Severity |
|------|----------|----------|
| Blackjack | blackjack, 21 | MEDIUM |
| Roulette | roulette, rolet | MEDIUM |
| Baccarat | baccarat, bakarat | MEDIUM |
| Poker | poker, texas holdem | MEDIUM |
| Dragon Tiger | dragon-tiger | MEDIUM |
| Sic Bo | sicbo, dadu | MEDIUM |

### Togel/Lottery Keywords

| Keyword | Context | Severity |
|---------|---------|----------|
| togel | lottery | HIGH |
| toto | lottery | HIGH |
| 4D | 4 digit lottery | HIGH |
| 3D | 3 digit lottery | HIGH |
| 2D | 2 digit lottery | HIGH |
| colok bebas | free pick | HIGH |
| colok jitu | exact pick | HIGH |
| shio | zodiac | HIGH |
| syair | prediction poem | HIGH |
| prediksi | prediction | MEDIUM |
| keluaran | output/result | MEDIUM |
| pengeluaran | expenditure | MEDIUM |
| data sgp | Singapore data | HIGH |
| data hk | Hong Kong data | HIGH |
| data sdy | Sydney data | HIGH |
| paito | result chart | HIGH |

### Sports Betting Keywords

| Keyword | Severity |
|---------|----------|
| judi bola | HIGH |
| taruhan bola | HIGH |
| sportsbook | HIGH |
| parlay | HIGH |
| mix parlay | HIGH |
| handicap | MEDIUM |
| over under | MEDIUM |
| odds | MEDIUM |
| livescore | MEDIUM |
| prediksi bola | HIGH |
| bandar bola | HIGH |
| agen bola | HIGH |
| sbobet | HIGH |
| maxbet | HIGH |
| cmd368 | HIGH |
| ubobet | HIGH |

---

## URL Pattern Analysis

### Suspicious URL Patterns

#### WordPress Injection Patterns
```
/wp-content/news/article-00000001.html
/wp-content/news/article-00000002.html
/wp-content/uploads/2024/01/casino-page.html
/wp-includes/sodium_compat/pages/slot-online/
/wp-content/backup/wp-config.php.bak
```

#### Common Injection Directories
```
/news/
/articles/
/pages/
/blog/
/media/
/uploads/
/temp/
/cache/
/backup/
/data/
/includes/
```

#### Dynamic URL Patterns
```
/?p=123456 (high post ID numbers)
/?page_id=99999
/category/casino/
/tag/slot-online/
/author/admin/ (but content is gambling)
```

#### Obfuscated Patterns
```
/base64encodedstring/
/hexencodedstring/
/random-looking-strings/
/mix-of-numbers-and-letters/
```

### URL Structure Red Flags

| Pattern | Example | Risk Level |
|---------|---------|------------|
| Sequential numbering | article-00000001.html | HIGH |
| News/content directory | /wp-content/news/ | HIGH |
| Brand name in path | /1xbet-login/ | CRITICAL |
| Game name in path | /mahjong-ways-slot/ | CRITICAL |
| RTP in path | /rtp-pragmatic-play/ | CRITICAL |
| Foreign language path | /kazino-online/ | HIGH |
| Mirror/alternative | /mirror-casino/ | HIGH |
| Login redirect | /login-1xbet/ | CRITICAL |

---

## Indicators of Compromise

### File System IoCs

#### Suspicious Files
```
# New PHP files in unexpected locations
wp-content/uploads/*.php
wp-content/news/*.html
wp-includes/*.php (not in original WordPress)

# Modified core files
wp-config.php (check for backdoors)
.htaccess (check for redirects)
index.php (check for injections)

# Hidden files
.hidden-file
.htaccess-hidden
.config.php.swp
```

#### File Timestamp Analysis
```bash
# Find recently modified files
find /path/to/wordpress -type f -mtime -30

# Find files modified after specific date
find /path/to/wordpress -type f -newer /path/to/reference/file

# Check for timestamp manipulation
stat suspicious-file.php
```

### Database IoCs

#### WordPress Database
```sql
-- Check for injected posts
SELECT ID, post_title, post_date, post_status 
FROM wp_posts 
WHERE post_title LIKE '%slot%' 
   OR post_title LIKE '%casino%'
   OR post_title LIKE '%judi%'
   OR post_title LIKE '%RTP%';

-- Check for hidden posts
SELECT ID, post_title, post_status 
FROM wp_posts 
WHERE post_status = 'publish' 
AND post_date > '2025-01-01';

-- Check for suspicious users
SELECT ID, user_login, user_email, user_registered 
FROM wp_users 
WHERE user_registered > '2025-01-01';

-- Check user meta for admin privileges
SELECT * FROM wp_usermeta 
WHERE meta_key = 'wp_capabilities' 
AND meta_value LIKE '%administrator%';

-- Check for injected options
SELECT * FROM wp_options 
WHERE option_name LIKE '%casino%' 
   OR option_name LIKE '%slot%'
   OR option_value LIKE '%1xbet%';
```

### Server Log IoCs

#### Access Log Patterns
```bash
# Find suspicious POST requests
grep "POST" access.log | grep -E "wp-login|wp-admin|xmlrpc"

# Find suspicious user agents
grep -E "bot|crawl|spider" access.log | grep -v "Googlebot"

# Find file upload attempts
grep "POST.*upload" access.log

# Find SQL injection attempts
grep -E "UNION|SELECT|INSERT|UPDATE|DELETE" access.log
```

#### Error Log Patterns
```bash
# PHP errors indicating exploitation
grep -E "Fatal|Warning|Notice" error.log | tail -100

# File permission errors
grep "Permission denied" error.log

# Database connection errors
grep "mysql_connect\|mysqli_connect" error.log
```

### Network IoCs

#### DNS Queries
```
# Suspicious domains that might be contacted
1xbet.com
1win.com
pinco.com
vulkan-vegas.com
stake.com
```

#### Outbound Connections
```bash
# Check for outbound connections to gambling domains
netstat -an | grep -E "ESTABLISHED|SYN_SENT"
ss -tp | grep -v "127.0.0.1"
```

---

## Multi-Language Detection

### Language-Specific Google Dorks

#### Russian Gambling Sites
```dork
site:domain.com казино OR слоты OR зеркало OR ставки
site:domain.com inurl:/kazino/ OR inurl:/sloty/
site:domain.com "игровые автоматы" OR "букмекерская"
```

#### Polish Gambling Sites
```dork
site:domain.com kasyno OR bukmacher OR zakłady
site:domain.com inurl:/kasyno/ OR inurl:/zaklady/
site:domain.com "automaty do gier" OR "legalnych"
```

#### German Gambling Sites
```dork
site:domain.com kasino OR wettanbieter OR wetten
site:domain.com inurl:/kasino/ OR inurl:/wetten/
site:domain.com "spielautomaten" OR "ohne Lugas"
```

#### Spanish Gambling Sites
```dork
site:domain.com casino OR apuestas OR tragamonedas
site:domain.com inurl:/casino/ OR inurl:/apuestas/
site:domain.com "máquinas tragamonedas" OR "bonos"
```

#### Portuguese Gambling Sites
```dork
site:domain.com cassino OR apostas OR caça-níqueis
site:domain.com inurl:/cassino/ OR inurl:/apostas/
site:domain.com "máquinas caça-níqueis" OR "bônus"
```

#### Azerbaijani Gambling Sites
```dork
site:domain.com kazino OR mərc OR slot
site:domain.com inurl:/kazino/ OR inurl:/merc/
site:domain.com "onlayn kazino" OR "mərc oyunları"
```

#### Turkish Gambling Sites
```dork
site:domain.com kumarhane OR bahis OR kumar
site:domain.com inurl:/kumarhane/ OR inurl:/bahis/
site:domain.com "online kumar" OR "bahis siteleri"
```

### Multi-Language Keyword Combinations

```dork
# Scan for ANY language gambling
site:domain.com (judi OR slot OR casino OR казино OR kasyno OR kasino OR cassino OR kazino)

# Scan for betting in any language
site:domain.com (taruhan OR betting OR ставки OR zakłady OR wetten OR apuestas OR apostas OR mərc)

# Scan for registration/login pages
site:domain.com (daftar OR login OR регистрация OR rejestración OR registrierung OR registro OR cadastro OR qeydiyyat)
```

---

## Response Protocol

### Immediate Actions (First 24 Hours)

#### 1. Document Everything
```bash
# Take screenshots
# Save search results
# Download compromised pages
# Record timestamps

# Example: Save Google search results
google-search-results.txt:
  - Query used
  - Date/time
  - Results found
  - Screenshots
```

#### 2. Secure Access
```bash
# Change ALL passwords immediately
- WordPress admin
- cPanel/WHM
- FTP/SFTP
- Database (MySQL/PostgreSQL)
- SSH
- Email accounts

# Enable 2FA where possible
# Revoke all active sessions
```

#### 3. Identify Scope
```bash
# How many pages compromised?
site:domain.com judi OR slot OR casino | wc -l

# When did it start?
# Check wayback machine
# Check file timestamps

# What was injected?
- Posts/pages?
- Files?
- Database entries?
- User accounts?
```

### Cleanup Actions (Days 1-3)

#### 1. Remove Injected Content
```bash
# WordPress database cleanup
wp db query "DELETE FROM wp_posts WHERE post_title LIKE '%slot%' OR post_title LIKE '%casino%'"

# Remove suspicious files
find /path/to/wordpress -name "*.html" -path "*/wp-content/news/*" -delete
find /path/to/wordpress -name "*.php" -path "*/wp-content/uploads/*" -delete

# Check and clean .htaccess
cat .htaccess | grep -v "suspicious-rule" > .htaccess.clean
mv .htaccess.clean .htaccess
```

#### 2. Update Everything
```bash
# WordPress core
wp core update

# All plugins
wp plugin update --all

# Theme
wp theme update --all

# Remove unused plugins/themes
wp plugin delete unused-plugin
wp theme delete unused-theme
```

#### 3. Install Security
```bash
# Install security plugin
wp plugin install wordfence --activate
# OR
wp plugin install sucuri-scanner --activate

# Run scan
wp wordfence scan
```

### Post-Cleanup Actions (Week 1-2)

#### 1. Request Google Reindex
```
1. Login to Google Search Console
2. Go to "Removals" tool
3. Request removal of compromised URLs
4. Submit updated sitemap
5. Request indexing of clean pages
```

#### 2. Monitor for Re-infection
```bash
# Setup automated monitoring
# Check daily for new injections
site:domain.com judi OR slot OR casino

# Monitor file changes
find /path/to/wordpress -type f -mtime -1

# Monitor database changes
wp db query "SELECT * FROM wp_posts WHERE post_date > DATE_SUB(NOW(), INTERVAL 1 DAY)"
```

#### 3. Harden Security
```bash
# Disable file editing
# In wp-config.php:
define('DISALLOW_FILE_EDIT', true);

# Disable XML-RPC if not needed
# In .htaccess:
<Files xmlrpc.php>
Order Deny,Allow
Deny from all
</Files>

# Limit login attempts
# Install: Limit Login Attempts Reloaded

# Change default login URL
# Install: WPS Hide Login
```

---

## Tools & Resources

### Online Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Google Search | google.com | Primary dorking tool |
| Bing Search | bing.com | Alternative search engine |
| Wayback Machine | web.archive.org | Historical snapshots |
| VirusTotal | virustotal.com | URL/file scanning |
| Sucuri SiteCheck | sitecheck.sucuri.net | Website malware scan |
| Quttera | quttera.com | Malware detection |
| URLScan | urlscan.io | URL analysis |
| SecurityTrails | securitytrails.com | DNS/history |
| BuiltWith | builtwith.com | Technology detection |

### Command Line Tools

```bash
# Google Dorking (via CLI)
gh-dork -d domain.com -q "judi OR slot OR casino"

# Web Archive API
curl "https://archive.org/wayback/available?url=domain.com"

# Sitemap fetcher
curl -s https://domain.com/sitemap.xml | xmllint --format -

# File integrity check
find /path/to/wordpress -type f -exec md5sum {} \; > current-checksums.txt
diff original-checksums.txt current-checksums.txt

# WordPress CLI
wp plugin list
wp theme list
wp user list --role=administrator
wp db query "SELECT * FROM wp_posts WHERE post_status='publish'"
```

### Automation Scripts

```bash
#!/bin/bash
# gambling-scanner.sh - Basic gambling content scanner

DOMAIN=$1
echo "[*] Scanning $DOMAIN for gambling content..."

# Google dork results
echo "[+] Checking Google index..."
echo "site:$DOMAIN judi OR slot OR casino OR gambling"

# Sitemap check
echo "[+] Checking sitemap..."
curl -s "https://$DOMAIN/sitemap.xml" | grep -i "slot\|casino\|judi\|gambling"

# File check (if you have access)
echo "[+] Checking for suspicious files..."
find /path/to/wordpress -name "*.html" -path "*/wp-content/*" 2>/dev/null

echo "[*] Scan complete. Review results above."
```

---

## Appendix: Sample Google Dork Cheat Sheet

### Quick Scan Dorks
```
# Basic gambling detection
site:domain.com judi|slot|casino|gambling|betting

# WordPress specific
site:domain.com inurl:/wp-content/news/
site:domain.com inurl:/wp-content/uploads/*.html

# Multi-language
site:domain.com казино|kasyno|kasino|cassino|kazino

# Brand names
site:domain.com 1xbet|1win|pinco|bet365|vulkan

# RTP/Slot specific
site:domain.com "RTP" AND ("slot" OR "gacor" OR "maxwin")

# Togel specific
site:domain.com togel|toto|4D|3D|2D|sgp|hk|sdy
```

### Comprehensive Scan Template
```
# Replace DOMAIN with target domain

# Indonesian gambling
site:DOMAIN judi OR slot OR togel OR poker OR kasino OR taruhan OR bandar OR agen OR maxwin OR gacor OR RTP OR deposit OR withdraw OR daftar OR login OR "link alternatif"

# International brands
site:DOMAIN 1xbet OR 1win OR pinco OR bet365 OR vulkan OR mostbet OR stake OR roobet OR pragmatic OR pgsoft OR habanero OR microgaming

# Russian
site:DOMAIN казино OR слоты OR зеркало OR ставки OR букмекер OR покер OR рулетка OR фриспины

# Polish
site:DOMAIN kasyno OR bukmacher OR zakłady OR automaty OR legalnych OR polskich

# German
site:DOMAIN kasino OR wettanbieter OR wetten OR spielautomaten OR ohne

# Multi-path
site:DOMAIN inurl:/news/ OR inurl:/articles/ OR inurl:/pages/ OR inurl:/wp-content/
```

---

## License

This document is for **defensive security purposes only**. Use to:
- Detect compromises on your own websites
- Audit websites you have authorization to test
- Educate about SEO spam attacks

Do NOT use for:
- Attacking websites
- Injecting gambling content
- Black hat SEO

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-11 | Initial release - Based on real incident analysis of stmik-tegal.ac.id |

---

**Author**: Sisyphus Security Agent  
**Created**: July 11, 2026  
**Last Updated**: July 11, 2026  
**Purpose**: Gambling content detection and SEO spam hack identification
