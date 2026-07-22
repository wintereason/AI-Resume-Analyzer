CREATE TABLE job_roles (
    job_role_id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(150) NOT NULL UNIQUE,
    category VARCHAR(100),
    experience_level ENUM('Fresher','Junior','Mid-Level','Senior') DEFAULT 'Fresher',
    description TEXT,
    average_salary_india DECIMAL(10,2),
    average_salary_us DECIMAL(10,2),
    demand_level ENUM('Low','Medium','High') DEFAULT 'High',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);