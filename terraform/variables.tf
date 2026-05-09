variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "admin_username" {
  description = "VM admin username"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
}
