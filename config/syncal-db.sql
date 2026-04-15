-- Inicialización de la base de datos SynCal
CREATE SCHEMA IF NOT EXISTS squema1;


CREATE TABLE squema1.grupo (
    id SERIAL PRIMARY KEY
);

CREATE TABLE squema1.usuario (
    id SERIAL PRIMARY KEY,
    tel VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100),
    contrasena VARCHAR(100),
    grupo_id INTEGER,
    constraint usuario_grupo_fk FOREIGN KEY (grupo_id) REFERENCES squema1.grupo(id)
);


CREATE TABLE squema1.tarea (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    deadline DATE,
    tipo VARCHAR(50),
    usuario_tel VARCHAR(20) NOT NULL,
    grupo_id INTEGER,
    constraint tarea_usuario_fk FOREIGN KEY (usuario_tel) REFERENCES squema1.usuario(tel),
    constraint tarea_grupo_id_fk FOREIGN KEY (grupo_id) REFERENCES squema1.grupo(id)
);

SET search_path TO squema1;