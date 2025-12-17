Create Schema IF NOT EXISTS mytau012;
USE mytau012 ;


CREATE TABLE Cloth (
    cloth_ID VARCHAR(50) PRIMARY KEY, 
    cloth_name VARCHAR(255) NOT NULL,
    is_campaigned BOOLEAN NOT NULL DEFAULT 0,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    path_image VARCHAR(255) ,
    cloth_description VARCHAR(255) 
);

CREATE TABLE User (
    email VARCHAR(255) PRIMARY KEY, 
    name VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    date_of_birth date NOT NULL,
    is_admin BOOL NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE Transaction (
    order_number INT AUTO_INCREMENT PRIMARY KEY, 
    email VARCHAR(255) , 
    date_time DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (email) REFERENCES User(email)
);

CREATE TABLE Transaction_details (
    quantity INT NOT NULL,
    cloth_ID VARCHAR(50) NOT NULL,
    order_number INT AUTO_INCREMENT,
    PRIMARY KEY (cloth_ID, order_number), 
    FOREIGN KEY (cloth_ID) REFERENCES Cloth(cloth_ID),
    FOREIGN KEY (order_number) REFERENCES Transaction(order_number)
);


CREATE TABLE Inventory_update (
	available_quantity INT NOT NULL, 
	email VARCHAR(255) ,
	cloth_ID VARCHAR(50),
	FOREIGN KEY (email) REFERENCES User(email),
    FOREIGN KEY (cloth_ID) REFERENCES Cloth(cloth_ID)
    );
    
CREATE TABLE Add_new_item (
    cloth_ID INT AUTO_INCREMENT PRIMARY KEY, -- ההלהחליט האם נשאר INT או VARCHER
    email VARCHAR(255) NOT NULL, 
    cloth_name VARCHAR(255) NOT NULL, 
    is_campaigned BOOLEAN NOT NULL DEFAULT 0, 
    quantity INT NOT NULL, 
    price DECIMAL(10, 2) NOT NULL, 
    path_image VARCHAR(255), 
    cloth_description VARCHAR(255),
    FOREIGN KEY (email) REFERENCES User(email)
);


INSERT INTO User (email, name, gender, faculty, date_of_birth, is_admin, password)
VALUES
('Dan@tau.ac.il', 'Dan', 'Male', 'Engineering', '1997-01-01', TRUE, 'AdminPass1'),
('Yael@tau.ac.il', 'Yael', 'Female', 'Management', '1995-05-01', TRUE, 'AdminPass2');



INSERT INTO Cloth (cloth_ID,cloth_name,is_campaigned,quantity,price,path_image,cloth_description)
VALUES
('1', 'MOM Jeans', TRUE, 10, 50.00, 'images/PANTS1.png', 'Trendy mom-fit jeans, perfect for casual outings.'),
('2', 'Elegant Jeans', FALSE, 5, 30.00, 'images/PANTS2.png', 'Sophisticated jeans for a polished look.'),
('3', 'Daily Jeans', TRUE, 5, 70.00, 'images/PANTS3.png', 'Comfortable everyday jeans for any occasion.'),
('4', 'Long Sleeve Shirt', FALSE, 8, 40.00, 'images/SHIRT1.png', 'A flowy and stylish green shirt, great for layering.'),
('5', 'T-Shirt with Prints', TRUE, 12, 20.00, 'images/SHIRT2.png', 'Bright and fun yellow T-shirt with eye-catching prints.'),
('6', 'Button Shirt', TRUE, 6, 60.00, 'images/SHIRT3.png', 'Classic white button shirt, suitable for any occasion.');



