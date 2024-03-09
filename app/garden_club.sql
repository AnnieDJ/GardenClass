--CREATE SCHEMA IF NOT EXISTS garden_club;
CREATE TABLE IF NOT EXISTS member (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(100),
    title VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(100),
    date_of_birth DATE,
    subscription_date DATE,
    type VARCHAR(100),
    expiry_date DATE
);

CREATE TABLE IF NOT EXISTS instructor (
    instructor_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(100),
    title VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(100),
    instructor_profile TEXT,
    instructor_image LONGBLOB
);

CREATE TABLE IF NOT EXISTS manager (
    manager_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(100),
    title VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    profile_image LONGBLOB,
    gardering_experience TEXT
);

CREATE TABLE IF NOT EXISTS user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(100),
    password VARCHAR(100),
    role ENUM('Member', 'Instructor', 'Manager'),
    related_manager_id INT,
    related_instructor_id INT,
    related_member_id INT,
    FOREIGN KEY (related_manager_id) REFERENCES manager(manager_id) ON DELETE CASCADE,
    FOREIGN KEY (related_instructor_id) REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (related_member_id) REFERENCES member(member_id) ON DELETE CASCADE
);