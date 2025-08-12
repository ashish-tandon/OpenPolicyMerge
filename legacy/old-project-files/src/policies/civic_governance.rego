package civic.governance

# Civic data governance and privacy policies

# Privacy protection rules
default allow_personal_data_access = false

# Allow access to personal data only for legitimate purposes
allow_personal_data_access {
    input.purpose == "parliamentary_proceedings"
    input.user.role in ["admin", "parliamentary_staff", "researcher"]
    input.user.has_clearance == true
}

# Explicit deny for no clearance
allow_personal_data_access = false {
    input.purpose == "parliamentary_proceedings"
    input.user.role in ["admin", "parliamentary_staff", "researcher"]
    input.user.has_clearance != true
}

allow_personal_data_access {
    input.purpose == "public_interest"
    input.user.role == "journalist"
    input.user.media_organization_verified == true
    input.data_anonymized == true
}

# Data retention policies
data_retention_compliant(data) {
    # Parliamentary data should be retained indefinitely for historical purposes
    data.type == "parliamentary_record"
    
    # Personal contact information should have limited retention
    data.type == "personal_contact"
    data.retention_period <= 730  # 2 years max
    
    # Financial data should follow government retention schedules
    data.type == "financial"
    data.retention_period <= 2555  # 7 years max
}

# Data anonymization requirements
require_anonymization(data) {
    data.type == "personal_contact"
    data.anonymized == true
}

require_anonymization(data) {
    data.type == "financial"
    data.anonymized == true
}

# Consent management
has_valid_consent(data, user) {
    data.consent_given == true
    data.consent_date
    data.consent_purpose == data.current_purpose
    data.consent_withdrawn != true
}

# Data sharing restrictions
allow_data_sharing(source, destination, data) {
    # Government to government sharing
    source.type == "government_entity"
    destination.type == "government_entity"
    data.sharing_agreement_exists == true
    
    # Research sharing
    source.type == "research_institution"
    destination.type == "research_institution"
    data.ethics_approval == true
    data.data_anonymized == true
    
    # Public interest sharing
    source.type == "public_interest"
    destination.type == "media"
    data.public_benefit_outweighs_privacy_risk == true
}

# Conflict of interest detection
detect_conflict_of_interest(user, data) {
    # User has financial interest in the data subject
    user.financial_interest_in_subject == true
    
    # User has personal relationship with data subject
    user.personal_relationship_with_subject == true
    
    # User has political affiliation that could bias data handling
    user.political_affiliation_creates_bias == true
}

# Data quality standards for civic data
civic_data_quality_standards(data) {
    # Accuracy requirements
    data.accuracy_verified == true
    data.source_documented == true
    data.last_updated_recently == true
    
    # Completeness requirements
    data.required_fields_present == true
    data.optional_fields_documented == true
    
    # Timeliness requirements
    data.age_in_days <= data.max_age_threshold
}

# Ethical AI and automation policies
ethical_ai_usage(algorithm, data) {
    # Algorithm transparency
    algorithm.explanation_available == true
    algorithm.bias_mitigation_applied == true
    
    # Human oversight
    algorithm.human_review_required == true
    algorithm.decision_threshold_appropriate == true
    
    # Fairness and non-discrimination
    algorithm.fairness_tested == true
    algorithm.discrimination_mitigation == true
}

# Public participation and transparency
public_participation_allowed(process) {
    process.type == "policy_development"
    process.public_comment_period_active == true
    process.stakeholder_consultation_completed == true
}

# Data sovereignty and jurisdictional compliance
jurisdiction_compliant(data, location) {
    # Canadian data residency
    data.stored_in_canada == true
    
    # Provincial jurisdiction compliance
    data.province == location.province
    data.municipal_jurisdiction == location.municipality
    
    # Federal jurisdiction compliance
    data.federal_jurisdiction == true
}

# Emergency data access protocols
emergency_data_access_allowed(situation) {
    situation.type == "public_emergency"
    situation.severity_level >= 7
    situation.authorized_by == "emergency_coordinator"
    situation.documentation_required == true
}

# Audit and compliance requirements
audit_compliance_met(operation) {
    operation.audit_logged == true
    operation.compliance_verified == true
    operation.oversight_committee_approved == true
}
