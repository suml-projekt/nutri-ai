terraform {
  required_version = ">= 1.6.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

locals {
  streamlit_image = "${azurerm_container_registry.main.login_server}/streamlit-app:${var.streamlit_image_tag}"
  common_tags = {
    project     = "nutri-ai"
    environment = var.environment_name
    managed_by  = "terraform"
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "container_apps" {
  name                = var.container_apps_identity_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.container_apps.principal_id
}

resource "azurerm_storage_account" "ollama" {
  name                     = var.ollama_storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.common_tags
}

resource "azurerm_storage_share" "ollama" {
  name               = var.ollama_file_share_name
  storage_account_id = azurerm_storage_account.ollama.id
  quota              = var.ollama_file_share_quota_gb
}

resource "azurerm_container_app_environment" "main" {
  name                       = var.container_app_environment_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.common_tags
}

resource "azurerm_container_app_environment_storage" "ollama" {
  name                         = var.ollama_environment_storage_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  account_name                 = azurerm_storage_account.ollama.name
  share_name                   = azurerm_storage_share.ollama.name
  access_key                   = azurerm_storage_account.ollama.primary_access_key
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app" "ollama" {
  name                         = var.ollama_container_app_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  ingress {
    external_enabled           = false
    target_port                = var.ollama_port
    allow_insecure_connections = true

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    volume {
      name         = "ollama-data"
      storage_name = azurerm_container_app_environment_storage.ollama.name
      storage_type = "AzureFile"
    }

    container {
      name   = "ollama"
      image  = var.ollama_image
      cpu    = var.ollama_cpu
      memory = var.ollama_memory

      env {
        name  = "OLLAMA_HOST"
        value = "0.0.0.0:${var.ollama_port}"
      }

      volume_mounts {
        name = "ollama-data"
        path = "/root/.ollama"
      }
    }
  }
}

resource "azurerm_container_app" "streamlit" {
  count = var.deploy_streamlit_app ? 1 : 0

  name                         = var.streamlit_container_app_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.container_apps.id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.container_apps.id
  }

  ingress {
    external_enabled = true
    target_port      = var.streamlit_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = var.streamlit_min_replicas
    max_replicas = var.streamlit_max_replicas

    container {
      name   = "streamlit"
      image  = local.streamlit_image
      cpu    = var.streamlit_cpu
      memory = var.streamlit_memory

      env {
        name  = "LLM_URL"
        value = "http://${azurerm_container_app.ollama.ingress[0].fqdn}"
      }

      env {
        name  = "REQUIRED_MODELS"
        value = join(",", var.required_ollama_models)
      }
    }
  }

  depends_on = [
    azurerm_role_assignment.acr_pull,
    azurerm_container_app.ollama
  ]
}
