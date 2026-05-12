terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "siem_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_virtual_network" "siem_vnet" {
  name                = "siem-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.siem_rg.location
  resource_group_name = azurerm_resource_group.siem_rg.name
}

resource "azurerm_subnet" "siem_subnet" {
  name                 = "siem-subnet"
  resource_group_name  = azurerm_resource_group.siem_rg.name
  virtual_network_name = azurerm_virtual_network.siem_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_security_group" "siem_nsg" {
  name                = "siem-nsg"
  location            = azurerm_resource_group.siem_rg.location
  resource_group_name = azurerm_resource_group.siem_rg.name

  security_rule {
    name                       = "allow-ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow-kibana"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5601"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow-elasticsearch"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "9200"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "siem_nsg_assoc" {
  subnet_id                 = azurerm_subnet.siem_subnet.id
  network_security_group_id = azurerm_network_security_group.siem_nsg.id
}

resource "azurerm_public_ip" "siem_pip" {
  name                = "siem-public-ip"
  location            = azurerm_resource_group.siem_rg.location
  resource_group_name = azurerm_resource_group.siem_rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "siem_nic" {
  name                = "siem-nic"
  location            = azurerm_resource_group.siem_rg.location
  resource_group_name = azurerm_resource_group.siem_rg.name

  ip_configuration {
    name                          = "siem-ip-config"
    subnet_id                     = azurerm_subnet.siem_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.siem_pip.id
  }
}

resource "azurerm_linux_virtual_machine" "siem_vm" {
  name                  = "siem-elk-vm"
  location              = azurerm_resource_group.siem_rg.location
  resource_group_name   = azurerm_resource_group.siem_rg.name
  size                  = "Standard_B2as_v2"
  admin_username        = var.admin_username
  network_interface_ids = [azurerm_network_interface.siem_nic.id]
  custom_data           = filebase64("cloud-init.yaml")

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
}

resource "azurerm_storage_account" "siem_storage" {
  name                     = "siemelkstorage"
  resource_group_name      = azurerm_resource_group.siem_rg.name
  location                 = azurerm_resource_group.siem_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_nested_items_to_be_public = true
}

resource "azurerm_storage_container" "datasets" {
  name                  = "datasets"
  storage_account_name  = azurerm_storage_account.siem_storage.name
  container_access_type = "blob"
}

resource "azurerm_storage_blob" "dataset1" {
  name                   = "elk-dataset-1.csv"
  storage_account_name   = azurerm_storage_account.siem_storage.name
  storage_container_name = azurerm_storage_container.datasets.name
  type                   = "Block"
  source                 = "../logs/elk-dataset-1.csv"
}

resource "azurerm_storage_blob" "dataset2" {
  name                   = "elk-dataset-2.csv"
  storage_account_name   = azurerm_storage_account.siem_storage.name
  storage_container_name = azurerm_storage_container.datasets.name
  type                   = "Block"
  source                 = "../logs/elk-dataset-2.csv"
}




















