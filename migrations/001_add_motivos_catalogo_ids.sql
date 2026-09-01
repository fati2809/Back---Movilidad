ALTER TABLE IF EXISTS boleta_infraccion
    ADD COLUMN IF NOT EXISTS motivos_catalogo_ids TEXT;

-- opcional: si quieres conservar el primer motivo en el campo antiguo
-- UPDATE boleta_infraccion
-- SET motivo_catalogo_id = NULL
-- WHERE motivo_catalogo_id IS NULL;
