CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    creator_id INT,
    CONSTRAINT unique_name_creator UNIQUE (name, creator_id)
);
CREATE INDEX IF NOT EXISTS idx_creator ON folders(creator_id);

CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    folder_id INT REFERENCES folders(id) ON DELETE CASCADE,
    CONSTRAINT unique_name_folder UNIQUE (name, folder_id)
);
CREATE INDEX IF NOT EXISTS idx_filename ON files(name);

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