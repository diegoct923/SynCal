-- Inicialización de la base de datos SynCal
CREATE SCHEMA IF NOT EXISTS squema1;

SET search_path TO squema1;
CREATE TABLE grupo (
    id SERIAL PRIMARY KEY
);

CREATE TABLE usuario (
    id SERIAL,
    tel VARCHAR(20),
    nombre VARCHAR(100),
    contrasena VARCHAR(100),
    grupo_id INTEGER,
    constraint usuario_tel_unique UNIQUE (tel)
    constraint usuario_grupo_fk FOREIGN KEY (grupo_id) REFERENCES grupo(id)
);

ALTER TABLE usuario ADD PRIMARY KEY(id, tel);

CREATE TABLE tarea (
    id SERIAL,
    nombre VARCHAR(100),
    deadline DATE,
    tipo VARCHAR(50),
    usuario_tel INTEGER,
    grupo_id INTEGER,
    constraint tarea_pk PRIMARY KEY (id),
    constraint tarea_usuario_fk FOREIGN KEY (usuario_tel) REFERENCES usuario(tel),
    constraint tarea_grupo_id_fk FOREIGN KEY (grupo_id) REFERENCES grupo(id)
);
 