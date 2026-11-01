-- Tests the triggers with temporary data. Everything is rolled back at the end.
BEGIN;

DO $$
DECLARE
    m int; b int; s1 int; s2 int;
    st int; tot double precision; blocked boolean;
BEGIN
    INSERT INTO medicine(med_name, mrp) VALUES ('TEST MED', 10) RETURNING med_no INTO m;
    INSERT INTO medicine_batch(med_no, mfg_date, exp_date, qty_in_stock, pur_price)
    VALUES (m, CURRENT_DATE - 30, CURRENT_DATE + 365, 10, 5) RETURNING batch_no INTO b;
    INSERT INTO sale(sale_date, payment_mode) VALUES (CURRENT_DATE, 'Cash') RETURNING bill_no INTO s1;
    INSERT INTO sale(sale_date, payment_mode) VALUES (CURRENT_DATE, 'Cash') RETURNING bill_no INTO s2;

    -- Test 1: selling 3 reduces stock to 7 and total becomes 30 (price defaults to MRP)
    INSERT INTO sale_details(bill_no, med_no, batch_no, qty_sold) VALUES (s1, m, b, 3);
    SELECT qty_in_stock INTO st FROM medicine_batch WHERE batch_no = b;
    ASSERT st = 7, 'Test 1 failed: stock should be 7, got ' || st;
    SELECT total_amt INTO tot FROM sale WHERE bill_no = s1;
    ASSERT tot = 30, 'Test 1 failed: total should be 30, got ' || tot;

    -- Test 2: overselling (8 > 7 left) must be blocked
    blocked := false;
    BEGIN
        INSERT INTO sale_details(bill_no, med_no, batch_no, qty_sold) VALUES (s2, m, b, 8);
    EXCEPTION WHEN OTHERS THEN
        blocked := true;
    END;
    ASSERT blocked, 'Test 2 failed: overselling was allowed';

    -- Test 3: editing quantity 3 -> 5 adjusts stock to 5 and total to 50
    UPDATE sale_details SET qty_sold = 5 WHERE bill_no = s1 AND batch_no = b;
    SELECT qty_in_stock INTO st FROM medicine_batch WHERE batch_no = b;
    SELECT total_amt INTO tot FROM sale WHERE bill_no = s1;
    ASSERT st = 5 AND tot = 50, 'Test 3 failed: stock ' || st || ', total ' || tot;

    -- Test 4: deleting the line restores stock to 10 and total to 0
    DELETE FROM sale_details WHERE bill_no = s1 AND batch_no = b;
    SELECT qty_in_stock INTO st FROM medicine_batch WHERE batch_no = b;
    SELECT total_amt INTO tot FROM sale WHERE bill_no = s1;
    ASSERT st = 10 AND tot = 0, 'Test 4 failed: stock ' || st || ', total ' || tot;

    -- Test 5: expired batch must be blocked
    UPDATE medicine_batch SET mfg_date = CURRENT_DATE - 400, exp_date = CURRENT_DATE - 1
     WHERE batch_no = b;
    blocked := false;
    BEGIN
        INSERT INTO sale_details(bill_no, med_no, batch_no, qty_sold) VALUES (s1, m, b, 1);
    EXCEPTION WHEN OTHERS THEN
        blocked := true;
    END;
    ASSERT blocked, 'Test 5 failed: expired batch was sold';

    RAISE NOTICE 'ALL 5 TESTS PASSED';
END $$;

ROLLBACK;
