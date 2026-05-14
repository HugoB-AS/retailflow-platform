-- RetailFlow - Useful analytical and governance views

CREATE OR REPLACE VIEW analytics.v_customer_summary AS
SELECT
    c.customer_id,
    c.country,
    c.city,
    c.loyalty_status,
    c.account_status,
    c.marketing_consent,
    c.analytics_consent,
    c.personalization_consent,
    COUNT(o.order_id) AS orders_count,
    COALESCE(SUM(o.total_incl_tax), 0) AS total_spent,
    MAX(o.order_datetime) AS last_order_datetime,
    c.last_interaction_at
FROM core.customers c
LEFT JOIN core.orders o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.country,
    c.city,
    c.loyalty_status,
    c.account_status,
    c.marketing_consent,
    c.analytics_consent,
    c.personalization_consent,
    c.last_interaction_at;

CREATE OR REPLACE VIEW analytics.v_customer_intelligence AS
SELECT
    cf.customer_id,
    cf.total_orders,
    cf.total_spent,
    cf.avg_order_value,
    cf.days_since_last_order,
    cf.return_rate,
    cf.cart_abandon_rate,
    cf.preferred_category,
    cs.segment_label,
    MAX(CASE WHEN mp.model_name = 'churn_model' THEN mp.prediction_value END) AS churn_probability,
    MAX(CASE WHEN mp.model_name = 'churn_model' THEN mp.prediction_label END) AS churn_risk,
    MAX(CASE WHEN mp.model_name = 'clv_model' THEN mp.prediction_value END) AS predicted_clv
FROM analytics.customer_features cf
LEFT JOIN analytics.customer_segments cs ON cf.customer_id = cs.customer_id
LEFT JOIN analytics.ml_predictions mp ON cf.customer_id = mp.customer_id
GROUP BY
    cf.customer_id,
    cf.total_orders,
    cf.total_spent,
    cf.avg_order_value,
    cf.days_since_last_order,
    cf.return_rate,
    cf.cart_abandon_rate,
    cf.preferred_category,
    cs.segment_label;

CREATE OR REPLACE VIEW governance.v_data_quality_summary AS
SELECT
    rule_id,
    rule_name,
    table_name,
    severity,
    status,
    COUNT(*) AS checks_count,
    MAX(checked_at) AS last_checked_at
FROM governance.data_quality_logs
GROUP BY rule_id, rule_name, table_name, severity, status;

CREATE OR REPLACE VIEW governance.v_dead_letter_summary AS
SELECT
    event_type,
    severity,
    error_reason,
    COUNT(*) AS events_count,
    MAX(created_at) AS last_seen_at
FROM governance.dead_letter_events
GROUP BY event_type, severity, error_reason;

CREATE OR REPLACE VIEW analytics.v_daily_kpis AS
SELECT
    sales_date,
    orders_count,
    revenue_incl_tax,
    avg_order_value,
    returns_count,
    refund_amount
FROM analytics.daily_sales;
