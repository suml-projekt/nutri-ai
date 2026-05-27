output "acr_login_server" {
  description = "ACR login server used by the GitHub Actions workflow."
  value       = azurerm_container_registry.main.login_server
}

output "ollama_internal_fqdn" {
  description = "Internal Ollama FQDN inside the Container Apps environment."
  value       = azurerm_container_app.ollama.latest_revision_fqdn
}

output "streamlit_url" {
  description = "Public Streamlit app URL. Null until deploy_streamlit_app is true."
  value       = var.deploy_streamlit_app ? "https://${azurerm_container_app.streamlit[0].latest_revision_fqdn}" : null
}
