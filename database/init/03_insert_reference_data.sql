-- RetailFlow - Reference data

INSERT INTO governance.data_retention_policies (
    policy_id,
    data_domain,
    table_name,
    data_category,
    retention_days,
    retention_trigger,
    retention_action,
    legal_basis,
    owner_role,
    description
) VALUES
('ret_001', 'customers', 'core.customers', 'personal_data', 1095, 'last_interaction_at', 'anonymize', 'GDPR - storage limitation', 'Data Protection Officer', 'Anonymize inactive customer personal data after 3 years without meaningful interaction.'),
('ret_002', 'events', 'raw.events', 'behavioral_data', 395, 'event_timestamp', 'pseudonymize', 'GDPR - analytics consent', 'Data Owner - Digital', 'Pseudonymize behavioral events after analytics retention period.'),
('ret_003', 'support', 'core.support_tickets', 'personal_text', 730, 'created_at', 'anonymize', 'Customer support legitimate interest', 'Customer Support Manager', 'Anonymize support ticket free text after retention period.'),
('ret_004', 'ml_predictions', 'analytics.ml_predictions', 'derived_data', 180, 'prediction_timestamp', 'refresh', 'Model governance policy', 'ML Owner', 'Refresh or remove outdated ML predictions.')
ON CONFLICT (policy_id) DO NOTHING;
