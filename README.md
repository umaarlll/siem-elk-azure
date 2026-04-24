# 🔐 Cloud-Based SIEM Platform using ELK Stack

A Security Information and Event Management (SIEM) platform built with the Elastic Stack (ELK), containerized with Docker and deployed on Microsoft Azure. The platform ingests, parses and visualizes 17,000+ security events enabling real-time threat detection, monitoring and incident investigation.

> **Status:** 🚧 In Progress — Detection & Investigation phase coming soon.

---

## 📸 Screenshots

> Dashboard, Threat Map and Investigation screenshots coming soon.

---

## 🏗️ Architecture

```
Datasets (CSV logs)
      ↓
  Logstash (parse & ingest)
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
Cloud Provider  → Microsoft Azure (Standard B2as v2)
OS              → Ubuntu 22.04 LTS
Containerization→ Docker + Docker Compose
ELK Version     → 8.13.0
Security        → Cloudflare Tunnel (HTTPS + DDoS)
```

---

## ✨ Features

- **17,000+ security events** ingested from multiple log sources
- **Multi-source ingestion** — supports multiple CSV datasets via Logstash
- **Interactive dashboards** — events over time, severity breakdown, event types
- **Geospatial threat map** — visualizes global attack origins and destinations
- **Threat detection** — DDoS, Brute Force, SQL Injection, Phishing, Ransomware, Malware
- **Kibana Timeline** — incident investigation and attacker tracing
- **VirusTotal integration** — IoC validation for IP addresses and domains
- **Public HTTPS access** — secured Cloudflare tunnel for team collaboration
- **Dockerized deployment** — fully containerized, easy to replicate

---

## 📊 Dataset

| Dataset | Period | Events | Source |
|---------|--------|--------|--------|
| elk-dataset-1.csv | Dec 2023 | ~16,440 | Academic lab dataset |
| elk-dataset-2.csv | Apr 2025 | ~14,000 | Extended academic dataset |

**Fields include:** Device Time, Source/Destination IP, Source/Destination Port, Protocol, Geolocation, Event Type, Event Severity, Action, Details

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
| Logstash 8.13.0 | Log ingestion and parsing |
| Kibana 8.13.0 | Visualization and investigation |
| Docker + Compose | Containerized deployment |
| Microsoft Azure | Cloud infrastructure |
| Cloudflare Tunnel | HTTPS and DDoS protection |
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
git clone https://github.com/yourusername/siem-elk-azure.git
cd siem-elk-azure
```

### 2. Set virtual memory (required for Elasticsearch)
```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 3. Configure environment
```bash
# Edit docker-compose.yml and set your password
nano docker-compose.yml
```

### 4. Add your datasets
```bash
cp your-dataset-1.csv ./logs/elk-dataset-1.csv
cp your-dataset-2.csv ./logs/elk-dataset-2.csv
```

### 5. Launch ELK Stack
```bash
docker compose up -d

# Verify all 3 containers are running
docker compose ps

# Check data ingestion
curl -u elastic:yourpassword "http://localhost:9200/siem-logs-*/_count"
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

# Check URL
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

## ⚠️ Security Notice

This repository does not contain any credentials, passwords or API keys. Before deploying:
- Change the default Elasticsearch password
- Never commit `.env` files or credentials
- Use environment variables for sensitive values

---

## 📄 License

This project is for academic purposes only.

---

> Built with ❤️ as part of a Cybersecurity assignment — ELK Stack SIEM on Azure
