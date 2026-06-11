variable "proxmox_endpoint" {
    type = string
}

variable "prox_mox_api_token" {
    type = string
    sensitive = true
}

variable "proxmox_node" {
    type = string
    default = "pve"
}

variable "ssh_public_key" {
    type = string
}

variable "vm_password" {
    type = string
    sensitive = true
}

variable "base_ip_prefix" {
    type = string
    default = ""
}

variable "gateway" {
    type = string
    default = ""
}

variable "vm_template" {
    type = string
    default = "archlinux-cloud"
}

variable "lxc_template" {
    type = string
    default = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst" 
}

variable "control_plane_count" {
    type = number
    default = 3
}

variable "worker_count"{
    type = number
    default = 3
}