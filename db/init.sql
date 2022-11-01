CREATE DATABASE csc535;
use csc535;

CREATE USER 'csc535'@'%%' IDENTIFIED BY 'welcome123';
GRANT ALL PRIVILEGES ON * . * TO 'csc535'@'%%';
FLUSH PRIVILEGES;


CREATE TABLE users(
    fname VARCHAR(20),
    lname VARCHAR(20),
    username VARCHAR(20),
    email VARCHAR(50),
    password VARCHAR(500),
    address VARCHAR(50),
    city VARCHAR(25),
    zipCode VARCHAR(5),
    phone VARCHAR(10),
    profile INT,
    accountEnabled BOOL,
    lastLogin DATETIME,
    accountCreated DATE, 
    totpEnabled BOOL,
    PRIMARY KEY(username));

INSERT INTO users(username, password, profile) 
VALUES
('admin', '$5$rounds=535000$t6Y73jKPWxeNh9Ru$teQmHgaGdlo6U/xUzdYoK414w9P7Uhyu2b5GIA1tGv1', 1)
