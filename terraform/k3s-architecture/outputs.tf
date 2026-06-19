output "k3s_haproxy_ip" {
  value = "${var.base_ip_prefix}.200"
}

output "k3s_control_plane_ips" {
  value = [for i in range(var.control_plane_count) : "${var.base_ip_prefix}.${201 + i}"]
}

output "k3s_worker_ips" {
  value = [for i in range(var.worker_count) : "${var.base_ip_prefix}.${210 + i}"]
}