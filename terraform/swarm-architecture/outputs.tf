output "haproxy_ip" {
    value = "${var.base_ip_prefix}.104"
}

output "swarm_manager_ip" {
    value = "${var.base_ip_prefix}.100"
}

output "swarm_worker_ips" {
    value = { for k, v in local.swarm_workers : k => "${var.base_ip_prefix}.${v.ip_last_octet}"}
}