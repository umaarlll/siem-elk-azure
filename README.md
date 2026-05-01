# 🔐 EyeSec — ELK SIEM on Azure

A Security Information and Event Management (SIEM) platform built with the Elastic Stack (ELK), containerized with Docker and deployed on Microsoft Azure. The platform ingests, parses and visualizes 17,000+ security events enabling real-time threat detection, monitoring and incident investigation.

> **Status:** 🚧 In Progress — Detection & Investigation phase coming soon.

---

## 😤 The Honest Story

So I got assigned a SIEM project and the setup guide said to manually install OpenJDK, extract three zip files and configure everything by hand.

I did not want to do that.

Instead I containerized the whole thing with Docker so it spins up with one command. Then realized my teammates needed access too — so I threw it on Azure, set up a Cloudflare tunnel for a public HTTPS URL and called it a day.

Lazy? Maybe. But it works, it's secure and my teammates just need a link. 🔗

What followed was several days of troubleshooting that I did not expect.

---

## 🤕 Hardships (The Real Documentation)

### 1. Elasticsearch kept dying on startup
Every time Docker started, Elasticsearch would crash silently. No obvious error. Just... gone.

Turns out Linux has a default virtual memory limit that Elasticsearch hates. You need to run:
```bash
sysctl -w vm.max_map_count=262144
```

And because I didn't make it permanent, I had to run this **every single time** Docker Desktop restarted. Every. Single. Time.

*Fix: add it to `/etc/sysctl.conf` on Linux. On Windows WSL, add it to `.wslconfig`.*

---

### 2. xpack security blocking everything
Moved to Azure VM, started the stack, opened Kibana — it asked for a token. Cool. Except the token expired. And the password was auto-generated and I didn't save it. And resetting it required Elasticsearch to be running. Which it wasn't.

The fix was to add one line to docker-compose.yml:
```yaml
- xpack.security.enabled=false
```

Done. Should have done this from the start.

---

### 3. Logstash crashing silently
Logstash would start, run for about 60 seconds, then disappear from `docker compose ps`. No error message visible. Just gone.

Reason: the log file didn't exist yet. Logstash couldn't find it so it just gave up and left without saying anything.

*Lesson: always check `docker logs logstash` before assuming everything is fine.*

---

### 4. Missing one `}` in logstash.conf
Spent way too long wondering why Logstash kept refusing to start after adding the geoip filter. The error message was:

```
Expected one of [ \t\r\n], "#", "=>" at line 38
```

It was a missing closing curly brace. One character. That's it.

---

### 5. "Other" showing instead of real data
Built a beautiful bar chart showing Top Source IPs. Except it showed:

```
Other → 16,110 events
1.144.155.98 → 33 events
```

Turns out the dataset has hundreds of IPs each with **exactly 33 events**. Perfectly distributed. Every single one. Because it's a simulated lab dataset and someone thought that was a good idea.

No fix. Just vibes. The "Other" stays.

---

### 6. All the map dots were in the ocean
Built the threat map. Looked impressive. Zoomed in. Half the dots were in the middle of the Pacific Ocean. Some were near Antarctica.

First response I got when asking for help: *"The fake coordinates can't be fixed."*

Reader, they were fixed.

The actual fix involved:
- Adding a geoip filter to Logstash to enrich IPs with real coordinates
- Creating a proper `geo_point` index template **before** ingesting
- Waiting for re-ingestion
- Creating a runtime field in Kibana using Painless script
- Deleting and re-adding the map layer with the new field
- Fighting with Kibana's read-only Source details panel
- Eventually just deleting the layer and adding a fresh one

The map now shows dots on actual countries. With color coding by severity. And tooltips. Worth it.

---

### 7. GitHub authentication failure
```
remote: Invalid username or token. Password authentication is not supported.
fatal: Authentication failed
```

GitHub removed password authentication for Git operations. You need a Personal Access Token now. Which I didn't know. So I tried my password four times before reading the error message properly.

---

