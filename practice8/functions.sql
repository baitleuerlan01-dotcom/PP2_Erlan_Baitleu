 -- Ensure the phonebook table exists (idempotent)
CREATE TABLE IF NOT EXISTS phonebook (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    phone   VARCHAR(20)  NOT NULL
);
 
-- -------------------------------------------------------------
-- 1. Pattern-search function
--    Returns all rows where name OR phone contains the pattern.
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM   phonebook pb
        WHERE  pb.name  ILIKE '%' || p_pattern || '%'
            OR pb.phone ILIKE '%' || p_pattern || '%'
        ORDER BY pb.name;
END;
$$ LANGUAGE plpgsql;
 
 
-- -------------------------------------------------------------
-- 2. Paginated query function
--    Returns contacts in chunks defined by page size and number.
--    page_number is 1-based.
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_page_size   INT DEFAULT 10,
    p_page_number INT DEFAULT 1
)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
DECLARE
    v_offset INT;
BEGIN
    -- Basic validation
    IF p_page_size   < 1 THEN p_page_size   := 10; END IF;
    IF p_page_number < 1 THEN p_page_number := 1;  END IF;
 
    v_offset := (p_page_number - 1) * p_page_size;
 
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM   phonebook pb
        ORDER BY pb.name
        LIMIT  p_page_size
        OFFSET v_offset;
END;
$$ LANGUAGE plpgsql;
