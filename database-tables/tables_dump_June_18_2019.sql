-- -------------------------------------------------------------
-- TablePlus 2.4(228)
--
-- https://tableplus.com/
--
-- Database: postgres
-- Generation Time: 2019-06-18 08:50:59.8410
-- -------------------------------------------------------------


-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."inventory" (
    "item" text NOT NULL,
    "count" int8 NOT NULL DEFAULT 0,
    "id" int8 NOT NULL,
    PRIMARY KEY ("id")
);

-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS menu_id_seq;

-- Table Definition
CREATE TABLE "public"."menu" (
    "id" int4 NOT NULL DEFAULT nextval('menu_id_seq'::regclass),
    "pizza" text NOT NULL,
    "recipe" json NOT NULL,
    PRIMARY KEY ("id")
);

-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."orders" (
    "id" int8 NOT NULL,
    "p_status" text NOT NULL DEFAULT 'TO DO'::text,
    PRIMARY KEY ("id")
);

INSERT INTO "public"."inventory" ("item", "count", "id") VALUES ('Cheese', '89', '0'),
('Pepperoni', '0', '1'),
('Sausage', '5', '2'),
('Sauce', '89', '3');

INSERT INTO "public"."menu" ("id", "pizza", "recipe") VALUES ('2', 'Pepperoni', '{ "recipe": [ "Cheese" , "Sauce", "Pepperoni"]}'),
('3', 'Cheese', '{ "recipe": [ "Cheese" , "Sauce"]}'),
('4', 'Sausage', '{ "recipe": [ "Cheese" , "Sauce", "Sausage"]}');

INSERT INTO "public"."orders" ("id", "p_status") VALUES ('1', 'Done'),
('2', 'Done'),
('3', 'Done'),
('4', 'Done'),
('23', 'Done'),
('500', 'IN PROGRESS');


