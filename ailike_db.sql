create database ailike;
use ailike;

SHOW TABLES IN ailike;

select * from data_user;
select * from data_friendrequest;
select * from data_post;
select * from data_topic;

ALTER TABLE data_post AUTO_INCREMENT = 1;
ALTER TABLE data_friendrequest AUTO_INCREMENT = 1;
ALTER TABLE data_topic AUTO_INCREMENT = 1;
ALTER TABLE data_user AUTO_INCREMENT = 2;
