package parliamentary.access

# Default deny - secure by default
default allow = false

# Explicit deny rules - these take precedence over allow rules
deny {
    input.resource.type == "personal_contact_info"
    input.user.role != "admin"
}

deny {
    input.resource.type == "internal_communications"
    input.user.role not in ["admin", "parliamentary_staff"]
}

deny {
    input.action == "api_call"
    input.user.rate_limit_exceeded == true
}

# Allow public read access to basic parliamentary information
allow {
    input.action == "read"
    input.resource.type == "public_parliamentary_data"
    input.resource.category in ["bills", "votes", "sessions", "parties"]
}

# Allow authenticated users to access detailed politician information
allow {
    input.action == "read"
    input.resource.type == "politician_details"
    input.user.authenticated == true
    input.user.role in ["citizen", "researcher", "journalist", "admin"]
}

# Allow researchers and journalists to access hansard (debate) data
allow {
    input.action == "read"
    input.resource.type == "hansard"
    input.user.authenticated == true
    input.user.role in ["researcher", "journalist", "admin"]
}

# Allow admin users full access to all parliamentary data
allow {
    input.user.role == "admin"
}

# Allow elected officials to access their own data and constituency information
allow {
    input.action == "read"
    input.user.role == "elected_official"
    input.resource.type == "constituency_data"
    input.resource.riding_id == input.user.constituency_id
}

# Allow party officials to access their party's data
allow {
    input.action == "read"
    input.user.role == "party_official"
    input.resource.type == "party_data"
    input.resource.party_id == input.user.party_id
}

# Audit logging for all access attempts
audit_log {
    input.action
    input.user.id
    input.resource.type
    input.resource.id
    input.timestamp
}
