variable "proxmox_endpoint"  { type = string }
variable "proxmox_api_token" { type = string; sensitive = true }
variable "proxmox_node"      { type = string; default = "pve" }
variable "ssh_public_key"    { type = string }
variable "vm_password"       { type = string; sensitive = true }

variable "base_ip_prefix" { type = string; default = "192.168.1" }
variable "gateway"         { type = string; default = "192.168.1.1" }

variable "vm_template"  { type = string; default = "archlinux-cloud" }
variable "lxc_template" { type = string; default = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst" }

variable "control_plane_count" {
  type    = number
  default = 3   # HA — use 1 for a single-node setup
}

variable "worker_count" {
  type    = number
  default = 3
}