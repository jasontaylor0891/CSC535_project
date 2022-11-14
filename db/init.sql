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
    phone VARCHAR(10),
    profile INT,
    accountEnabled BOOL,
    lastLogin DATETIME,
    accountCreated DATE, 
    totpEnabled BOOL,
    PRIMARY KEY(username));

CREATE TABLE list (
	listid INT PRIMARY KEY AUTO_INCREMENT,
	listname VARCHAR(20),
    listdesc VARCHAR(100),
    username VARCHAR(20),
    FOREIGN KEY(Username) REFERENCES users(username) ON UPDATE CASCADE
);

CREATE TABLE reminders(
    reminderid INT PRIMARY KEY AUTO_INCREMENT,
    remindername VARCHAR(50),
    reminderdesc VARCHAR(100),
    priority VARCHAR(10),
    reminderstartdate DATE, 
    flaged BOOL,
	username VARCHAR(20),
	listid INT,
	FOREIGN KEY(Username) REFERENCES users(username) ON UPDATE CASCADE,
	FOREIGN KEY(listid) REFERENCES list(listid) ON UPDATE CASCADE
);

INSERT INTO users(username, password, profile) 
VALUES
('admin', '$5$rounds=535000$t6Y73jKPWxeNh9Ru$teQmHgaGdlo6U/xUzdYoK414w9P7Uhyu2b5GIA1tGv1', 1),
('paid', '$5$rounds=535000$t6Y73jKPWxeNh9Ru$teQmHgaGdlo6U/xUzdYoK414w9P7Uhyu2b5GIA1tGv1', 2),
('free', '$5$rounds=535000$t6Y73jKPWxeNh9Ru$teQmHgaGdlo6U/xUzdYoK414w9P7Uhyu2b5GIA1tGv1', 3);

INSERT INTO list(listname, listdesc, username)
VALUES
('Default', 'Default list', 'paid'),
('Work', 'Work list', 'paid'),
('Default', 'Default list', 'free');
