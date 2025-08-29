# Locals - Valeurs calculées et tags communs
locals {
  
  # Noms des ressources avec convention de nommage
  resource_group_name    = "rg-${var.project_name}-${var.environment}"

  storage_account_name   = "${var.project_name}storagebecode"
  function_app_name      = "${var.project_name}-functionapp"
  sql_server_name        = "${var.project_name}-sql-${var.environment}"

  sql_database_name      = "${var.project_name}-db-${var.environment}"

  db_conn_str = join("", [
    "Driver={ODBC Driver 18 for SQL Server};",
    "Server=${azurerm_mssql_server.main.fully_qualified_domain_name};",
    "Database=${azurerm_mssql_database.main.name};",
    "Uid=${var.sql_admin_username};",
    "Pwd=${var.sql_admin_password};"
  ])
}
