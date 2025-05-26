create database ailike;
use ailike;

SHOW TABLES IN ailike;

select * from data_user;
select * from data_topic;
select * from data_post_topics;
select * from data_userembedding;
select * from data_postlike;
select * from data_usermatch;

ALTER TABLE data_notification AUTO_INCREMENT = 3;
ALTER TABLE data_post AUTO_INCREMENT = 1;
ALTER TABLE data_postlike AUTO_INCREMENT = 1;
ALTER TABLE data_friendrequest AUTO_INCREMENT = 1;
ALTER TABLE data_user AUTO_INCREMENT = 2;

DELETE FROM data_user WHERE id BETWEEN 2 AND 3;

DELETE FROM data_friendrequest WHERE from_user_id BETWEEN 2 AND 6 OR to_user_id BETWEEN 2 AND 6;
DELETE FROM data_post WHERE author_id BETWEEN 1 AND 100;
DELETE FROM data_postlike WHERE user_id BETWEEN 1 AND 208;
DELETE FROM data_notification WHERE user_id BETWEEN 2 AND 6;
