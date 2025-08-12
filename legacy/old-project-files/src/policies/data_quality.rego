package data.quality

# Data validation rules for parliamentary entities

# Validate politician data
validate_politician(data) {
    # Required fields
    data.name
    data.name_given
    data.name_family
    
    # Name validation
    len(data.name) > 0
    len(data.name) <= 100
    len(data.name_given) <= 50
    len(data.name_family) <= 50
    
    # Gender validation
    data.gender in ["M", "F", ""]
    
    # Slug validation if present
    not data.slug or (len(data.slug) > 0 and len(data.slug) <= 30)
}

# Explicit validation failure for missing required fields
validate_politician(data) = false {
    not data.name
}

validate_politician(data) = false {
    not data.name_given
}

validate_politician(data) = false {
    not data.name_family
}

# Alternative approach: use a separate validation function
is_politician_valid(data) {
    data.name
    data.name_given
    data.name_family
    len(data.name) > 0
    len(data.name) <= 100
    len(data.name_given) <= 50
    len(data.name_family) <= 50
    data.gender in ["M", "F", ""]
}

# Validate party data
validate_party(data) {
    # Required fields
    data.name_en
    data.name_fr
    
    # Name validation
    len(data.name_en) > 0
    len(data.name_en) <= 100
    len(data.name_fr) <= 100
    
    # Short name validation
    not data.short_name_en or len(data.short_name_en) <= 100
    not data.short_name_fr or len(data.short_name_fr) <= 100
    
    # Slug validation
    not data.slug or (len(data.slug) > 0 and len(data.slug) <= 10)
}

# Validate riding data
validate_riding(data) {
    # Required fields
    data.name_en
    data.province
    
    # Name validation
    len(data.name_en) > 0
    len(data.name_en) <= 200
    len(data.name_fr) <= 200
    
    # Province validation (Canadian provinces and territories)
    data.province in ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]
    
    # Slug validation
    not data.slug or (len(data.slug) > 0 and len(data.slug) <= 60)
    
    # EDID validation if present
    not data.edid or data.edid > 0
}

# Validate session data
validate_session(data) {
    # Required fields
    data.id
    data.name
    data.start
    
    # ID validation (format: XX-X where XX is parliament number, X is session number)
    regex.match("^[0-9]{2}-[0-9]$", data.id)
    
    # Name validation
    len(data.name) > 0
    len(data.name) <= 100
    
    # Date validation
    data.start
    not data.end or data.end > data.start
    
    # Parliament and session number validation
    not data.parliamentnum or (data.parliamentnum > 0 and data.parliamentnum <= 50)
    not data.sessnum or (data.sessnum > 0 and data.sessnum <= 10)
}

# Validate elected member data
validate_elected_member(data) {
    # Required fields
    data.politician_id
    data.riding_id
    data.party_id
    data.start_date
    
    # Date validation
    data.start_date
    not data.end_date or data.end_date > data.start_date
    
    # Relationship validation
    data.politician_id > 0
    data.riding_id > 0
    data.party_id > 0
}

# Validate bill data
validate_bill(data) {
    # Required fields
    data.number
    data.session_id
    data.institution
    
    # Number validation
    len(data.number) > 0
    len(data.number) <= 10
    regex.match("^[CS]-[0-9]+$", data.number)
    
    # Institution validation
    data.institution in ["C", "S"]
    
    # Status validation if present
    not data.status_code or data.status_code in [
        "BillNotActive", "WillNotBeProceededWith", "RoyalAssentAwaiting",
        "BillDefeated", "HouseAtReportStage", "SenateAtReportStage",
        "RoyalAssentGiven", "SenateAt1stReading", "HouseAt1stReading",
        "HouseAtReferralToCommitteeBeforeSecondReading", "HouseAt2ndReading",
        "HouseAtReportStageAndSecondReading", "SenateAt2ndReading",
        "SenateAt3rdReading", "HouseAt3rdReading", "HouseInCommittee",
        "SenateInCommittee", "SenateConsiderationOfCommitteeReport",
        "HouseConsiderationOfCommitteeReport", "SenateConsiderationOfAmendments",
        "HouseConsiderationOfAmendments", "Introduced", "ProForma",
        "SenateBillWaitingHouse", "HouseBillWaitingSenate",
        "OutsideOrderPrecedence", "SenConsideringHouseAmendments",
        "HouseConsideringSenAmendments"
    ]
}

# Data consistency checks
check_data_consistency(data) {
    # Check for duplicate politicians with same name
    not has_duplicate_politicians(data)
    
    # Check for duplicate ridings in same province
    not has_duplicate_ridings(data)
    
    # Check for valid foreign key relationships
    all_foreign_keys_valid(data)
}

# Helper functions
has_duplicate_politicians(data) {
    count(data.politicians) != count(unique(data.politicians, "name"))
}

has_duplicate_ridings(data) {
    count(data.ridings) != count(unique(data.ridings, ["name_en", "province"]))
}

all_foreign_keys_valid(data) {
    # This would be implemented with actual database queries
    # For now, we assume they are valid
    true
}
