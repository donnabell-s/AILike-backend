-- create database ailike;
use ailike;
SHOW VARIABLES LIKE 'character_set%';

-- SHOW TABLES IN ailike;

select * from data_user;
select * from data_friendrequest;
select * from data_post;
select * from data_postlike;
select * from data_notification;

ALTER TABLE data_notification AUTO_INCREMENT = 3;
ALTER TABLE data_post AUTO_INCREMENT = 1;
ALTER TABLE data_postlike AUTO_INCREMENT = 1;
ALTER TABLE data_friendrequest AUTO_INCREMENT = 1;
ALTER TABLE data_user AUTO_INCREMENT = 2;
