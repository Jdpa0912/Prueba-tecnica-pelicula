CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favoritas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    pelicula_id VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    year VARCHAR(10),
    poster VARCHAR(500),
    nota TEXT,
    date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_favoritas_usuario_pelicula UNIQUE (usuario_id, pelicula_id)
);
