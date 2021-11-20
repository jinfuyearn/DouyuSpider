CREATE DATABASE IF NOT EXISTS`douyu_download`;
USE `douyu_download`;

DROP TABLE IF EXISTS `douyu_show`;

CREATE TABLE `douyu_show` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `up_id` VARCHAR(255) DEFAULT NULL,
  `show_id` VARCHAR(255) DEFAULT NULL,
  `start_time` VARCHAR(255) DEFAULT NULL,
  `title` VARCHAR(255) DEFAULT NULL,
  `cut_num` INT(11) DEFAULT NULL,
  `fan_num` INT(11) DEFAULT NULL,
  `re_num` INT(11) DEFAULT NULL,
  `show_page` INT(11) DEFAULT NULL,
  `show_limit` INT(11) DEFAULT NULL,
  `start_timestamp` TIMESTAMP NULL DEFAULT NULL,
  `start_year` INT(11) DEFAULT NULL,
  `start_month` INT(11) DEFAULT NULL,
  `start_day` INT(11) DEFAULT NULL,
  `is_reply_download` INT(11) DEFAULT NULL,
  `create_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=INNODB;

DROP TABLE IF EXISTS `douyu_video`;

CREATE TABLE `douyu_video` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `up_id` VARCHAR(255) DEFAULT NULL,
  `show_id` VARCHAR(255) DEFAULT NULL,
  `index_of_show` INT(11) DEFAULT NULL,
  `title` VARCHAR(255) DEFAULT NULL,
  `video_type` INT(11) DEFAULT NULL,
  `start_time` VARCHAR(255) DEFAULT NULL,
  `hash_id` VARCHAR(255) DEFAULT NULL,
  `video_str_duration` VARCHAR(255) DEFAULT NULL,
  `point_id` VARCHAR(255) DEFAULT NULL,
  `json` VARCHAR(2000) DEFAULT NULL,
  `video_page` INT(11) DEFAULT NULL,
  `video_limit` INT(11) DEFAULT NULL,
  `is_download` INT(11) DEFAULT NULL,
  `create_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=INNODB ;
