
CREATE TABLE user_model (
    id INT NOT NULL AUTO_INCREMENT, 
    first_name VARCHAR(255) NOT NULL, 
    last_name VARCHAR(255) NOT NULL, 
    parent1_id INT, 
    parent2_id INT, 
    PRIMARY KEY (id)
);
