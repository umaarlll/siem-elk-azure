# siem-elk-azure

A cloud-based SIEM platform running the ELK stack on Azure, fully automated with Terraform and cloud-init. What started as a university assignment turned into a proper IaC project because why deploy manually when you can just terraform apply and go touch grass.

## What is this

This spins up a full security monitoring stack on Azure from scratch. One command and you get a VM with Elasticsearch, Kibana, and Logstash running, datasets loaded, and everything configured. No SSH-ing in, no manual setup, nothing.

The dataset is a mix of simulated network security events covering DDoS, SQL injection, phishing, ransomware, malware, and brute force attacks. About 17k events total across two datasets.

## Stack

- Terraform for provisioning all Azure infrastructure
- cloud-init for bootstrapping Docker and ELK on first boot
- Elasticsearch + Kibana + Logstash 8.13.0
- Azure Blob Storage for dataset hosting
- Cloudflare tunnel for remote Kibana access (optional)

## Infrastructure

Everything lives inside one resource group in East Asia region.

- Virtual network with a dedicated subnet
- Network security group allowing SSH (22), Kibana (5601), and Elasticsearch (9200)
- Static public IP
- Ubuntu 22.04 VM running Standard B2as v2 (2 vCPU, 8GB RAM)

## How to use

You need Terraform and Azure CLI installed. Then just log in and go.

```bash
az login
cd terraform
terraform init
terraform apply
```

Grab the IP from the output, go to http://YOUR_IP:5601, and log in with the credentials you set. That is it.

## What happens on first boot

cloud-init handles everything automatically so you do not have to touch the VM at all.

1. Installs Docker and Docker Compose
2. Sets vm.max_map_count to 262144 (Elasticsearch needs this or it refuses to start)
3. Downloads both datasets from Azure Blob Storage
4. Runs fix_coordinates.py to replace fake geo coordinates in dataset 1 with real country centroids
5. Writes docker-compose.yml and logstash.conf
6. Starts the ELK stack
7. Waits for Elasticsearch to be healthy, then sets the kibana_system password

The whole thing takes around 5 to 10 minutes after the VM is created.

## Setup

Copy the example vars file and fill in your values.

```bash
cp terraform.tfvars.example terraform.tfvars
```

You need to fill in your Azure subscription ID, admin username, and SSH public key. The elastic password goes in there too, keep that file out of git.

## Tear down

```bash
terraform destroy
```

Blows up everything. Clean slate. Run terraform apply again and it rebuilds from scratch.

If you only want to rebuild the VM without touching the network resources, target just the VM.

```bash
terraform destroy -target=azurerm_linux_virtual_machine.siem_vm
terraform apply
```

This keeps the same public IP so you do not have to update anything.

## Dashboard

The Kibana dashboard covers:

- Total events, DDoS count, high severity count, blocked vs allowed traffic
- Global threat map with source and destination geolocation
- Event type breakdown, protocol distribution, traffic action donut
- Top source countries for both datasets
- Top source IPs
- Events over time

## Known quirks

Top source IPs for the 2023 dataset shows mostly "Other" because every IP in that dataset has exactly 33 events each. Simulated dataset behavior, nothing wrong with the config.

Some map dots land in the ocean because IP geolocation is not perfect. Normal limitation.

Cloudflare tunnel URL changes every restart on the free tier. If you want a stable URL you need a proper domain.

## Planned improvements

- Move secrets into Azure Key Vault
- Add storage account and blob uploads into Terraform so everything is one terraform apply
- VirusTotal API integration for automated IOC enrichment
