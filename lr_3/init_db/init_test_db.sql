CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) UNIQUE NOT NULL,
    last_name VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_first_name ON users(first_name);
CREATE INDEX IF NOT EXISTS idx_last_name ON users(last_name);

CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    creator_id INT REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_name_creator UNIQUE (name, creator_id)
);

CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    folder_id INT REFERENCES folders(id) ON DELETE CASCADE,
    CONSTRAINT unique_name_folder UNIQUE (name, folder_id)
);
CREATE INDEX IF NOT EXISTS idx_filename ON files(name);

INSERT INTO users (username, first_name, last_name, email, password) VALUES 
('admin', 'admin', 'admin', 'admin@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS')
ON CONFLICT DO NOTHING;

INSERT INTO users (username, first_name, last_name, email, password) VALUES 
('user1', 'John', 'Doe', 'john.doe@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user2', 'Jane', 'Smith', 'jane.smith@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user3', 'Alice', 'Johnson', 'alice.johnson@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user4', 'Bob', 'Brown', 'bob.brown@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user5', 'Charlie', 'Williams', 'charlie.williams@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user6', 'David', 'Jones', 'david.jones@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user7', 'Eve', 'Miller', 'eve.miller@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user8', 'Frank', 'Taylor', 'frank.taylor@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user9', 'Grace', 'Anderson', 'grace.anderson@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user10', 'Henry', 'Thomas', 'henry.thomas@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user11', 'Ivy', 'Jackson', 'ivy.jackson@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user12', 'Jack', 'White', 'jack.white@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user13', 'Kelly', 'Harris', 'kelly.harris@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user14', 'Leo', 'Martin', 'leo.martin@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user15', 'Megan', 'Clark', 'megan.clark@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user16', 'Nina', 'Rodriguez', 'nina.rodriguez@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user17', 'Oscar', 'Martinez', 'oscar.martinez@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user18', 'Paul', 'Davis', 'paul.davis@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user19', 'Quincy', 'Lopez', 'quincy.lopez@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS'),
('user20', 'Rachel', 'Gonzalez', 'rachel.gonzalez@example.com', '$2b$12$DFKswboZoqOSSKQn78yZMe87qgAMHsUZ.Zvqs98MIqbraZgfZeTdS')
ON CONFLICT DO NOTHING;

INSERT INTO folders (name, creator_id) VALUES
('Documents', 1), 
('Photos', 1), 
('Videos', 1),
('Work', 2),
('Travel', 2),
('Personal', 3),
('Music', 4),
('Projects', 5),
('School', 6),
('Recipes', 7),
('Books', 8),
('Art', 9),
('Games', 10),
('Health', 11),
('Shopping', 12),
('Bills', 13),
('Family', 14),
('Finance', 15),
('Vacation', 16),
('Workouts', 17)
ON CONFLICT DO NOTHING;

INSERT INTO files (name, folder_id) VALUES
('resume.pdf', 1),
('photo1.jpg', 2),
('video1.mp4', 3),
('project_report.docx', 4),
('vacation_pictures.zip', 5),
('personal_notes.txt', 6),
('music_playlist.m3u', 7),
('project_presentation.pptx', 8),
('school_schedule.pdf', 9),
('recipe1.docx', 10),
('novel.txt', 11),
('art_gallery.jpg', 12),
('game_scores.csv', 13),
('health_checkup.pdf', 14),
('shopping_list.xlsx', 15),
('electric_bill.pdf', 16),
('family_tree.jpg', 17),
('finance_plan.xlsx', 18),
('vacation_plans.docx', 19),
('workout_schedule.xlsx', 20)
ON CONFLICT DO NOTHING;