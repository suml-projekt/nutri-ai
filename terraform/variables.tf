variable "subscription_id" {
  description = "Azure subscription ID used by the azurerm provider."
  type        = string
  default     = null
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "polandcentral"
}

variable "environment_name" {
  description = "Deployment environment label used in tags."
  type        = string
  default     = "prod"
}

variable "resource_group_name" {
  description = "Resource group for the application infrastructure."
  type        = string
  default     = "rg-suml-projekt-studia"
}

variable "log_analytics_workspace_name" {
  description = "Log Analytics workspace name for Container Apps logs."
  type        = string
  default     = "law-suml-projekt-studia"
}

variable "acr_name" {
  description = "Azure Container Registry name. Must be globally unique."
  type        = string
  default     = "acrsumlprojektstudia"
}

variable "container_apps_identity_name" {
  description = "User-assigned identity used by Container Apps to pull from ACR."
  type        = string
  default     = "id-aca-suml-projekt-studia"
}

variable "container_app_environment_name" {
  description = "Azure Container Apps environment name."
  type        = string
  default     = "aca-env-suml"
}

variable "streamlit_container_app_name" {
  description = "Public Streamlit Container App name."
  type        = string
  default     = "streamlit-app"
}

variable "ollama_container_app_name" {
  description = "Internal Ollama Container App name."
  type        = string
  default     = "ollama"
}

variable "ollama_image" {
  description = "Ollama container image."
  type        = string
  default     = "ollama/ollama:latest"
}

variable "required_ollama_models" {
  description = "Comma-joined into REQUIRED_MODELS for the Streamlit app to pull on startup."
  type        = list(string)
  default     = ["llava:latest", "llama3:latest"]
}

variable "streamlit_image_tag" {
  description = "Streamlit image tag to deploy from ACR."
  type        = string
  default     = "latest"
}

variable "deploy_streamlit_app" {
  description = "Set false for first infrastructure bootstrap before the Streamlit image exists in ACR."
  type        = bool
  default     = true
}

variable "streamlit_port" {
  description = "Streamlit container port."
  type        = number
  default     = 8501
}

variable "ollama_port" {
  description = "Ollama container port."
  type        = number
  default     = 11434
}

variable "streamlit_cpu" {
  description = "CPU cores assigned to the Streamlit app."
  type        = number
  default     = 0.5
}

variable "streamlit_memory" {
  description = "Memory assigned to the Streamlit app."
  type        = string
  default     = "1Gi"
}

variable "streamlit_min_replicas" {
  description = "Minimum Streamlit replicas."
  type        = number
  default     = 1
}

variable "streamlit_max_replicas" {
  description = "Maximum Streamlit replicas."
  type        = number
  default     = 1
}

variable "ollama_cpu" {
  description = "CPU cores assigned to Ollama."
  type        = number
  default     = 2
}

variable "ollama_memory" {
  description = "Memory assigned to Ollama."
  type        = string
  default     = "4Gi"
}

variable "ollama_storage_account_name" {
  description = "Storage account for persisted Ollama model data. Must be globally unique."
  type        = string
  default     = "stsumlollamamodels"
}

variable "ollama_file_share_name" {
  description = "Azure Files share name mounted into the Ollama container."
  type        = string
  default     = "ollama-models"
}

variable "ollama_environment_storage_name" {
  description = "Container Apps environment storage name for Ollama models."
  type        = string
  default     = "ollama-models"
}

variable "ollama_file_share_quota_gb" {
  description = "Azure Files quota for Ollama models."
  type        = number
  default     = 100
}
