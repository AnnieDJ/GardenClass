# COMP639 Studio Project 
- Group AS (Schwifty) 

## Group Member:
- Sunlanglang Su (Lana) - 1157037 
- Yu Nie (Neal) - 1159131 
- Xiaojia Dou (Annie) - 1156500 
- Vivien Kuan - 1155767 
- Gui Yan (Kassi)  - 1156524

## Project Name
- Rākau Gardening Society Management System

## Python Anywhere
- PA Link: https://schwifty.pythonanywhere.com/

## Project Overview
- Purpose: To digitalise and optimise the Rākau Gardening Society's operations, enhancing the experience for New Zealand native plant enthusiasts through automated member management, booking systems, and financial oversight.
- Scope: The project encompasses the development of a web application to manage memberships, workshops, lessons, instructor schedules, payments, and news dissemination, ensuring a comprehensive solution for both administrative staff and society members.

## Technology Stack
- Frontend: HTML, CSS, JavaScript 
- Backend: Flask (Python) 
- Database: MySQL
- Security: Implement password hashing and salting 
- Deployment: PythonAnywhere

## Methodology
- Adopting the Scrum framework with scheduled sprints, this approach emphasises collaboration, regular progress reviews, and adaptability to changes. The project will utilise sprint planning, daily stand-ups, sprint reviews, and retrospectives to ensure alignment with user needs and project goals.

## Database Design
- The model includes tables for 'member', 'instructor', and 'manager', each holding specific attributes such as names, contact information, and relevant roles within the society.

- The 'user' table simplifies login and centralizes user management by grouping all user types under role-based access, ensuring clear separation of roles for security and functionality.

- The 'workshops' ,'lessons' and 'one_on_one_lessons' tables are managed through their respective tables, which include detailed scheduling and financial information. 

- The 'bookings' table for all 'workshops' ,'lessons' and 'one_on_one_lessons' tables are consolidated in the 'bookings' table, which simplifies the management of user reservations.

- The 'payments' table underpins the financial transactions, linking to members and tracking the status of each payment. 

- The 'bank_info' table facilitates financial transactions by connecting to members and monitoring the status of bank transactions.

- The 'new' table serves as a communication tool within the society, linked to the managers who are the primary authors of updates and announcements. 

- The "subscriptions" table stores information about user subscriptions within the society.

- The database is designed with normalisation principles to minimise redundancy and ensure data integrity. It features a role-based access control system, facilitating appropriate permissions and security.

## Project Framework
- Homepage: The main page where you see general information and options to navigate further.
- Login: The page where you enter your username and password to access your account.
- Register: The page where you create a new account by providing your information such as username, password, and email etc.
- Member dashboard：
- - Manage own profile
- - Update own password
- - View the workshop schedule
- - Book a workshop and pay the fee
- - Book an individual one-on-one lesson with an instructor and pay the fee
- - Manage bookings 
- - Manage membership subscription details
- - View news
- Instructor dashboard:
- - Manager own profile
- - Update own password
- - View workshop schedule
- - Manage own one-on-one lesson and group lesson schedule
- - Record attendance at workshops and one-on-one lessons
- - View news
- Manager dashboard:
- - Manager own profile
- - Manager instructor and member profile
- - Update own password
- - Manage the workshop schedule
- - Manage own one-on-one lesson and group lesson schedule
- - Record attendance at workshops and one-on-one lessons
- - Manage news

## System Login Information
- Manager Account 
- - username: jane_smith
- - password: John1234

- Instructor Account
- - username: john_instructor
- - password: John1234

- Member Account
- - username: john_doe
- - password: John1234



