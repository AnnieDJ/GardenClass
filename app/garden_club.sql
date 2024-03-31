DROP SCHEMA IF EXISTS garden_club;
CREATE SCHEMA garden_club;
USE garden_club;

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
    workshop_image VARCHAR(255),
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
CREATE TABLE IF NOT EXISTS one_on_one_lessons (
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
    FOREIGN KEY (one_on_one_id) REFERENCES one_on_one_lessons(lesson_id) ON DELETE SET NULL,
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



INSERT INTO instructor
  (instructor_id, user_name, title, first_name, last_name, position, phone_number, email, address, instructor_profile)
VALUES
  (1, 'john_instructor', 'Dr.', 'John', 'Doe', 'Head Instructor', '123456789', 'john.doe@example.com', '123 Main St, City, Country', 'Experienced horticulturist with expertise in plant biology.'),
  (2, 'lisa_green', 'Ms.', 'Lisa', 'Green', 'Instructor', '234560123', 'lisa.green@example.com', '124 Plant St', 'Expert in urban gardening'),
  (3, 'david_bloom', 'Mr.', 'David', 'Bloom', 'Junior Instructor', '234560456', 'david.bloom@example.com', '125 Seedling St', 'Passionate about flower gardening'),
  (4, 'sarah_field', 'Ms.', 'Sarah', 'Field', 'Intermediate Instructor', '234560789', 'sarah.field@example.com', '126 Sprout St', 'Specializes in field crops'),
  (5, 'mike_branch', 'Mr.', 'Mike', 'Branch', 'Senior Instructor', '234560012', 'mike.branch@example.com', '127 Leaf Ave', 'Tree cultivation expert'),
  (6, 'amy_sprout', 'Ms.', 'Amy', 'Sprout', 'Chief Instructor', '234560345', 'amy.sprout@example.com', '128 Bud Blvd', 'Enjoys teaching about plant propagation');
  
INSERT INTO manager
  (manager_id, user_name, title, first_name, last_name, position, phone_number, email, profile_image, gardering_experience)
VALUES
  (2, 'tom_branch', 'Mr.', 'Tom', 'Branch', 'Assistant Manager', '987654322', 'tom.branch@gardensociety.org', NULL, 'Expert in tree shaping and bonsai'),
  (3, 'lisa_green', 'Mrs.', 'Lisa', 'Green', 'Operations Manager', '987654323', 'lisa.green@gardensociety.org', NULL, 'Specializes in organic gardening and permaculture');
  
INSERT INTO member
(member_id, user_name, title, first_name, last_name, position, phone_number, email, address, date_of_birth, subscription_date, type, expiry_date)
VALUES
(2, 'alice_wonder', 'Ms.', 'Alice', 'Wonder', 'Member', '1234567891', 'alice@example.com', '124 Main St', '1985-05-05', '2024-02-24', 'Regular', '2025-02-24'),
(3, 'bob_builder', 'Mr.', 'Bob', 'Builder', 'Member', '1234567892', 'bob@example.com', '125 Main St', '1986-06-06', '2024-02-25', 'Regular', '2025-02-25'),
(4, 'charlie_brown', 'Mr.', 'Charlie', 'Brown', 'Member', '1234567893', 'charlie@example.com', '126 Main St', '1987-07-07', '2024-02-26', 'Regular', '2025-02-26'),
(5, 'daisy_duck', 'Ms.', 'Daisy', 'Duck', 'Member', '1234567894', 'daisy@example.com', '127 Main St', '1988-08-08', '2024-02-27', 'Regular', '2025-02-27'),
(6, 'edward_scissor', 'Mr.', 'Edward', 'Scissor', 'Member', '1234567895', 'edward@example.com', '128 Main St', '1989-09-09', '2024-02-28', 'Regular', '2025-02-28'),
(7, 'fiona_fair', 'Ms.', 'Fiona', 'Fair', 'Member', '1234567896', 'fiona@example.com', '129 Main St', '1990-10-10', '2024-02-29', 'Regular', '2025-02-28'), -- changed date here
(8, 'george_giant', 'Mr.', 'George', 'Giant', 'Member', '1234567897', 'george@example.com', '130 Main St', '1991-11-11', '2024-03-01', 'Regular', '2025-03-01'),
(9, 'hazel_hunt', 'Ms.', 'Hazel', 'Hunt', 'Member', '1234567898', 'hazel@example.com', '131 Main St', '1992-12-12', '2024-03-02', 'Regular', '2025-03-02'),
(10, 'ivan_ink', 'Mr.', 'Ivan', 'Ink', 'Member', '1234567899', 'ivan@example.com', '132 Main St', '1993-01-13', '2024-03-03', 'Regular', '2025-03-03'),
(11, 'jessica_jewel', 'Ms.', 'Jessica', 'Jewel', 'Member', '1234567800', 'jessica@example.com', '133 Main St', '1994-02-14', '2024-03-04', 'Regular', '2025-03-04'),
(12, 'kyle_king', 'Mr.', 'Kyle', 'King', 'Member', '1234567811', 'kyle@example.com', '134 Main St', '1995-03-15', '2024-03-05', 'Regular', '2025-03-05'),
(13, 'laura_lake', 'Ms.', 'Laura', 'Lake', 'Member', '1234567822', 'laura@example.com', '135 Main St', '1996-04-16', '2024-03-06', 'Regular', '2025-03-06'),
(14, 'mike_mountain', 'Mr.', 'Mike', 'Mountain', 'Member', '1234567833', 'mike@example.com', '136 Main St', '1997-05-17', '2024-03-07', 'Regular', '2025-03-07'),
(15, 'nancy_night', 'Ms.', 'Nancy', 'Night', 'Member', '1234567844', 'nancy@example.com', '137 Main St', '1998-06-18', '2024-03-08', 'Regular', '2025-03-08'),
(16, 'oscar_ocean', 'Mr.', 'Oscar', 'Ocean', 'Member', '1234567855', 'oscar@example.com', '138 Main St', '1999-07-19', '2024-03-09', 'Regular', '2025-03-09'),
(17, 'patty_peak', 'Ms.', 'Patty', 'Peak', 'Member', '1234567866', 'patty@example.com', '139 Main St', '2000-08-20', '2024-03-10', 'Regular', '2025-03-10'),
(18, 'quentin_quarry', 'Mr.', 'Quentin', 'Quarry', 'Member', '1234567877', 'quentin@example.com', '140 Main St', '2001-09-21', '2024-03-11', 'Regular', '2025-03-11'),
(19, 'rachel_rain', 'Ms.', 'Rachel', 'Rain', 'Member', '1234567888', 'rachel@example.com', '141 Main St', '2002-10-22', '2024-03-12', 'Regular', '2025-03-12'),
(20, 'steven_star', 'Mr.', 'Steven', 'Star', 'Member', '1234567890', 'steven@example.com', '142 Main St', '2003-11-23', '2024-03-13', 'Regular', '2025-03-13');

INSERT INTO locations (location_id,name, address, capacity) VALUES
(1,'Garden Central', '49 Plant Lane, Auckland', 50),
(2,'Botany Bay', '47 Plant Lane, Auckland', 75),
(3,'Green Space Venue', '50 Plant Lane, Auckland', 100);

INSERT INTO workshops (title, details, location_id, instructor_id, manager_id, price, capacity, date, start_time, end_time, workshop_image) VALUES
('Introduction to Botany', 'Learn the basics of plant biology and identification.', 1, 2, 2, 50.00, 20, '2024-04-15', '10:00', '12:00', 'workshops_images/workshop1.png'),
('Advanced Organic Gardening', 'Deep dive into organic farming techniques and practices.', 2, 3, 2, 75.00, 15, '2024-05-20', '09:00', '11:00', 'workshops_images/workshop2.png'),
('Landscape Design Workshop', 'Design your dream garden with professional guidance.', 3, 4, 3, 65.00, 10, '2024-06-25', '14:00', '17:00', 'workshops_images/workshop3.png');
    
INSERT INTO one_on_one_lessons (instructor_id, member_id, manager_id, date, start_time, end_time, location_id, price, status) VALUES
(2, 2, 2, '2024-07-01', '09:00', '10:00', 1, 100.00, 'Scheduled'),
(3, 3, 3, '2024-08-05', '11:00', '12:00', 2, 100.00, 'Scheduled'),
(4, 4, 2, '2024-09-10', '13:00', '14:00', 3, 100.00, 'Scheduled');

INSERT INTO lessons (instructor_id, title, date, start_time, end_time, location_id, capacity, price) VALUES
(2, 'Gardening Fundamentals', '2024-10-10', '08:00', '10:00', 1, 25, 30),
(3, 'Pest Management in Gardening', '2024-11-15', '09:00', '11:00', 2, 20, 40),
(4, 'Soil Health and Nutrition', '2024-12-20', '14:00', '16:00', 3, 30, 35);


-- 在 member 表中创建一条数据
INSERT INTO member (user_name, title, first_name, last_name, position, phone_number, email, address, date_of_birth, subscription_date, type, expiry_date) 
VALUES ('john_doe', 'Mr', 'John', 'Doe', 'Member', '1234567890', 'john@example.com', '123 Main St', '1990-01-01', '2024-02-23', 'Regular', '2025-02-23');

-- 在 user 表中创建一条数据
INSERT INTO user (user_name, password, role, related_member_id) 
VALUES ('john_doe', 'cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0', 'Member', LAST_INSERT_ID()); 

-- Insert data into the manager table
INSERT INTO manager (user_name, title, first_name, last_name, position, phone_number, email, manager_image_name,profile_image, gardering_experience)
VALUES ('jane_smith', 'Ms.', 'Jane', 'Smith', 'Senior Manager', '987654321', 'jane.smith@example.com',NULL, NULL, 'Experienced horticulturist specializing in landscape design.');

-- Insert data into the user table
INSERT INTO user (user_name, password, role, related_manager_id, related_instructor_id, related_member_id)
VALUES ('jane_smith', 'cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0', 'Manager', LAST_INSERT_ID(), NULL, NULL);

-- Insert data into the user table
INSERT INTO user (user_name, password, role, related_manager_id, related_instructor_id, related_member_id)
VALUES ('john_instructor', 'cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0', 'Instructor', NULL, LAST_INSERT_ID(), NULL);

-- Insert a group lesson for instructor with ID 1
INSERT INTO lessons (instructor_id, title, date, start_time, end_time, location_id, capacity, price)
VALUES
(1, 'Horticulture 101', '2024-05-10', '09:00:00', '11:00:00', 1, 20, 50.00),
(1, 'Advanced Plant Care', '2024-05-17', '13:00:00', '15:00:00', 2, 15, 60.00);

-- Insert a one-on-one lesson for instructor with ID 1
INSERT INTO one_on_one_lessons (instructor_id, member_id, manager_id, date, start_time, end_time, location_id, price, status)
VALUES
(1, 2, 2, '2024-05-10', '14:00:00', '15:00:00', 1, 100.00, 'Scheduled'),
(1, 3, 2, '2024-05-17', '16:00:00', '17:00:00', 2, 100.00, 'Scheduled');



