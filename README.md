# Online MCQ Test Management System

A web-based MCQ test management system built as part of the Database Systems Lab (CSS 2212) mini project at Manipal Institute of Technology.

# About

This system allows administrators to create and manage MCQ tests, and students to attempt them within a time limit. Scores are automatically calculated using a MySQL AFTER INSERT trigger.

# Features
- Admin can add, view and delete tests and questions
- Students can attempt timed tests with auto submission
- Automatic score calculation using MySQL AFTER INSERT trigger
- Student performance report generated via stored procedure
- Analytics dashboard with complex SQL queries
- Question-wise result breakdown showing correct and wrong answers

# Tech Stack
- **Database:** MySQL 8.0
- **Backend:** Python 3.x with Flask
- **Frontend:** HTML5, CSS3, Jinja2
- **DB Connector:** mysql-connector-python

# Database Design
- 7 normalized tables in Third Normal Form (3NF)
- AFTER INSERT trigger for automatic score calculation
- Stored procedure for student performance reports
- Complex SQL queries with JOINs, GROUP BY and subqueries

