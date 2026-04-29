-- Уникальность имени контакта (чтобы импорт работал корректно)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'contacts_name_key'
    ) THEN
        ALTER TABLE contacts ADD CONSTRAINT contacts_name_key UNIQUE (name);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'phones_contact_phone_key'
    ) THEN
        ALTER TABLE phones ADD CONSTRAINT phones_contact_phone_key UNIQUE (contact_id, phone);
    END IF;
END $$;