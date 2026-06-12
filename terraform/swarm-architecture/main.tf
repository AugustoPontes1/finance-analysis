# --- HAProxy load balancer (LXC 104) ───────────────────────────────────────────
resource "proxmox_virtual_enviroment_container" "haproxy" {
    node_name = var.proxmox_node
    vm_id = 104
    description = "HAProxy - Swarm ingress"
    unprivileged = true

    operating_system {
        template_file_id = var.lxc_template
        type = "debian"
    }

    cpu { cores = 1 }

    memory { dedicated = 512 }

    network_interface {
        name = "eth0"
        bridge = "vmbr0"
        ip_v4_config {
            address = "${var.base_ip_prefix}.104/24"
            gateway = var.gateway
        }
    }

    initialization {
        hostname = "haproxy"
        user_account {
            password = var.vm_password
            keys = [var.ssh_public_key]
        }
    }

    disk {
        datastore_id = "loval-lvm"
        size = 8
    }
}

# ── Swarm manager (VM 100) ─────────────────────────────────────────────────────
resource "proxmox_virtual_enviroment_vm" "swarm_manager" {
    node_name = var.proxmox_node
    vm_id = 100
    name = "arch-vm-1"
    description = "Docker Swarm manager"

    clone {
        vm_id = var.vm_template
        full = true
    }

    cpu {
        cores = 2
        type = "host"
    }

    memory { dedicated = 4096}

    disk {
        datastore_id = "local-lvm"
        interface = "scsi0"
        size = 32
    }

    network_device {
        bridge = "vmbr0"
        model = "virtio"
    }

    initialization{
        ip_config {
            ipv4 {
                address = "${var.base_ip_prefix}.100/24"
                gateway = var.gateway
            }
        }
        user_account {
            password = var.vm_password
            keys = [var.ssh_public_key]
        }
    }
}

# ── Swarm workers (VMs 102 & 103) ─────────────────────────────────────────────
locals {
    swarm_workers = {
        "arch-vm-2" = { vm_id = 102, ip_last_octet = 102 }
        "arch-vm-3" = { vm_id = 103, ip_last_octet = 103 }
    }
}

resource "proxmox_virtual_enviroment_vm" "swarm_worker" {
    for_each = local.swarm_workers

    node_name = var.proxmox_node
    vm_id = each.value.vm_id
    name = each.key
    description = "Docker Swarm worker"

    clone {
        vm_id = var.vm_template
        full = true
    }

    cpu {
        cores = 2
        type = "host"
    }

    memory { dedicated = 2048 }

    disk {
        datastore_id = "local-lvm"
        interface = "scsi0"
        size = 32
    }

    network_device {
        bridge = "vmbr0"
        model = "virtio"
    }

    initialization {
        ip_config {
            ipv4 {
                address = "${var.base_ip_prefix}.${each.value.ip_last_octet}/24"
                gateway = var.gateway
            }
        }
        user_account {
            password = var.vm_password
            keys = [var.ssh_public_key]
        }
    }
}