### 8. Pushed the SSH private key to GitHub
Not my proudest moment. The `.pem` key file for SSHing into the Azure VM somehow ended up in the repo. Fixed immediately with `git rm --cached` but still.

Add this to your `.gitignore` before anything else:
```
*.pem
*.env
*.log
logs/
```

---

## 📸 Screenshots

> Dashboard and investigation screenshots coming soon.

---

## 🏗️ Architecture

```
Datasets (CSV logs)
      ↓
  Logstash (parse, enrich & ingest)
      ↓
Elasticsearch (store & index)
      ↓
   Kibana (visualize & investigate)
      ↓
Cloudflare Tunnel (HTTPS + DDoS protection)
      ↓
   Public URL (teammates & stakeholders)
```

**Infrastructure:**
```
Cloud Provider   → Microsoft Azure (Standard B2as v2)
OS               → Ubuntu 22.04 LTS
Containerization → Docker + Docker Compose
ELK Version      → 8.13.0
Security         → Cloudflare Tunnel (HTTPS + DDoS)
GeoIP            → MaxMind GeoLite2 via Logstash
```

---

## ✨ Features

- **17,000+ security events** ingested from multiple log sources
- **Multi-source ingestion** — supports multiple CSV datasets via Logstash
- **Interactive dashboards** — events over time, severity breakdown, event types
- **Geospatial threat map** — real coordinates via GeoIP enrichment, color coded by severity, with tooltips
- **Threat detection** — DDoS, Brute Force, SQL Injection, Phishing, Ransomware, Malware
- **Kibana Timeline** — incident investigation and attacker tracing
- **VirusTotal integration** — IoC validation for IP addresses and domains
- **Public HTTPS access** — Cloudflare tunnel for team collaboration
- **Dockerized deployment** — fully containerized, easy to replicate

---

## 📊 Dataset

| Dataset | Period | Events | Source |
|---------|--------|--------|--------|
| elk-dataset-1.csv | Dec 2023 | ~16,440 | Academic lab dataset |
| elk-dataset-2.csv | Apr 2025 | ~14,000 | Extended academic dataset |

---

## 🔍 Detected Threats

| Event Type | Count | Severity |
|------------|-------|----------|
| DDoS | 8,184 | High |
| Normal | 4,425 | Low |
| SQL Injection | 795 | High |
| Phishing | 783 | Medium |
| Ransomware | 777 | High |
| Malware | 768 | High |
| Brute Force | 708 | Medium |

**Traffic Actions:** Allowed 42.66% · Blocked 40.78% · Success 8.28% · Failure 8.28%

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Elasticsearch 8.13.0 | Log storage and indexing |
| Logstash 8.13.0 | Log ingestion, parsing and GeoIP enrichment |
| Kibana 8.13.0 | Visualization and investigation |
| Docker + Compose | Containerized deployment |
| Microsoft Azure | Cloud infrastructure |
| Cloudflare Tunnel | HTTPS and DDoS protection |
| MaxMind GeoLite2 | IP geolocation database |
| VirusTotal | IoC validation |
| Ubuntu 22.04 | Server OS |

---

## ⚡ TLDR — Quick Start

### Start the platform
```bash
# 1. Start VM
# Azure Portal → Virtual Machines → SIEM-ELK-Server → Start → wait 2-3 mins

# 2. SSH into VM
ssh -i C:\ELK\SIEM-ELK-Server_key.pem azureuser@<VM_IP_ADDRESS>

# 3. Start Docker
cd ~/ELK
docker compose up -d

# 4. Start Cloudflare tunnel
nohup cloudflared tunnel --url http://localhost:5601 > cloudflared.log 2>&1 &

# 5. Get your public URL
cat cloudflared.log | grep "trycloudflare.com"
```

### Stop the platform
```bash
# 1. Stop Cloudflare tunnel
pkill cloudflared

# 2. Stop Docker gracefully
cd ~/ELK
docker compose down

# 3. Stop VM
# Azure Portal → Virtual Machines → SIEM-ELK-Server → Stop → confirm
```

