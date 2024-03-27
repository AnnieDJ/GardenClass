--DROP SCHEMA IF EXISTS garden_club;
--CREATE SCHEMA garden_club;
--USE garden_club;

-- Create member table
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

-- Create bank table for member
CREATE TABLE IF NOT EXISTS bank_info (
    bank_info_id INT PRIMARY KEY AUTO_INCREMENT,
    bank_name VARCHAR(100),
    bank_card VARCHAR(100),
    security_code VARCHAR(50),
    member_id INT,
    FOREIGN KEY (member_id) REFERENCES member(member_id) ON DELETE CASCADE
);

-- Create instructor table
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
    instructor_image_name VARCHAR(100),
    instructor_image LONGBLOB
);

-- Create manager table
CREATE TABLE IF NOT EXISTS manager (
    manager_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(100),
    title VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    manager_image_name VARCHAR(100),
    profile_image LONGBLOB,
    gardering_experience TEXT
);

-- Create Lessons user role table
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

-- Create Locations table
CREATE TABLE IF NOT EXISTS locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    address VARCHAR(255),
    capacity INT
);

-- Create Workshops table
CREATE TABLE IF NOT EXISTS workshops (
    workshop_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    details TEXT,
    location_id INT,
    instructor_id INT,
    manager_id INT,
    price DECIMAL(10,2),
    capacity INT,
    date DATE,
    start_time TIME,
    end_time TIME,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES manager(manager_id) ON DELETE SET NULL
    
);

-- Create Lessons table
CREATE TABLE IF NOT EXISTS one_one_one_lessons (
    lesson_id INT PRIMARY KEY AUTO_INCREMENT,
    lesson_name VARCHAR(255),
    instructor_id INT,
    member_id INT,
    manager_id INT,
    date DATE,
    start_time TIME,
    end_time TIME,
    location_id INT,
    price DECIMAL(10,2) DEFAULT 100.00, -- As per the requirements
    status ENUM('Scheduled', 'Completed', 'Cancelled'),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES manager(manager_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS lessons (
  lesson_id INT AUTO_INCREMENT PRIMARY KEY,
  instructor_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  location_id INT NOT NULL,
  capacity INT NOT NULL,
  price INT NOT NULL
);

-- Create Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    workshop_id INT NULL,
    lesson_id INT NULL,
    one_on_one_id INT NULL,
    booking_type ENUM('Workshop', 'Lesson'),
    status ENUM('Booked', 'Cancelled'),
    FOREIGN KEY (user_id) REFERENCES member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (workshop_id) REFERENCES workshops(workshop_id) ON DELETE SET NULL,
    FOREIGN KEY (one_on_one_id) REFERENCES one_one_one_lessons(lesson_id) ON DELETE SET NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE SET NULL
);


-- Create Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    type ENUM('Annual', 'Monthly'),
    start_date DATE,
    end_date DATE,
    status ENUM('Active', 'Expired'), -- To easily check subscription status
    FOREIGN KEY (user_id) REFERENCES member(member_id) ON DELETE CASCADE
);

-- Create Payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    amount DECIMAL(10,2),
    payment_type ENUM('Subscription', 'Workshop', 'Lesson'),
    payment_date DATE,
    status ENUM('Completed', 'Pending', 'Failed'),
    FOREIGN KEY (user_id) REFERENCES member(member_id) ON DELETE CASCADE
);

-- Create News table
CREATE TABLE IF NOT EXISTS news (
    news_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255),
    content TEXT,
    date_published DATE,
    author_id INT,
    FOREIGN KEY (user_id) REFERENCES member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES manager(manager_id) ON DELETE CASCADE
);


