CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    sub_category VARCHAR(100),
    description TEXT,
    difficulty ENUM('Beginner','Intermediate','Advanced') DEFAULT 'Beginner',
    demand_level ENUM('Low','Medium','High') DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);