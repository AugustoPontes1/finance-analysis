# ── HAProxy – K3S API load balancer (LXC 200) ─────────────────────────────────
resource "proxmox_virtual_environment_container" "k3s_haproxy" {
  node_name    = var.proxmox_node
  vm_id        = 200
  description  = "HAProxy – K3S API server LB"
  unprivileged = true

  operating_system {
    template_file_id = var.lxc_template
    type             = "debian"
  }

  cpu    { cores = 1 }
  memory { dedicated = 512 }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
    ip_v4_config {
      address = "${var.base_ip_prefix}.200/24"
      gateway = var.gateway
    }
  }

  initialization {
    hostname = "k3s-haproxy"
    user_account {
      password = var.vm_password
      keys     = [var.ssh_public_key]
    }
  }

  disk {
    datastore_id = "local-lvm"
    size         = 8
  }
}

# ── K3S control plane nodes (VMs 201, 202, 203) ───────────────────────────────
resource "proxmox_virtual_environment_vm" "k3s_control_plane" {
  count = var.control_plane_count

  node_name   = var.proxmox_node
  vm_id       = 201 + count.index
  name        = "k3s-master-${count.index + 1}"
  description = "K3S control plane"

  clone {
    vm_id = var.vm_template
    full  = true
  }

  cpu {
    cores = 2
    type  = "host"
  }

  memory { dedicated = 4096 }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 40
  }

  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "${var.base_ip_prefix}.${201 + count.index}/24"
        gateway = var.gateway
      }
    }
    user_account {
      password = var.vm_password
      keys     = [var.ssh_public_key]
    }
  }
}

# ── K3S worker nodes (VMs 210, 211, 212) ──────────────────────────────────────
resource "proxmox_virtual_environment_vm" "k3s_worker" {
  count = var.worker_count

  node_name   = var.proxmox_node
  vm_id       = 210 + count.index
  name        = "k3s-worker-${count.index + 1}"
  description = "K3S worker node"

  clone {
    vm_id = var.vm_template
    full  = true
  }

  cpu {
    cores = 2
    type  = "host"
  }

  memory { dedicated = 2048 }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 40
  }

  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "${var.base_ip_prefix}.${210 + count.index}/24"
        gateway = var.gateway
      }
    }
    user_account {
      password = var.vm_password
      keys     = [var.ssh_public_key]
    }
  }
}