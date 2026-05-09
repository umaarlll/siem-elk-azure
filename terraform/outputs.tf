output "vm_public_ip" {
  value = azurerm_public_ip.siem_pip.ip_address
}
