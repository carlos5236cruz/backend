CREATE DATABASE IF NOT EXISTS annyle91_atb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE annyle91_atb;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','operator') NOT NULL DEFAULT 'operator',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    original_filename VARCHAR(300) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS template_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    column_name VARCHAR(200) NOT NULL,
    column_order INT NOT NULL,
    data_type VARCHAR(50) DEFAULT 'text',
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    parent_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS category_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    attribute_name VARCHAR(200) NOT NULL,
    default_value VARCHAR(500) DEFAULT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    category_id INT DEFAULT NULL,
    status ENUM('pending','reviewed') NOT NULL DEFAULT 'pending',
    created_by INT,
    updated_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS product_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    column_id INT NOT NULL,
    value TEXT DEFAULT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (column_id) REFERENCES template_columns(id) ON DELETE CASCADE,
    UNIQUE KEY uq_product_column (product_id, column_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS export_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exported_by INT,
    filename VARCHAR(300),
    total_products INT DEFAULT 0,
    filter_used VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exported_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Default admin user (password: admin123)
INSERT INTO users (name, email, password_hash, role) VALUES
('Administrador', 'admin@bling.com', '$2b$12$9CvIFQqhJhtzAYsXSc4gQuxG9sHSVAWf.6ZYQwfcfk2OXYcZJOn2K', 'admin')
ON DUPLICATE KEY UPDATE name=name;
