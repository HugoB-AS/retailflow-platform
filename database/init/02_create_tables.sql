-- RetailFlow - Core database tables
-- Database: retailflow_db

-- =========================
-- CORE SCHEMA
-- =========================

CREATE TABLE IF NOT EXISTS core.customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(50),
    birth_date DATE,
    gender VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(30),
    registration_date DATE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    analytics_consent BOOLEAN DEFAULT FALSE,
    personalization_consent BOOLEAN DEFAULT FALSE,
    loyalty_status VARCHAR(50),
    account_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction_at TIMESTAMP,
    is_anonymized BOOLEAN DEFAULT FALSE,
    anonymized_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    esg_compliant BOOLEAN DEFAULT FALSE,
    esg_score NUMERIC(5,2),
    certifications TEXT,
    supplier_risk_level VARCHAR(50),
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_role VARCHAR(100),
    support_phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    color VARCHAR(50),
    size VARCHAR(50),
    material VARCHAR(100),
    manufacturing_country VARCHAR(100),
    price_excl_tax NUMERIC(12,2) NOT NULL,
    tax_rate NUMERIC(5,2) DEFAULT 0.20,
    price_incl_tax NUMERIC(12,2) NOT NULL,
    cost NUMERIC(12,2),
    stock_quantity INTEGER DEFAULT 0,
    supplier_id VARCHAR(20) REFERENCES core.suppliers(supplier_id),
    image_code VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    order_datetime TIMESTAMP NOT NULL,
    order_hour INTEGER,
    order_status VARCHAR(50),
    sales_channel VARCHAR(50),
    items_count INTEGER DEFAULT 0,
    total_excl_tax NUMERIC(12,2),
    tax_amount NUMERIC(12,2),
    total_incl_tax NUMERIC(12,2),
    discount_amount NUMERIC(12,2) DEFAULT 0,
    coupon_code VARCHAR(100),
    payment_status VARCHAR(50),
    shipping_status VARCHAR(50),
    delivery_address TEXT,
    delivery_city VARCHAR(100),
    delivery_postal_code VARCHAR(30),
    delivery_country VARCHAR(100),
    has_return BOOLEAN DEFAULT FALSE,
    return_status VARCHAR(50),
    returned_items_count INTEGER DEFAULT 0,
    refund_total_amount NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.order_items (
    order_item_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES core.orders(order_id),
    product_id VARCHAR(20) REFERENCES core.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price_excl_tax NUMERIC(12,2),
    tax_rate NUMERIC(5,2),
    unit_price_incl_tax NUMERIC(12,2),
    discount_rate NUMERIC(5,2) DEFAULT 0,
    line_total_excl_tax NUMERIC(12,2),
    line_tax_amount NUMERIC(12,2),
    line_total_incl_tax NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS core.payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES core.orders(order_id),
    payment_method VARCHAR(50),
    payment_provider VARCHAR(100),
    card_network VARCHAR(50),
    payment_status VARCHAR(50),
    payment_amount NUMERIC(12,2),
    payment_datetime TIMESTAMP,
    transaction_reference_tokenized VARCHAR(255),
    fraud_score NUMERIC(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.shipments (
    shipment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES core.orders(order_id),
    shipment_direction VARCHAR(50),
    carrier VARCHAR(100),
    shipping_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    actual_delivery_date TIMESTAMP,
    delivery_status VARCHAR(50),
    shipping_delay_days INTEGER,
    tracking_reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.returns (
    return_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES core.orders(order_id),
    product_id VARCHAR(20) REFERENCES core.products(product_id),
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    return_date TIMESTAMP,
    return_reason VARCHAR(255),
    return_status VARCHAR(50),
    refund_amount NUMERIC(12,2),
    is_refunded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.sessions (
    session_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    device_type VARCHAR(50),
    traffic_source VARCHAR(100),
    session_duration_seconds INTEGER,
    pages_viewed INTEGER,
    converted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.support_tickets (
    ticket_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(100),
    priority VARCHAR(50),
    status VARCHAR(50),
    ticket_text TEXT,
    resolution_time_hours NUMERIC(10,2),
    satisfaction_score NUMERIC(3,2),
    contains_personal_data BOOLEAN DEFAULT FALSE,
    moderation_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS core.reviews (
    review_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    product_id VARCHAR(20) REFERENCES core.products(product_id),
    rating INTEGER,
    review_text TEXT,
    review_date TIMESTAMP,
    moderation_status VARCHAR(50),
    contains_personal_data BOOLEAN DEFAULT FALSE
);

-- =========================
-- RAW SCHEMA
-- =========================

CREATE TABLE IF NOT EXISTS raw.events (
    event_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20),
    session_id VARCHAR(30),
    event_type VARCHAR(100),
    product_id VARCHAR(20),
    event_timestamp TIMESTAMP,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    country VARCHAR(100),
    page_url TEXT,
    referrer TEXT,
    sales_channel VARCHAR(50),
    raw_payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- GOVERNANCE SCHEMA
-- =========================

CREATE TABLE IF NOT EXISTS governance.customer_consents (
    consent_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    consent_type VARCHAR(100),
    consent_value BOOLEAN,
    consent_date TIMESTAMP,
    source VARCHAR(100),
    withdrawal_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.data_retention_policies (
    policy_id VARCHAR(30) PRIMARY KEY,
    data_domain VARCHAR(100),
    table_name VARCHAR(150),
    data_category VARCHAR(100),
    retention_days INTEGER,
    retention_trigger VARCHAR(100),
    retention_action VARCHAR(100),
    legal_basis VARCHAR(255),
    owner_role VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.retention_actions_log (
    action_id VARCHAR(30) PRIMARY KEY,
    policy_id VARCHAR(30) REFERENCES governance.data_retention_policies(policy_id),
    table_name VARCHAR(150),
    record_id VARCHAR(100),
    action_type VARCHAR(100),
    action_status VARCHAR(50),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_by VARCHAR(100),
    details TEXT
);

CREATE TABLE IF NOT EXISTS governance.data_quality_logs (
    check_id VARCHAR(30) PRIMARY KEY,
    rule_id VARCHAR(20),
    rule_name VARCHAR(150),
    table_name VARCHAR(150),
    record_id VARCHAR(100),
    status VARCHAR(50),
    severity VARCHAR(50),
    action VARCHAR(50),
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS governance.dead_letter_events (
    dead_letter_id VARCHAR(30) PRIMARY KEY,
    event_id VARCHAR(30),
    source_topic VARCHAR(150),
    event_type VARCHAR(100),
    error_reason TEXT,
    raw_payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(50),
    reprocessed BOOLEAN DEFAULT FALSE,
    reprocessed_at TIMESTAMP
);

-- =========================
-- ANALYTICS SCHEMA
-- =========================

CREATE TABLE IF NOT EXISTS analytics.customer_features (
    customer_id VARCHAR(20) PRIMARY KEY REFERENCES core.customers(customer_id),
    total_orders INTEGER,
    total_spent NUMERIC(12,2),
    avg_order_value NUMERIC(12,2),
    days_since_last_order INTEGER,
    return_rate NUMERIC(6,4),
    cart_abandon_rate NUMERIC(6,4),
    session_count_30d INTEGER,
    pages_viewed_30d INTEGER,
    support_tickets_count INTEGER,
    avg_rating_given NUMERIC(3,2),
    discount_usage_rate NUMERIC(6,4),
    preferred_category VARCHAR(100),
    loyalty_status VARCHAR(50),
    feature_date DATE
);

CREATE TABLE IF NOT EXISTS analytics.ml_predictions (
    prediction_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    model_name VARCHAR(150),
    model_version VARCHAR(50),
    prediction_value NUMERIC(14,4),
    prediction_label VARCHAR(100),
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_features_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.customer_segments (
    customer_id VARCHAR(20) REFERENCES core.customers(customer_id),
    segment_id INTEGER,
    segment_label VARCHAR(100),
    segment_description TEXT,
    model_version VARCHAR(50),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id, model_version)
);

CREATE TABLE IF NOT EXISTS analytics.daily_sales (
    sales_date DATE PRIMARY KEY,
    orders_count INTEGER,
    revenue_excl_tax NUMERIC(14,2),
    tax_amount NUMERIC(14,2),
    revenue_incl_tax NUMERIC(14,2),
    avg_order_value NUMERIC(12,2),
    returns_count INTEGER,
    refund_amount NUMERIC(14,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- INDEXES
-- =========================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON core.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_datetime ON core.orders(order_datetime);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON core.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON core.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_events_customer_id ON raw.events(customer_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON raw.events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON raw.events(event_type);
CREATE INDEX IF NOT EXISTS idx_quality_rule ON governance.data_quality_logs(rule_id);
CREATE INDEX IF NOT EXISTS idx_dead_letter_event_type ON governance.dead_letter_events(event_type);
CREATE INDEX IF NOT EXISTS idx_predictions_customer ON analytics.ml_predictions(customer_id);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON analytics.ml_predictions(model_name);
