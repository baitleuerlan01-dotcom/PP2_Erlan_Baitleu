-- ============================================================
-- PhoneBook Stored Procedures & Functions
-- TSIS 1: New procedures (do NOT duplicate Practice 8 objects)
-- ============================================================

-- -------------------------------------------------------
-- 1. Procedure: add_phone
--    Adds a new phone number to an existing contact.
-- -------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    -- Find the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Check for duplicate phone
    IF EXISTS (
        SELECT 1 FROM phones
        WHERE contact_id = v_contact_id AND phone = p_phone
    ) THEN
        RAISE NOTICE 'Phone "%" already exists for contact "%".', p_phone, p_contact_name;
        RETURN;
    END IF;

    -- Insert the phone
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone "%" (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- -------------------------------------------------------
-- 2. Procedure: move_to_group
--    Moves a contact to a different group.
--    Creates the group if it does not exist.
-- -------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Find or create the group
    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name)
        VALUES (p_group_name)
        RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;

    -- Find the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Move the contact
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- -------------------------------------------------------
-- 3. Function: search_contacts
--    Extended search: matches username, first_name, last_name,
--    email, AND all phone numbers from the phones table.
--    Returns a table of matching contacts with their phones.
-- -------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id  INTEGER,
    username    VARCHAR,
    first_name  VARCHAR,
    last_name   VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    phones_list TEXT,
    created_at  TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.username,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name   AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ')
            OVER (PARTITION BY c.id) AS phones_list,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.username   ILIKE '%' || p_query || '%'
        OR c.first_name ILIKE '%' || p_query || '%'
        OR c.last_name  ILIKE '%' || p_query || '%'
        OR c.email      ILIKE '%' || p_query || '%'
        OR p.phone      ILIKE '%' || p_query || '%'
    ORDER BY c.username;
END;
$$;


-- -------------------------------------------------------
-- 4. Function: get_contacts_page  (uses LIMIT/OFFSET)
--    Paginated list with optional group filter & sort.
--    Already have paginate_contacts from Practice 8;
--    this one adds group_filter and sort_by parameters.
-- -------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit       INTEGER DEFAULT 10,
    p_offset      INTEGER DEFAULT 0,
    p_group_name  VARCHAR DEFAULT NULL,
    p_sort_by     VARCHAR DEFAULT 'username'   -- 'username' | 'birthday' | 'created_at'
)
RETURNS TABLE (
    contact_id  INTEGER,
    username    VARCHAR,
    first_name  VARCHAR,
    last_name   VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    phones_list TEXT,
    created_at  TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Validate sort column to prevent SQL injection
    IF p_sort_by NOT IN ('username', 'birthday', 'created_at') THEN
        RAISE EXCEPTION 'Invalid sort column "%". Use username, birthday, or created_at.', p_sort_by;
    END IF;

    RETURN QUERY EXECUTE format(
        'SELECT DISTINCT
             c.id,
             c.username,
             c.first_name,
             c.last_name,
             c.email,
             c.birthday,
             g.name,
             STRING_AGG(p.phone || '' ('' || COALESCE(p.type, ''?'') || '')'', '', '')
                 OVER (PARTITION BY c.id),
             c.created_at
         FROM contacts c
         LEFT JOIN groups  g ON g.id = c.group_id
         LEFT JOIN phones  p ON p.contact_id = c.id
         WHERE ($1 IS NULL OR g.name = $1)
         ORDER BY c.%I
         LIMIT $2 OFFSET $3',
        p_sort_by
    ) USING p_group_name, p_limit, p_offset;
END;
$$;