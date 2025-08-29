# Configuration du provider Azure
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  # subscription_id = export ARM_SUBSCRIPTION_ID
}

# Groupe de ressources
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
}

# Compte de stockage principal
resource "azurerm_storage_account" "main" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # Permettre l'accès depuis Azure Functions
  allow_nested_items_to_be_public = false
}

resource "azurerm_storage_container" "models" {
  name                  = "models"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}

# Ensuite créer le blob (fichier) dans le conteneur
resource "azurerm_storage_blob" "model_file" {
  name                   = "model.ubj"
  storage_account_name   = azurerm_storage_account.main.name
  storage_container_name = azurerm_storage_container.models.name
  type                   = "Block"
  source                 = "../model.ubj"  # Chemin vers le fichier local
}

# App Service Plan pour Azure Functions
resource "azurerm_service_plan" "main" {
  name                = "asp-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1" # "Y1" # Consumption plan
}

# Function App
resource "azurerm_linux_function_app" "main" {
  name                = local.function_app_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key
  service_plan_id            = azurerm_service_plan.main.id

  site_config {
    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    "FUNCTIONS_EXTENSION_VERSION"       = "~4"
    "FUNCTIONS_WORKER_RUNTIME"          = "python"
    "AZURE_STORAGE_CONNECTION_STRING"   = azurerm_storage_account.main.primary_connection_string
    "DATABASE_URI"                      = local.db_conn_str
    "WEBSITE_RUN_FROM_PACKAGE"          = "1"
    "DB_CONN_STR"                       = local.db_conn_str
  }
}

# Serveur SQL Azure
resource "azurerm_mssql_server" "main" {
  name                         = local.sql_server_name
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

# Base de données SQL
resource "azurerm_mssql_database" "main" {
  name           = "${var.project_name}-db"
  server_id      = azurerm_mssql_server.main.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  sku_name       = "S0"
  zone_redundant = false
}

# Règle de pare-feu pour autoriser les services Azure
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Règles de pare-feu pour les adresses IP spécifiées
resource "azurerm_mssql_firewall_rule" "allowed_ips" {
  count            = length(var.allowed_ip_addresses)
  name             = "AllowedIP-${count.index}"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = var.allowed_ip_addresses[count.index]
  end_ip_address   = var.allowed_ip_addresses[count.index]
}

# Web App for Streamlit (docker)
resource "azurerm_linux_web_app" "streamlit" {
  name                = "${var.project_name}-streamlit"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_image_name   = "zohrr26/eliza-o7:latest"
      docker_registry_url = "https://index.docker.io" # https://index.docker.io/v1
    }
  }

  app_settings = {
    WEBSITES_PORT = "8501"
  }
}
