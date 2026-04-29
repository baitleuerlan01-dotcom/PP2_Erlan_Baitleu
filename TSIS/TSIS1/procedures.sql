-- =============================================
-- Функция и процедуры для PhoneBook (TSIS 1)
-- =============================================

-- Поиск по имени / email / телефону (используется в меню 2)
CREATE OR REPLACE FUNCTION search_contacts(search_term TEXT)
RETURNS TABLE (
    contact_id   INTEGER,
    name         VARCHAR(100),
    email        VARCHAR(100),
    birthday     DATE,
    group_name   VARCHAR(50),
    phone        VARCHAR(20),
    phone_type   VARCHAR(10)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS contact_id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        p.phone,
        p.type AS phone_type
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE LOWER(c.name) LIKE LOWER('%' || search_term || '%')
       OR (c.email IS NOT NULL AND LOWER(c.email) LIKE LOWER('%' || search_term || '%'))
       OR (p.phone IS NOT NULL AND LOWER(p.phone) LIKE LOWER('%' || search_term || '%'))
    ORDER BY c.name, c.id, p.id;
END;
$$ LANGUAGE plpgsql;

-- Процедура добавления телефона (меню 6)
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR(100), p_phone VARCHAR(20), p_type VARCHAR(10))
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE LOWER(name) = LOWER(p_contact_name);

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Контакт "%" не найден!', p_contact_name;
        RETURN;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        p_type := 'mobile';
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type)
    ON CONFLICT DO NOTHING;
END;
$$;

-- Процедура перемещения контакта в группу (меню 7)
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR(100), p_group_name VARCHAR(50))
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE LOWER(name) = LOWER(p_contact_name);

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Контакт "%" не найден!', p_contact_name;
        RETURN;
    END IF;

    -- Создаём группу, если её нет
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id 
    FROM groups 
    WHERE LOWER(name) = LOWER(p_group_name);

    UPDATE contacts 
    SET group_id = v_group_id 
    WHERE id = v_contact_id;
END;
$$;