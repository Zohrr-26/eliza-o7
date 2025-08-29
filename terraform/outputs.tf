# Outputs - Informations importantes après le déploiement

output "resource_group_name" {
  description = "Nom du groupe de ressources"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Nom du compte de stockage"
  value       = azurerm_storage_account.main.name
}

output "storage_connection_string" {
  description = "Chaîne de connexion du compte de stockage"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "function_app_name" {
  description = "Nom de la Function App"
  value       = azurerm_linux_function_app.main.name
}

output "function_app_url" {
  description = "URL de la Function App"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}"
}

output "sql_server_name" {
  description = "Nom du serveur SQL"
  value       = azurerm_mssql_server.main.name
}

output "sql_server_fqdn" {
  description = "FQDN du serveur SQL"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "Nom de la base de données"
  value       = azurerm_mssql_database.main.name
}

output "sql_connection_string" {
  description = "Chaîne de connexion SQL"
  value       = local.db_conn_str
  sensitive   = true
}

output "frontend_url" {
  description = "URL du frontend"
  value       = "http://${azurerm_linux_web_app.streamlit.default_hostname}"
}

output "deployment_commands" {
  description = "Commandes de déploiement"
  value = {
    upload_model = "az storage blob upload --account-name ${azurerm_storage_account.main.name} --container-name models --name model.ubj --file model.ubj"
    deploy_function = "func azure functionapp publish ${azurerm_linux_function_app.main.name}"
    test_api = "curl -X POST https://${azurerm_linux_function_app.main.default_hostname}/api/test"
  }
}
