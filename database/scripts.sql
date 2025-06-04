
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_authorized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description VARCHAR(255),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'reversed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT positive_amount CHECK (amount > 0)
);


CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);


CREATE OR REPLACE PROCEDURE register_user(
    p_username VARCHAR(50),
    p_email VARCHAR(100),
    p_password VARCHAR(255),
    p_full_name VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, email, hashed_password, full_name)
    VALUES (p_username, p_email, p_password, p_full_name);
END;
$$;


CREATE OR REPLACE PROCEDURE start_transaction(
    p_user_id INTEGER,
    p_amount DECIMAL(10, 2),
    p_currency VARCHAR(3),
    p_description VARCHAR(255),
    INOUT p_transaction_id INTEGER,
    INOUT p_status VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_is_authorized BOOLEAN;
BEGIN
    -- Verificar si el usuario está autorizado
    SELECT is_authorized INTO v_is_authorized FROM users WHERE user_id = p_user_id;
    
    IF NOT v_is_authorized THEN
        p_status := 'failed';
        RAISE EXCEPTION 'User is not authorized to perform transactions';
    END IF;
    
    -- Insertar la transacción
    INSERT INTO transactions (user_id, amount, currency, description, status)
    VALUES (p_user_id, p_amount, p_currency, p_description, 'pending')
    RETURNING transaction_id INTO p_transaction_id;
    
    p_status := 'pending';
END;
$$;

-- Función para obtener el historial de transacciones de un usuario
CREATE OR REPLACE FUNCTION get_user_transactions(
    p_user_id INTEGER,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    transaction_id INTEGER,
    amount DECIMAL(10, 2),
    currency VARCHAR(3),
    description VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.transaction_id,
        t.amount,
        t.currency,
        t.description,
        t.status,
        t.created_at,
        t.completed_at
    FROM transactions t
    WHERE t.user_id = p_user_id
    ORDER BY t.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;