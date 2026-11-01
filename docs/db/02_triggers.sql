-- Pharmacy DB: triggers for stock control and bill totals.
-- Safe to re-run (functions use CREATE OR REPLACE, triggers are dropped first).
BEGIN;

ALTER TABLE sale ALTER COLUMN total_amt SET DEFAULT 0;

-- ---------------------------------------------------------------
-- 1. Stock control on sale_details (INSERT / UPDATE / DELETE)
--    - checks batch belongs to the medicine and is not expired
--    - blocks overselling
--    - reduces stock on sale, restores it on delete or edit
--    - fills sale_price from medicine.mrp if left empty
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_sale_details_stock() RETURNS trigger AS $$
DECLARE
    v_med int;
    v_exp date;
BEGIN
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        UPDATE medicine_batch
           SET qty_in_stock = qty_in_stock + OLD.qty_sold
         WHERE batch_no = OLD.batch_no;
    END IF;

    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        SELECT med_no, exp_date INTO v_med, v_exp
          FROM medicine_batch
         WHERE batch_no = NEW.batch_no
           FOR UPDATE;                       -- lock row against concurrent sales

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Batch % does not exist', NEW.batch_no;
        END IF;
        IF v_med <> NEW.med_no THEN
            RAISE EXCEPTION 'Batch % does not belong to medicine %', NEW.batch_no, NEW.med_no;
        END IF;
        IF v_exp IS NOT NULL AND v_exp < CURRENT_DATE THEN
            RAISE EXCEPTION 'Batch % expired on %', NEW.batch_no, v_exp;
        END IF;

        UPDATE medicine_batch
           SET qty_in_stock = qty_in_stock - NEW.qty_sold
         WHERE batch_no = NEW.batch_no
           AND qty_in_stock >= NEW.qty_sold;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Insufficient stock in batch %', NEW.batch_no;
        END IF;

        IF NEW.sale_price IS NULL THEN
            SELECT mrp INTO NEW.sale_price FROM medicine WHERE med_no = NEW.med_no;
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sale_details_stock ON sale_details;
CREATE TRIGGER trg_sale_details_stock
BEFORE INSERT OR UPDATE OR DELETE ON sale_details
FOR EACH ROW EXECUTE FUNCTION fn_sale_details_stock();

-- ---------------------------------------------------------------
-- 2. Keep sale.total_amt = SUM(qty_sold * sale_price)
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_sale_recalc_total(p_bill int) RETURNS void AS $$
    UPDATE sale
       SET total_amt = COALESCE((SELECT SUM(qty_sold * sale_price)
                                   FROM sale_details
                                  WHERE bill_no = p_bill), 0)
     WHERE bill_no = p_bill;
$$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION fn_sale_details_total() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        PERFORM fn_sale_recalc_total(NEW.bill_no);
    END IF;
    IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.bill_no <> NEW.bill_no) THEN
        PERFORM fn_sale_recalc_total(OLD.bill_no);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sale_details_total ON sale_details;
CREATE TRIGGER trg_sale_details_total
AFTER INSERT OR UPDATE OR DELETE ON sale_details
FOR EACH ROW EXECUTE FUNCTION fn_sale_details_total();

COMMIT;
