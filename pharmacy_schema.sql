--
-- PostgreSQL database dump
--

\restrict GK5oqgRU3xYJLDJZX6Is7rSUbArAsiqhXUcgWuzUobBicb6Cw4mXFaaTvBMDL4Z

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-10-12 21:56:06

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 16408)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    cust_name character varying(50) NOT NULL,
    age integer,
    phone_no character varying(15),
    address character varying(50),
    cust_no integer NOT NULL
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16423)
-- Name: employee; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee (
    emp_no integer NOT NULL,
    emp_name character varying(50),
    emp_role character varying(50),
    salary double precision,
    phone_no character varying(15)
);


ALTER TABLE public.employee OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16393)
-- Name: medicine; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicine (
    med_no integer NOT NULL,
    med_name character varying(50),
    category character(50),
    manufacturer character varying(50),
    unit character varying(50),
    mrp double precision
);


ALTER TABLE public.medicine OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16396)
-- Name: medicine_batch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicine_batch (
    batch_no integer NOT NULL,
    med_no integer,
    mfg_date date,
    exp_date date,
    qty_in_stock integer,
    pur_price double precision
);


ALTER TABLE public.medicine_batch OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16411)
-- Name: prescription; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prescription (
    pres_no integer NOT NULL,
    cust_no integer,
    doc_name character varying(50),
    pres_date date,
    diagnosis character varying(50)
);


ALTER TABLE public.prescription OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16414)
-- Name: prescription_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prescription_details (
    pres_no integer NOT NULL,
    med_no integer NOT NULL,
    dosage character varying(50),
    duration character varying(50)
);


ALTER TABLE public.prescription_details OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16402)
-- Name: purchase_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchase_order (
    pur_no integer NOT NULL,
    sup_no integer,
    order_date date,
    status character(50)
);


ALTER TABLE public.purchase_order OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16405)
-- Name: purchase_order_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchase_order_details (
    pur_no integer NOT NULL,
    med_no integer NOT NULL,
    qty_ordered integer,
    rate double precision
);


ALTER TABLE public.purchase_order_details OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16417)
-- Name: sale; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale (
    bill_no integer NOT NULL,
    cust_no integer,
    emp_no integer,
    sale_date date,
    total_amt double precision,
    payment_mode character varying(50)
);


ALTER TABLE public.sale OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16420)
-- Name: sale_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_details (
    bill_no integer NOT NULL,
    med_no integer,
    batch_no integer NOT NULL,
    qty_sold double precision,
    sale_price double precision
);


ALTER TABLE public.sale_details OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16399)
-- Name: supplier; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.supplier (
    sup_no integer NOT NULL,
    sup_name character varying(50),
    address character varying(50),
    gst_no character varying(50)
);


ALTER TABLE public.supplier OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 24684)
-- Name: supplier_phone; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.supplier_phone (
    sup_no integer NOT NULL,
    phone_no character varying(15) NOT NULL
);


ALTER TABLE public.supplier_phone OWNER TO postgres;

--
-- TOC entry 4910 (class 2606 OID 24611)
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (cust_no);


--
-- TOC entry 4920 (class 2606 OID 24590)
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (emp_no);


--
-- TOC entry 4902 (class 2606 OID 24596)
-- Name: medicine_batch medicine_batch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicine_batch
    ADD CONSTRAINT medicine_batch_pkey PRIMARY KEY (batch_no);


--
-- TOC entry 4900 (class 2606 OID 24593)
-- Name: medicine medicine_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicine
    ADD CONSTRAINT medicine_pkey PRIMARY KEY (med_no);


--
-- TOC entry 4914 (class 2606 OID 24703)
-- Name: prescription_details prescription_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_details
    ADD CONSTRAINT prescription_details_pkey PRIMARY KEY (pres_no, med_no);


--
-- TOC entry 4912 (class 2606 OID 24599)
-- Name: prescription prescription_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT prescription_pkey PRIMARY KEY (pres_no);


--
-- TOC entry 4908 (class 2606 OID 24699)
-- Name: purchase_order_details purchase_order_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_order_details
    ADD CONSTRAINT purchase_order_details_pkey PRIMARY KEY (pur_no, med_no);


