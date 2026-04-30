--
-- PostgreSQL database dump
--

\restrict tmcPGV8oC0y6lzTjjc3EgS8JaReeP23cMhHOSM90rtUlFmNubITPKqQt3wDViJ5

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 18.3

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

--
-- Name: squema1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA squema1;


ALTER SCHEMA squema1 OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: grupo; Type: TABLE; Schema: squema1; Owner: postgres
--

CREATE TABLE squema1.grupo (
    id integer NOT NULL
);


ALTER TABLE squema1.grupo OWNER TO postgres;

--
-- Name: grupo_id_seq; Type: SEQUENCE; Schema: squema1; Owner: postgres
--

CREATE SEQUENCE squema1.grupo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE squema1.grupo_id_seq OWNER TO postgres;

--
-- Name: grupo_id_seq; Type: SEQUENCE OWNED BY; Schema: squema1; Owner: postgres
--

ALTER SEQUENCE squema1.grupo_id_seq OWNED BY squema1.grupo.id;


--
-- Name: sesion_conversacion; Type: TABLE; Schema: squema1; Owner: postgres
--

CREATE TABLE squema1.sesion_conversacion (
    telefono character varying(20) NOT NULL,
    esperando character varying(50),
    creado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE squema1.sesion_conversacion OWNER TO postgres;

--
-- Name: sesiones; Type: TABLE; Schema: squema1; Owner: postgres
--

CREATE TABLE squema1.sesiones (
    state text NOT NULL,
    telefono text NOT NULL,
    creado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE squema1.sesiones OWNER TO postgres;

--
-- Name: tarea; Type: TABLE; Schema: squema1; Owner: postgres
--

CREATE TABLE squema1.tarea (
    id integer NOT NULL,
    nombre character varying(100),
    deadline timestamp without time zone,
    tipo character varying(50),
    usuario_tel character varying(20) NOT NULL,
    grupo_id integer,
    status character varying(20) DEFAULT 'PENDIENTE'::character varying
);


ALTER TABLE squema1.tarea OWNER TO postgres;

--
-- Name: tarea_id_seq; Type: SEQUENCE; Schema: squema1; Owner: postgres
--

CREATE SEQUENCE squema1.tarea_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE squema1.tarea_id_seq OWNER TO postgres;

--
-- Name: tarea_id_seq; Type: SEQUENCE OWNED BY; Schema: squema1; Owner: postgres
--

ALTER SEQUENCE squema1.tarea_id_seq OWNED BY squema1.tarea.id;


--
-- Name: usuario; Type: TABLE; Schema: squema1; Owner: postgres
--

CREATE TABLE squema1.usuario (
    id integer NOT NULL,
    tel character varying(20) NOT NULL,
    nombre character varying(100),
    contrasena character varying(100),
    grupo_id integer
);


ALTER TABLE squema1.usuario OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: squema1; Owner: postgres
--

CREATE SEQUENCE squema1.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE squema1.usuario_id_seq OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: squema1; Owner: postgres
--

ALTER SEQUENCE squema1.usuario_id_seq OWNED BY squema1.usuario.id;


--
-- Name: grupo id; Type: DEFAULT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.grupo ALTER COLUMN id SET DEFAULT nextval('squema1.grupo_id_seq'::regclass);


--
-- Name: tarea id; Type: DEFAULT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.tarea ALTER COLUMN id SET DEFAULT nextval('squema1.tarea_id_seq'::regclass);


--
-- Name: usuario id; Type: DEFAULT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.usuario ALTER COLUMN id SET DEFAULT nextval('squema1.usuario_id_seq'::regclass);


--
-- Name: grupo grupo_pkey; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.grupo
    ADD CONSTRAINT grupo_pkey PRIMARY KEY (id);


--
-- Name: sesion_conversacion sesion_conversacion_pkey; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.sesion_conversacion
    ADD CONSTRAINT sesion_conversacion_pkey PRIMARY KEY (telefono);


--
-- Name: sesiones sesiones_pkey; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.sesiones
    ADD CONSTRAINT sesiones_pkey PRIMARY KEY (state);


--
-- Name: tarea tarea_pkey; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.tarea
    ADD CONSTRAINT tarea_pkey PRIMARY KEY (id);


--
-- Name: tarea unique_tarea; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.tarea
    ADD CONSTRAINT unique_tarea UNIQUE (nombre, tipo, deadline, usuario_tel);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_tel_key; Type: CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.usuario
    ADD CONSTRAINT usuario_tel_key UNIQUE (tel);


--
-- Name: sesion_conversacion sesion_conversacion_telefono_fkey; Type: FK CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.sesion_conversacion
    ADD CONSTRAINT sesion_conversacion_telefono_fkey FOREIGN KEY (telefono) REFERENCES squema1.usuario(tel);


--
-- Name: tarea tarea_grupo_id_fk; Type: FK CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.tarea
    ADD CONSTRAINT tarea_grupo_id_fk FOREIGN KEY (grupo_id) REFERENCES squema1.grupo(id);


--
-- Name: tarea tarea_usuario_fk; Type: FK CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.tarea
    ADD CONSTRAINT tarea_usuario_fk FOREIGN KEY (usuario_tel) REFERENCES squema1.usuario(tel);


--
-- Name: usuario usuario_grupo_fk; Type: FK CONSTRAINT; Schema: squema1; Owner: postgres
--

ALTER TABLE ONLY squema1.usuario
    ADD CONSTRAINT usuario_grupo_fk FOREIGN KEY (grupo_id) REFERENCES squema1.grupo(id);


--
-- PostgreSQL database dump complete
--

\unrestrict tmcPGV8oC0y6lzTjjc3EgS8JaReeP23cMhHOSM90rtUlFmNubITPKqQt3wDViJ5

