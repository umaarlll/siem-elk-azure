# Cloud-Based Threat Monitoring Infrastructure Using ELK Stack on Azure

A fully automated SIEM platform built on the ELK stack, provisioned on Microsoft Azure using Terraform and cloud-init. Zero manual steps after `terraform apply`.

---

## Architecture

```
Developer
    |
    | terraform apply
    v
Terraform (IaC)
    |
    | provisions 12 resources
    v
Azure Resource Group: siem-elk-rg (East Asia)
    |
    +-- Azure Virtual Network: siem-vnet (10.0.0.0/16)
    |       |
    |       +-- Subnet: siem-subnet (10.0.1.0/24)
    |               |
    |               +-- NSG: ports 22, 5601, 9200
    |               |
    |               +-- VM: siem-elk-vm (Ubuntu 22.04, Standard_B2as_v2)
    |                       |
    |                       | cloud-init on first boot
    |                       |
    |                       +-- pulls fix_coordinates.py from GitHub
    |                       +-- pulls dashboard.ndjson from GitHub
    |                       +-- downloads datasets from Blob Storage
    |                       +-- Docker: Logstash -> Elasticsearch -> Kibana
    |
    +-- Azure Blob Storage: siemelkstorage
            |
            +-- Container: datasets
                    +-- elk-dataset-1.csv
                    +-- elk-dataset-2.csv
```

---

## Repository Structure

```
siem-elk-azure/
├── fix_coordinates.py          # normalizes country coordinates in dataset1
├── logstash/
│   └── logstash.conf           # pipeline: CSV parse, geo mapping, ES output
├── logs/                       # gitignored — place CSVs here locally
├── kibana/
│   └── dashboard.ndjson        # exported Kibana dashboard (auto-imported on boot)
├── README.md
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── cloud-init.yaml         # full VM automation on first boot
    ├── terraform.tfvars        # gitignored
    └── terraform.tfvars.example
```

---

## Prerequisites

- Terraform >= 1.0
- Azure CLI authenticated (`az login`)
- An Azure subscription
- SSH key pair

---

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/umaarlll/siem-elk-azure.git
cd siem-elk-azure
```

**2. Place datasets**

Put your CSV files in the `logs/` directory:

```
logs/elk-dataset-1.csv
logs/elk-dataset-2.csv
```

**3. Configure variables**

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
subscription_id     = "your-subscription-id"
resource_group_name = "siem-elk-rg"
location            = "eastasia"
admin_username      = "azureuser"
ssh_public_key      = "ssh-rsa AAAA..."
```

**4. Deploy**

```bash
cd terraform
terraform init
terraform apply
```

Provisioning takes approximately 10-15 minutes. cloud-init runs automatically and handles everything on first boot.

**5. Access Kibana**

```
URL      : http://<VM_PUBLIC_IP>:5601
Username : elastic
Password : defined in terraform.tfvars / .env
```

The SIEM Security Overview dashboard and Global Threat Source Map are imported automatically.

**6. Tear down**

```bash
terraform destroy
```

---

## What cloud-init Does on First Boot

Executed automatically in this order:

```
1.  Install Docker and Docker Compose
2.  Set vm.max_map_count=262144 (required by Elasticsearch)
3.  Download elk-dataset-1.csv and elk-dataset-2.csv from Azure Blob Storage
4.  Download fix_coordinates.py from GitHub and run it on dataset1
5.  Write docker-compose.yml, logstash.conf, and .env
6.  Start Elasticsearch, Logstash, and Kibana via docker compose
7.  Wait for Elasticsearch to be healthy, then set kibana_system password
8.  Create index template with geo_point mapping before Logstash indexes data
9.  Wait for Kibana to be healthy, then import dashboard.ndjson via saved objects API
```

---

## Data Pipeline

```
elk-dataset-1.csv  (network threat logs with geo coordinates)
elk-dataset-2.csv  (firewall logs)
        |
        | Logstash
        | - CSV parse with explicit column mapping
        | - Date parsing to @timestamp
        | - GeoIP enrichment via MaxMind
        | - Coordinate normalization to source_geo and dest_geo (geo_point)
        | - Copy source_geo to real_threat_location for map visualization
        v
Elasticsearch index: siem-logs-YYYY.MM.dd
        |
        v
Kibana
- SIEM Security Overview dashboard
- Global Threat Source Map (real_threat_location field)
```

---

## Tradeoffs and Known Issues

**ELASTIC_PASSWORD is hardcoded in cloud-init**
The password is stored in plaintext in `cloud-init.yaml` and `.env`. The correct fix is Azure Key Vault with a VM Managed Identity fetching the secret at boot. Not implemented in this version.

**Map coordinates are partially normalized**
`fix_coordinates.py` maps country names to real centroids with jitter. It covers approximately 100 countries. Rows with unrecognized country names retain the original random coordinates from the fake dataset, which places some dots in oceans.

**Terraform state is local**
`terraform.tfstate` is stored locally. In a team or production environment this should be moved to an Azure Blob Storage backend with state locking.

**No HTTPS**
Kibana is served over HTTP on port 5601. Acceptable for a lab environment. Production would require a reverse proxy with TLS termination.

**NSG allows 9200 from any source**
Elasticsearch port 9200 is open to the internet. In production this should be restricted to the subnet or a specific IP range.

**Elasticsearch index template must exist before first indexing**
If Logstash indexes data before the geo_point template is applied, the mapping defaults to float lat/lon pairs and the map visualization breaks. cloud-init handles this by creating the template between the kibana_system password step and Logstash's first successful connection.

---

## Terraform Resources (12 total)

| Resource | Name |
|---|---|
| Resource Group | siem-elk-rg |
| Virtual Network | siem-vnet |
| Subnet | siem-subnet |
| Network Security Group | siem-nsg |
| NSG Association | siem-nsg-assoc |
| Public IP | siem-public-ip |
| Network Interface | siem-nic |
| Virtual Machine | siem-elk-vm |
| Storage Account | siemelkstorage |
| Storage Container | datasets |
| Storage Blob | elk-dataset-1.csv |
| Storage Blob | elk-dataset-2.csv |

---

## Future Improvements

- Azure Key Vault for secret management
- GitHub Actions CI/CD — `terraform plan` on PR, `terraform apply` on merge
- Terraform remote state backend on Azure Blob Storage
- HTTPS with Let's Encrypt or Azure Application Gateway
- Expand `fix_coordinates.py` to cover all countries in the dataset
