# CLINICAL- MANAGMENT SYSTEM 

This project is a robust digital platform designed to streamline and automate workflows within a medical clinic. It centralizes administrative tasks, facilitating communication between medical staff and patients while providing an organized structure for managing appointments, patient databases, and medical specializations. The system addresses common operational challenges such as scheduling conflicts and fragmented information across departments. 
## Key Features
* Centralized Patient Management: A unified database utilizing CNP (Personal Numeric Code) for accurate patient identification and medical history tracking.
*  Automated Scheduling: A booking module that connects patients with specific doctors at precise times, effectively preventing scheduling conflicts.
*  Medical Staff Administration: A structured system to register doctors and classify them by specialization (e.g., Cardiology, Neurology, Pediatrics).
*  Business Intelligence & Reporting: Automated generation of professional reports in PDF, CSV, and JSON formats, including visual performance analytics.
*  Audit & Security: Advanced security features, including bcrypt password hashing, Fernet symmetric encryption for sensitive data, and comprehensive activity logging.
## Technologies Used:
* Backend: Python
* Web Framework: Flask
* Database: MariaDB (containerized via Docker)
* Infrastructure as Code: Docker Compose
* Data Analysis & Visualization: Matplotlib, ReportLab
* Security: cryptography (Fernet), bcrypt
* Environment Management: python-dotenv
## Technical Architecture:
* Orchestration: Microservices managed via docker-compose.yml ensure a deterministic and reproducible execution environment.
* Database Layer: A centralized db.py layer manages connections, executing secure, parameterized SQL queries to prevent SQL Injection vulnerabilities.
* Data Integrity: Enforced through foreign key constraints, triggers for validation (e.g., preventing negative invoice sums), and automated verification scripts (check_tables.py).
* Performance: Optimized via database indexing on frequently queried columns (e.g., CNP, Specialization).