--
-- TOC entry 4906 (class 2606 OID 24602)
-- Name: purchase_order purchase_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_order
    ADD CONSTRAINT purchase_order_pkey PRIMARY KEY (pur_no);


--
-- TOC entry 4918 (class 2606 OID 24707)
-- Name: sale_details sale_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT sale_details_pkey PRIMARY KEY (bill_no, batch_no);


--
-- TOC entry 4916 (class 2606 OID 24605)
-- Name: sale sale_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_pkey PRIMARY KEY (bill_no);


--
-- TOC entry 4922 (class 2606 OID 24690)
-- Name: supplier_phone supplier_phone_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_phone
    ADD CONSTRAINT supplier_phone_pkey PRIMARY KEY (sup_no, phone_no);


--
-- TOC entry 4904 (class 2606 OID 24608)
-- Name: supplier supplier_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier
    ADD CONSTRAINT supplier_pkey PRIMARY KEY (sup_no);


--
-- TOC entry 4923 (class 2606 OID 24612)
-- Name: medicine_batch fk_batch_medicine; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicine_batch
    ADD CONSTRAINT fk_batch_medicine FOREIGN KEY (med_no) REFERENCES public.medicine(med_no);


--
-- TOC entry 4924 (class 2606 OID 24617)
-- Name: purchase_order fk_po_supplier; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_order
    ADD CONSTRAINT fk_po_supplier FOREIGN KEY (sup_no) REFERENCES public.supplier(sup_no);


--
-- TOC entry 4925 (class 2606 OID 24627)
-- Name: purchase_order_details fk_pod_medicine; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_order_details
    ADD CONSTRAINT fk_pod_medicine FOREIGN KEY (med_no) REFERENCES public.medicine(med_no);


--
-- TOC entry 4926 (class 2606 OID 24622)
-- Name: purchase_order_details fk_pod_po; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_order_details
    ADD CONSTRAINT fk_pod_po FOREIGN KEY (pur_no) REFERENCES public.purchase_order(pur_no);


--
-- TOC entry 4927 (class 2606 OID 24632)
-- Name: prescription fk_prescription_customer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_customer FOREIGN KEY (cust_no) REFERENCES public.customers(cust_no);


--
-- TOC entry 4928 (class 2606 OID 24642)
-- Name: prescription_details fk_presd_medicine; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_details
    ADD CONSTRAINT fk_presd_medicine FOREIGN KEY (med_no) REFERENCES public.medicine(med_no);


--
-- TOC entry 4929 (class 2606 OID 24637)
-- Name: prescription_details fk_presd_prescription; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_details
    ADD CONSTRAINT fk_presd_prescription FOREIGN KEY (pres_no) REFERENCES public.prescription(pres_no);


--
-- TOC entry 4930 (class 2606 OID 24647)
-- Name: sale fk_sale_customer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT fk_sale_customer FOREIGN KEY (cust_no) REFERENCES public.customers(cust_no);


--
-- TOC entry 4931 (class 2606 OID 24652)
-- Name: sale fk_sale_employee; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT fk_sale_employee FOREIGN KEY (emp_no) REFERENCES public.employee(emp_no);


--
-- TOC entry 4932 (class 2606 OID 24667)
-- Name: sale_details fk_saled_batch; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT fk_saled_batch FOREIGN KEY (batch_no) REFERENCES public.medicine_batch(batch_no);


--
-- TOC entry 4933 (class 2606 OID 24662)
-- Name: sale_details fk_saled_medicine; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT fk_saled_medicine FOREIGN KEY (med_no) REFERENCES public.medicine(med_no);


--
-- TOC entry 4934 (class 2606 OID 24657)
-- Name: sale_details fk_saled_sale; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT fk_saled_sale FOREIGN KEY (bill_no) REFERENCES public.sale(bill_no);


--
-- TOC entry 4935 (class 2606 OID 24691)
-- Name: supplier_phone fk_supphone_supplier; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.supplier_phone
    ADD CONSTRAINT fk_supphone_supplier FOREIGN KEY (sup_no) REFERENCES public.supplier(sup_no);


-- Completed on 2026-10-12 21:56:07

--
-- PostgreSQL database dump complete
--

\unrestrict GK5oqgRU3xYJLDJZX6Is7rSUbArAsiqhXUcgWuzUobBicb6Cw4mXFaaTvBMDL4Z

