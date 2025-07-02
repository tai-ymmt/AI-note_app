CREATE DATABASE IF NOT EXISTS ai_note;

CREATE TABLE IF NOT EXISTS users(
    num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id varchar(20) NOT NULL UNIQUE KEY,
    password varchar(255) NOT NULL,
    ai_level_flag INT(1) NOT NULL DEFAULT 1,
    ai_answer_flag INT(1) NOT NULL,
    mode_flag INT(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS notes(
    num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_num int NOT NULL,
    title varchar(20) NOT NULL,
    content text,
    update_time DATETIME NOT NULL,

    FOREIGN KEY (user_num) REFERENCES users(num)
);