---

## 🚀 Full Setup Guide

### Prerequisites
- Microsoft Azure account (Standard B2as v2 — 2 vCPUs, 8GB RAM)
- Ubuntu 22.04 LTS VM
- Docker + Docker Compose installed
- Cloudflared installed
- CSV log datasets

### 1. Clone this repository
```bash
git clone https://github.com/umaarlll/siem-elk-azure.git
cd siem-elk-azure
```

### 2. Set virtual memory (do this or Elasticsearch will crash)
```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 3. Add your datasets
```bash
cp your-dataset-1.csv ./logs/elk-dataset-1.csv
cp your-dataset-2.csv ./logs/elk-dataset-2.csv
```

### 4. Create geo_point index template (do this BEFORE ingesting or the map won't work)
```bash
curl -u elastic:yourpassword -X PUT "http://localhost:9200/_index_template/siem-logs-template" \
  -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["siem-logs-*"],
  "template": {
    "mappings": {
      "properties": {
        "source_geo":         { "type": "geo_point" },
        "dest_geo":           { "type": "geo_point" },
        "geoip.geo.location": { "type": "geo_point" }
      }
    }
  }
}'
```

### 5. Launch ELK Stack
```bash
docker compose up -d
docker compose ps   # verify all 3 containers are running
```

### 6. Configure Kibana
```
Open http://localhost:5601
→ Stack Management → Data Views → Create data view
→ Index pattern: siem-logs-*
→ Timestamp: @timestamp
→ Save
```

### 7. Start Cloudflare tunnel
```bash
nohup cloudflared tunnel --url http://localhost:5601 > cloudflared.log 2>&1 &
cat cloudflared.log | grep "trycloudflare.com"
```

---

## 🔧 Auto-start on VM Boot (Optional)

### Auto-start Docker
```bash
sudo systemctl enable docker
```

### Auto-start Cloudflared
```bash
sudo nano /etc/systemd/system/cloudflared.service
```

Paste:
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
ExecStart=cloudflared tunnel --url http://localhost:5601
Restart=always
User=azureuser

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
journalctl -u cloudflared | grep "trycloudflare.com"
```

---

## 🗂️ Project Structure

```
siem-elk-azure/
├── docker-compose.yml        # ELK Stack services
├── logstash/
│   └── logstash.conf         # Log ingestion pipeline
├── logs/                     # Dataset directory (gitignored)
│   ├── elk-dataset-1.csv
│   └── elk-dataset-2.csv
├── screenshots/              # Dashboard screenshots
└── README.md
```

---

## 👥 Team Contributions

| Member | Role |
|--------|------|
| Umar | Infrastructure setup, Docker deployment, Dashboard engineering, Monitoring phase |
| Teammate 2 | Detection phase |
| Teammate 3 | Kibana Timeline investigation |
| Teammate 4 | VirusTotal IoC analysis & report |

---

## 📋 Assignment Progress

| Task | Marks | Status |
|------|-------|--------|
| Dashboard Engineering | 10 | ✅ Done |
| Monitoring Phase | 10 | ✅ Done |
| Detection Phase | 15 | 🚧 In Progress |
| ELK Timeline Investigation | 15 | 🚧 In Progress |
| VirusTotal Investigation | 10 | 🚧 In Progress |
| **Total** | **60** | |

---

## 🗺️ Planned Improvements

- [ ] VirusTotal API integration for automated IoC enrichment
- [ ] Makefile for one-command start/stop
- [ ] Terraform IaC for reproducible Azure deployment

---

## ⚠️ Security Notice

This repository does not contain any credentials, passwords or API keys. Before deploying:
- Change the default Elasticsearch password
- Never commit `.env` files or credentials
- Never commit `.pem` key files (ask me how I know)
- Use environment variables for sensitive values

---

## 📄 License

This project is for academic purposes only.

---

> Built with ❤️ and an unhealthy amount of `docker logs logstash` — ELK SIEM on Azure
