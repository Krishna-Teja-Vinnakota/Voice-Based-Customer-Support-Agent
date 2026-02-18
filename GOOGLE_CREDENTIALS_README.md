# Google Credentials Configuration
# This file is used for Google Text-to-Speech services authentication
# 
# Instructions:
# 1. Go to Google Cloud Console (https://console.cloud.google.com)
# 2. Create a new service account or use an existing one
# 3. Generate a new key (JSON format)
# 4. Download the JSON file and rename it to google-credentials.json
# 5. Place this file in the project root directory
# 
# Required fields:
# - type: Always "service_account"
# - project_id: Your Google Cloud project ID
# - private_key_id: The private key ID from your service account
# - private_key: The private key (multiline, starts with -----BEGIN PRIVATE KEY-----)
# - client_email: The service account email
# - client_id: The client ID
# - auth_uri: OAuth2 authorization endpoint
# - token_uri: OAuth2 token endpoint
# - auth_provider_x509_cert_url: Google's certificate endpoint
# - client_x509_cert_url: Service account certificate URL
#
# Note: Never commit this file to version control. Use .env or environment variables instead.
