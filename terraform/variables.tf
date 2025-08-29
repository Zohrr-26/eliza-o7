# Variables Terraform - Description et validation

variable "project_name" {
  description = "Nom du projet (utilisé comme préfixe)"
  type        = string
  default     = "eliza"
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Région Azure"
  type        = string
  default     = "francecentral"
}

variable "sql_admin_username" {
  description = "Nom d'utilisateur administrateur SQL"
  type        = string
  default     = "admin_username"
}

variable "sql_admin_password" {
  description = "Mot de passe administrateur SQL"
  type        = string
  sensitive   = true
  default     = "admin_password" # should include upper, lower and number char
}

variable "allowed_ip_addresses" {
  description = "Adresses IP autorisées pour SQL Server"
  type        = list(string)
  default     = ["0.0.0.0"] # Remplacez par vos IPs réelles
}

