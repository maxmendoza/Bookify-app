create database library;
use library;
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    name_rol VARCHAR(100) NOT NULL,
    status BOOLEAN DEFAULT TRUE
);

-- "Users"
CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    lastname VARCHAR(200) NOT NULL,
    second_lastname VARCHAR(200),
    email VARCHAR(100) NOT NULL,
    password VARCHAR(200) NOT NULL,
    phone VARCHAR(12) NOT NULL,
    id_rol INT,
    status BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- "Rents"
CREATE TABLE rents (
    id_rents INT AUTO_INCREMENT PRIMARY KEY,
    initial_date DATE NOT NULL,
    final_date DATE NOT NULL,
    id_user INT,
    id_book INT,
    status BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_user) REFERENCES users(id_usuario),
    FOREIGN KEY (id_book) REFERENCES libros(id_book)
);

-- "Books"
CREATE TABLE books (
    id_book INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    gener VARCHAR(100) NOT NULL,
    year VARCHAR(4) NOT NULL,
    description VARCHAR(300) NOT NULL,
    synopsis VARCHAR(1000) NOT NULL,
    image_url VARCHAR(255),
    pdf_url VARCHAR(255),
    status BOOLEAN DEFAULT TRUE
);


-- Book images
CREATE TABLE images_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255),
    id_book INT,
    FOREIGN KEY (id_book) REFERENCES books(id_book)
);

-- Script SQL para crear la tabla "pdfs_libros"
CREATE TABLE pdfs_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255),
    id_book INT,
    FOREIGN KEY (id_book) REFERENCES books(id_book)
);

-- Script SQL para crear la tabla "recomendaciones"
CREATE TABLE recommendations (
    id_recommendation INT AUTO_INCREMENT PRIMARY KEY,
    id_book INT NOT NULL,
    id_user INT NOT NULL,
    recommendation_text VARCHAR(1000) NOT NULL,
    FOREIGN KEY (id_book) REFERENCES books(id_book),
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);