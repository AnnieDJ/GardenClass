-- DROP SCHEMA IF EXISTS garden_club;
-- CREATE SCHEMA garden_club;
-- USE garden_club;

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
    is_attended BOOLEAN DEFAULT FALSE, 
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

-- Test Data password is John1234

INSERT INTO `instructor` VALUES (2,'michael_instructor','Dr.','Michael','Instructor','Fitness Trainer','9876543210','michael_instructor@example.com','456 Elm St','Certified fitness trainer specializing in weight training and nutrition.','michael_image.jpg',NULL),(3,'jim_instructor','Mr.','Jim','Instructor','Dance Instructor','5551234567','jim_instructor@example.com','789 Oak St','Professional dance instructor offering classes in various dance styles.','jim_image.jpg',NULL),(4,'susan_instructor','Ms.','Susan','Instructor','Swimming Coach','9998887776','susan_instructor@example.com','321 Pine St','Experienced swimming coach providing personalized training for all ages and skill levels.','susan_image.jpg',NULL),(5,'david_instructor','Mr.','David','Instructor','Martial Arts Instructor','4445556666','david_instructor@example.com','654 Birch St','Black belt martial arts instructor offering classes in self-defense and traditional martial arts forms.','david_image.jpg',NULL);
INSERT INTO `member` VALUES (1,'john_doe','Mr.','John','Doe','Manager','1234567890','john@example.com','123 Main St','1990-01-01','2023-01-01','Annual','2023-12-31'),(2,'jane_smith','Ms.','Jane','Smith','Instructor','9876543210','jane@example.com','456 Elm St','1995-05-15','2023-01-01','Annual','2023-12-31'),(3,'bob_johnson','Mr','Bob','Johnson','Member','5551234567','bob@example.com','789 Oak St','1988-08-20','2024-01-01','Annual','2025-01-31'),(4,'alice_wong','Ms.','Alice','Wong','Member','9998887776','alice@example.com','321 Pine St','1987-03-10','2023-01-01','Monthly','2023-01-31'),(5,'michael_davis','Dr.','Michael','Davis','Instructor','4445556666','michael@example.com','654 Birch St','1980-12-05','2023-01-01','Annual','2023-12-31'),(6,'emp_id','Mrs','EMP','ID','Member','123456890','test@gmail.com','124 core street','2003-01-14',NULL,NULL,NULL),(7,'emp_nf','Mr','emp','nf','Member','1234567890','test1@gmail.com','123 core street','1997-01-01',NULL,NULL,NULL),(8,'qwe_er','Mr','qwe','er','Member','1234567890','test3@gmail.com','234 core street','1996-01-01',NULL,NULL,NULL),(9,'qwe_er','Mr','qwe','er','Member','1234567890','test3@gmail.com','234 core street','1996-01-01',NULL,NULL,NULL),(10,'poi_ii','Mr','poi','11','Member','123456890','tret@gmail.com','123 street street','1995-01-01',NULL,NULL,NULL),(11,'zxc_qwe','Miss','zxc','qwe','Member','1234567890','zxc@gmail.com','345 core street','1996-01-01',NULL,NULL,NULL),(12,'wer_xcv','Mr','wer','xcv','Member','12345678909','wer@gmail.com','234 core street','1993-01-01',NULL,NULL,NULL),(13,'val_val','Mr','val','val','Member','1234567890','erer@gmail.com','erer','1993-01-01',NULL,NULL,NULL),(14,'qaz_wsx','Mr','qaz','wsx','Member','1234567890','rew@gmail.com','123 cre ','1994-01-01',NULL,NULL,NULL),(15,'qaz_wsx','Mr','qaz','wsx','Member','1234567890','rew@gmail.com','123 cre ','1994-01-01',NULL,NULL,NULL),(16,'qaz_wsx','Mr','Bob','Johnson','Member','5551234567','bob@example.com','789 Oak St','1988-08-20','2024-01-01','Monthly','2025-01-31'),(17,'edc_rv','Mr','edc','rfv','Member','1234567890','edc@gmail.com','234','1996-01-01',NULL,NULL,NULL);
INSERT INTO `manager` VALUES (1,'alice_manager','Mr','Alice','Manager','Event Manager','1112223333','alice_manager@example.com','guy-mechanic.png',NULL,'Experienced in event planning and coordination.'),(2,'peter_manager','Mr.','Peter','Manager','Operations Manager','3334445555','peter_manager@example.com','peter_image.jpg',NULL,'Skilled in managing day-to-day operations and optimizing workflow.'),(3,'sophia_manager','Ms.','Sophia','Manager','Sales Manager','7778889999','sophia_manager@example.com','sophia_image.jpg',NULL,'Proven track record in achieving sales targets and driving revenue growth.'),(4,'tom_manager','Mr.','Tom','Manager','Marketing Manager','9990001111','tom_manager@example.com','tom_image.jpg',NULL,'Expertise in developing and implementing marketing strategies to promote products and services.'),(5,'linda_manager','Ms.','Linda','Manager','HR Manager','2223334444','linda_manager@example.com','linda_image.jpg',NULL,'Specialized in talent acquisition, employee relations, and performance management.');
INSERT INTO `user` VALUES (1,'alice_manager','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Manager',1,NULL,NULL),(2,'peter_manager','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Manager',2,NULL,NULL),(3,'sophia_manager','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Manager',3,NULL,NULL),(4,'tom_manager','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Manager',4,NULL,NULL),(5,'linda_manager','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Manager',5,NULL,NULL),(7,'michael_instructor','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Instructor',NULL,2,NULL),(8,'jim_instructor','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Instructor',NULL,3,NULL),(9,'susan_instructor','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Instructor',NULL,4,NULL),(10,'david_instructor','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Instructor',NULL,5,NULL),(11,'john_doe','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,1),(12,'jane_smith','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,2),(13,'bob_johnson','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,3),(14,'alice_wong','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,4),(15,'michael_davis','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,5),(16,'emp_id','0f9710903b8a33440a86970b59403edf77ea0c2ac98acf01969612c5a49b3292','Member',NULL,NULL,6),(17,'emp_nf','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,7),(18,'qwe_er','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,8),(19,'qwe_er','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,9),(20,'poi_ii','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,10),(21,'zxc_qwe','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,11),(22,'wer_xcv','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,12),(23,'val_val','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,13),(24,'qaz_wsx','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,14),(27,'edc_rv','cee7498757b4bcb505ee4c90093f37454daf9579f80c29d18b455d80e57ffad0','Member',NULL,NULL,17);
INSERT INTO `bank_info` VALUES (1,'ANZ','1234567890123456','125',1),(2,'Bank B','9876543210987654','456',2),(3,'Bank C','1111222233334444','789',3),(4,'Bank D','5555666677778888','321',4),(5,'Bank E','9999888877776666','654',5),(6,'ANZ','1234567890123456','123',6),(7,'ANZ','0987654321098765','098',7),(8,'ANZ','1234567890987654','123',8),(9,'ANZ','1234567890987654','123',9),(10,'ANZ','1234567890912345','345',10),(11,'ANZ','1234567890123456','123',11),(12,'ANZ','1234567890123456','890',12),(13,'ANZ','1234567890123456','123',13),(14,'ANZ','1234567890987654','123',14),(15,'ANZ','1234567890987654','123',15),(16,'ANZ','1234567890987654','123',16),(17,'ANZ','1234567890123456','123',17);
INSERT INTO `locations` VALUES (1,'Location A','123 Main St',50),(2,'Location B','456 Elm St',100),(3,'Location C','789 Oak St',75),(4,'Location D','321 Pine St',80);
INSERT INTO `lessons` VALUES (1,2,'Yoga Class','2024-06-01','09:00:00','10:00:00',1,30,20),(2,3,'Fitness Class','2024-01-25','10:00:00','11:00:00',2,25,25),(3,4,'Dance Workshop','2024-05-30','13:00:00','14:00:00',2,100,30),(4,5,'Swimming Lesson','2023-12-16','12:00:00','13:00:00',4,15,15),(5,1,'Martial Arts Class','2023-12-18','13:00:00','14:00:00',5,20,35),(7,2,'Lesson 2','2024-06-02','10:00:00','12:00:00',2,25,60),(9,1,'add lesson test','2024-04-26','03:56:00','04:56:00',2,67,567),(10,1,'Update 1 after delete','2024-04-26','08:12:00','09:12:00',4,50,345),(12,1,'test time','2024-04-25','10:52:00','11:52:00',1,50,45),(13,1,'test time 2','2024-04-26','09:53:00','10:53:00',2,50,45),(14,1,'test capa','2024-04-26','10:53:00','11:53:00',1,50,56);
INSERT INTO `one_on_one_lessons` VALUES (1,'Private Yoga Session',2,3,1,'2024-12-17','10:00:00','11:00:00',2,100.00,'Scheduled'),(2,'Personal Training',3,4,2,'2023-12-22','14:05:00','15:00:00',3,100.00,'Scheduled'),(3,'Individual Dance Lesson',4,5,3,'2023-12-27','15:00:00','16:00:00',3,100.00,'Scheduled'),(8,NULL,2,8,NULL,'2024-04-24','10:48:00','11:48:00',2,45.00,'Completed'),(9,NULL,2,13,NULL,'2024-04-25','10:50:00','11:50:00',2,45.00,'Completed'),(10,NULL,2,1,NULL,'2024-04-26','10:51:00','11:51:00',2,56.00,'Completed');
INSERT INTO `workshops` VALUES (2,'Fitness Bootcamp','Get fit and healthy with our intensive fitness bootcamp.',2,3,2,'fitness_image.jpg',50.00,30,'2023-12-20','10:00:00','12:00:00'),(3,'Dance Class','Learn to dance like a pro with our experienced instructors.',3,4,3,'dance_image.jpg',40.00,25,'2023-12-25','11:00:00','13:00:00'),(4,'Swimming Lessons','Improve your swimming skills with personalized coaching.',4,5,4,'swimming_image.jpg',35.00,15,'2023-12-30','12:00:00','14:00:00'),(5,'Martial Arts Seminar','Master the art of self-defense with our martial arts experts.',1,NULL,5,NULL,45.00,25,'2024-01-05','13:00:00','15:00:00'),(11,'Yoga Workshop','Join us for a rejuvenating yoga session.',1,2,1,'yoga_image.jpg',30.00,20,'2024-07-15','09:00:00','11:00:00'),(12,'Fitness Bootcamp','Get fit and healthy with our intensive fitness bootcamp.',1,3,2,NULL,45.60,30,'2024-05-20','10:00:00','12:00:00'),(13,'Dance Class','Learn to dance like a pro with our experienced instructors.',3,4,3,'dance_image.jpg',40.00,25,'2024-06-25','11:00:00','13:00:00'),(14,'Swimming Lessons','Improve your swimming skills with personalized coaching.',4,5,4,'swimming_image.jpg',35.00,15,'2024-08-30','12:00:00','14:00:00'),(15,'Martial Arts Seminar','Master the art of self-defense with our martial arts experts.',4,NULL,5,'martial_arts_image.jpg',45.00,20,'2024-05-05','13:00:00','15:00:00'),(16,'232',NULL,4,NULL,NULL,'workshops_images/workshop1.png',222.00,222,'2024-04-08','21:38:00','22:37:00'),(18,'title `',NULL,NULL,NULL,NULL,'workshops_images/workshop1.png',34.00,1,'2024-04-08','15:31:00','16:31:00'),(21,'Workshop Path Test',NULL,1,NULL,NULL,'app/workshops_images/21.jpg',34.00,45,'2024-04-27','15:46:00','16:46:00'),(22,'Workshop Test Path ',NULL,1,NULL,NULL,NULL,345.00,56,'2024-04-26','14:49:00','15:49:00'),(23,'Workshop Test Path ',NULL,1,NULL,NULL,'workshops_images/23.jpg',345.00,56,'2024-04-26','14:49:00','15:49:00'),(28,'test time validation',NULL,2,3,NULL,'workshops_images/28.jpg',345.00,50,'2024-04-30','10:14:00','11:14:00'),(29,'Test Workshop Time',NULL,1,2,NULL,'workshops_images/29.jpg',450.00,50,'2024-04-30','10:25:00','11:25:00'),(30,'change titile',NULL,1,3,NULL,'workshops_images/30.jpg',45.00,50,'2024-04-30','10:35:00','11:35:00'),(31,'test price',NULL,1,3,NULL,'workshops_images/31.jpg',89.00,50,'2024-04-26','10:38:00','11:38:00');
INSERT INTO `news` VALUES (1,1,'New Yoga Workshop','Join us for our latest yoga workshop.','2023-12-01',1),(2,2,'Fitness Bootcamp Announcement','Get ready for our upcoming fitness bootcamp.','2023-12-05',2),(3,3,'Dance Workshop Registration Open','Sign up now for our dance workshop.','2023-12-10',3),(4,4,'Swimming Lesson Schedule Update','Check out our revised swimming lesson schedule.','2023-12-15',4),(5,5,'Martial Arts Seminar Registration','Register now for our martial arts seminar.','2023-12-20',5),(6,1,'testing news 1','test','2024-04-20',1),(8,NULL,'workshop Swimming Lessons has been cancelled','workshop Swimming Lessons has been cancelled becasue manager has deleted it.','2024-04-22',NULL),(9,3,'Your one on one lesson has been cancelled','Your one on one lesson has been cancelled becasue manager has deleted it.','2024-04-22',1),(10,NULL,'workshop Dance Class has been cancelled','workshop Dance Class has been cancelled becasue manager has deleted it.','2024-04-22',1),(11,NULL,'Lesson Fitness Class has been cancelled','Lesson Fitness Class has been cancelled becasue manager has deleted it.','2024-04-22',1),(12,NULL,'workshop  has been cancelled','workshop  has been cancelled becasue manager has deleted it.','2024-04-22',1),(13,NULL,'Lesson test has been cancelled','Lesson test has been cancelled becasue manager has deleted it.','2024-04-22',1),(14,4,'Pay Subscription','Please pay your subscription because it will be expired soon or has expired.','2024-04-23',1),(15,5,'Pay Subscription','Please pay your subscription because it will be expired soon or has expired.','2024-04-23',1),(16,2,'Pay Subscription','Please pay your subscription because it will be expired soon or has expired.','2024-04-23',1),(17,17,'You havent pay the subscription, please pay it soon.','Please pay The subscription as soon as you can, thanks.','2024-04-23',NULL),(18,4,'Pay Subscription','Please pay your subscription because it will be expired soon or has expired.','2024-04-23',1);
INSERT INTO `payments` VALUES (1,3,100.00,'Subscription','2023-01-01','Completed'),(2,4,50.00,'Workshop','2023-12-15','Completed'),(3,5,35.00,'Lesson','2023-12-16','Completed'),(4,1,20.00,'Workshop','2023-12-10','Completed'),(5,2,100.00,'Subscription','2023-01-01','Completed'),(6,1,100.00,'Subscription','2024-04-04','Completed'),(7,1,1000.00,'Subscription','2024-04-05','Completed'),(8,1,1000.00,'Subscription','2024-04-05','Completed'),(9,1,1000.00,'Subscription','2024-04-05','Completed'),(10,1,1000.00,'Subscription','2024-04-05','Completed'),(11,1,20.00,'Lesson','2024-04-07','Completed'),(12,1,20.00,'Lesson','2024-04-07','Completed'),(13,1,50.00,'Workshop','2024-04-07','Completed'),(14,1,50.00,'Workshop','2024-04-07','Completed'),(15,1,50.00,'Workshop','2024-04-07','Completed'),(16,1,50.00,'Workshop','2024-04-07','Completed'),(17,1,25.00,'Lesson','2024-04-07','Completed'),(18,1,25.00,'Lesson','2024-04-07','Completed'),(19,1,30.00,'Lesson','2024-04-08','Completed'),(20,1,50.00,'Workshop','2024-04-08','Completed'),(21,1,15.00,'Lesson','2024-04-08','Completed'),(22,1,20.00,'Lesson','2024-04-08','Completed'),(23,1,50.00,'Lesson','2024-04-09','Completed'),(24,1,45.60,'Workshop','2024-04-10','Completed'),(25,1,111.00,'Workshop','2024-04-10','Completed'),(26,1,60.00,'Lesson','2024-04-17','Completed'),(27,1,100.00,'Lesson','2024-04-17','Completed'),(28,1,100.00,'Lesson','2024-04-17','Completed'),(29,1,45.00,'Workshop','2024-04-17','Completed'),(30,6,1000.00,'Subscription','2024-04-20','Completed'),(31,7,1000.00,'Subscription','2024-04-20','Completed'),(32,7,567.00,'Lesson','2024-04-21','Completed'),(33,7,345.00,'Workshop','2024-04-21','Completed'),(34,9,1000.00,'Subscription','2024-04-21','Completed'),(35,11,1000.00,'Subscription','2024-04-22','Completed'),(36,13,1000.00,'Subscription','2024-04-22','Completed'),(37,13,345.00,'Workshop','2024-04-22','Completed'),(38,16,1000.00,'Subscription','2024-04-23','Completed');
INSERT INTO `subscriptions` VALUES (1,3,'Annual','2024-01-01','2025-01-31','Active'),(2,4,'Monthly','2024-01-01','2024-01-31','Active'),(3,4,'Monthly','2024-04-01','2024-05-31','Active'),(4,5,'Monthly','2023-01-01','2024-06-30','Active'),(5,5,'Annual','2024-01-01','2024-12-31','Active'),(8,2,'Annual','2023-01-01','2023-12-31','Active'),(10,2,'Annual','2024-01-01','2024-12-31','Active'),(15,1,'Annual','2024-03-14','2025-04-18','Active'),(16,6,'Annual','2024-04-20','2025-04-20','Active'),(17,7,'Annual','2024-04-20','2025-04-20','Active'),(18,9,'Annual','2024-04-21','2025-04-21','Active'),(19,11,'Annual','2024-04-22','2025-04-22','Active'),(20,13,'Annual','2024-04-22','2025-04-22','Active'),(21,16,'Monthly','2024-01-01','2025-01-31','Active');
INSERT INTO `bookings` VALUES (2,1,NULL,2,NULL,'Lesson','Booked',0),(3,1,NULL,3,NULL,'Lesson','Booked',0),(4,1,2,NULL,NULL,'Workshop','Cancelled',0),(5,1,NULL,NULL,NULL,'Workshop','Booked',0),(6,1,NULL,4,NULL,'Lesson','Cancelled',0),(7,1,NULL,1,NULL,'Lesson','Cancelled',0),(8,1,NULL,NULL,NULL,'Workshop','Booked',0),(9,1,NULL,NULL,NULL,'Lesson','Booked',0),(10,1,15,NULL,NULL,'Workshop','Booked',0),(11,1,12,NULL,NULL,'Workshop','Booked',0),(12,1,NULL,NULL,NULL,'Workshop','Booked',0),(13,1,NULL,7,NULL,'Lesson','Booked',0),(14,1,NULL,NULL,1,'Lesson','Cancelled',0),(15,1,NULL,NULL,1,'Lesson','Cancelled',0),(16,1,NULL,NULL,1,'Lesson','Booked',0),(17,1,15,NULL,NULL,'Workshop','Booked',0),(18,1,NULL,NULL,2,'Lesson','Booked',0),(19,7,NULL,9,NULL,'Lesson','Booked',0),(20,7,NULL,NULL,NULL,'Workshop','Booked',0),(21,7,22,NULL,NULL,'Workshop','Booked',0),(22,13,NULL,NULL,NULL,'Workshop','Booked',0);
