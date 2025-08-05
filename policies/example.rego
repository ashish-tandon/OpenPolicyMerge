package example

# Default deny
default allow = false

# Allow access if user has admin role
allow {
    input.user.role == "admin"
}

# Allow access if user has read permission and is accessing read-only resources
allow {
    input.user.permissions[_] == "read"
    input.action == "read"
}

# Allow access if user is accessing their own resources
allow {
    input.user.id == input.resource.owner
}

# Deny access if user is blocked
allow = false {
    input.user.status == "blocked"
} 