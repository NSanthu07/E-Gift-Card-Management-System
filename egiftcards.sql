CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY,
    card_id VARCHAR(50) NOT NULL,
    rating INT NOT NULL,
    comments TEXT,
    feedback_date DATE NOT NULL
);

CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    card_id INT,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (card_id) REFERENCES gift_cards(card_id)
);

-- Create the promotions table
CREATE TABLE promotions (
    promotion_id INT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    validity_period VARCHAR(50) NOT NULL
);

-- Create the merchants table
CREATE TABLE merchants (
    merchant_id INT PRIMARY KEY,
    merchant_name VARCHAR(255) NOT NULL,
    merchant_email VARCHAR(255) NOT NULL,
    merchant_password VARCHAR(255) NOT NULL,
    merchant_phone VARCHAR(20) NOT NULL,
    merchant_address VARCHAR(255) NOT NULL
);

-- Create the users table
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    user_phone VARCHAR(20) NOT NULL,
    user_address VARCHAR(255) NOT NULL
);

-- Create the gift_cards table
CREATE TABLE gift_cards (
    card_id INT PRIMARY KEY,
    card_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    expiry_date DATE NOT NULL,
    activation_date DATE NOT NULL
);

CREATE TABLE done_gift_cards (
    c_id INT PRIMARY KEY
);