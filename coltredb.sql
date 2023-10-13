use `coltre`;

DROP TABLE IF EXISTS `blacklist`;
DROP TABLE IF EXISTS `repetitions_counter`;
DROP TABLE IF EXISTS `verification`;
DROP TABLE IF EXISTS `queue`;
DROP TABLE IF EXISTS `videomessage`;
DROP TABLE IF EXISTS `warning_counter`;
DROP TABLE IF EXISTS `warning`;
DROP TABLE IF EXISTS `transaction`;
DROP TABLE IF EXISTS `penalty`;
DROP TABLE IF EXISTS `exercise`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `group`;
DROP TABLE IF EXISTS `training_level`;

CREATE TABLE IF NOT EXISTS `training_level` (
  `training_level_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `training_level_name` varchar(50) NOT NULL,
  `description` varchar(1000) NOT NULL,
  `multiplier` double unsigned NOT NULL,
  PRIMARY KEY (`training_level_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `group` (
  `group_id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `created_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `user` (
  `user_id` bigint unsigned NOT NULL,
  `username` varchar(64) DEFAULT NULL,
  `first_name` varchar(96) DEFAULT NULL,
  `training_level_id` tinyint unsigned NOT NULL,
  `group_id` smallint unsigned NOT NULL,
  `timezone` tinyint NOT NULL,
  PRIMARY KEY (`user_id`),
  KEY `user-training_level` (`training_level_id`),
  KEY `user-group` (`group_id`),
  CONSTRAINT `user-group` FOREIGN KEY (`group_id`) REFERENCES `group` (`group_id`) ON UPDATE CASCADE,
  CONSTRAINT `user-training_level` FOREIGN KEY (`training_level_id`) REFERENCES `training_level` (`training_level_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `exercise` (
  `exercise_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `norm` tinyint unsigned NOT NULL,
  `unit` varchar(20) NOT NULL,
  PRIMARY KEY (`exercise_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `repetitions_counter` (
  `user_id` bigint unsigned NOT NULL,
  `current_user_date` date NOT NULL,
  `exercise_id` tinyint unsigned NOT NULL,
  `repetition_count` tinyint unsigned NOT NULL,
  PRIMARY KEY (`user_id`),
  KEY `repetitions_counter-exercise` (`exercise_id`),
  CONSTRAINT `repetitions_counter-exercise` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `repetitions_counter-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `videomessage` (
  `videomessage_id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `telegram_message_id` mediumint unsigned NOT NULL,
  `created_at` datetime NOT NULL,
  `exercise_id` tinyint unsigned NOT NULL,
  `exercise_count` tinyint unsigned NOT NULL,
  PRIMARY KEY (`videomessage_id`),
  KEY `videomessage-user` (`user_id`),
  KEY `videomessage-exercise` (`exercise_id`),
  CONSTRAINT `videomessage-exercise` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON UPDATE CASCADE,
  CONSTRAINT `videomessage-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `queue` (
  `queue_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `videomessage_id` int unsigned NOT NULL,
  `status` varchar(16) DEFAULT 'pending',
  `inspector_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`queue_id`),
  KEY `queue-videomessage` (`videomessage_id`),
  KEY `queue-user` (`inspector_id`),
  CONSTRAINT `queue-user` FOREIGN KEY (`inspector_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `queue-videomessage` FOREIGN KEY (`videomessage_id`) REFERENCES `videomessage` (`videomessage_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `verification` (
  `verification_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `inspector_id` bigint unsigned NOT NULL,
  `checked_user_id` bigint unsigned NOT NULL,
  `videomessage_id` int unsigned NOT NULL,
  `real_done_count` tinyint unsigned NOT NULL,
  `verified_at` datetime NOT NULL,
  PRIMARY KEY (`verification_id`),
  KEY `verification-inspector` (`inspector_id`),
  KEY `verification-checked_user` (`checked_user_id`),
  KEY `verification-videomessage` (`videomessage_id`),
  CONSTRAINT `verification-checked_user` FOREIGN KEY (`checked_user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `verification-inspector` FOREIGN KEY (`inspector_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `verification-videomessage` FOREIGN KEY (`videomessage_id`) REFERENCES `videomessage` (`videomessage_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `warning` (
  `warning_id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `warning_date` date NOT NULL,
  `exercise_id` tinyint unsigned NOT NULL,
  PRIMARY KEY (`warning_id`),
  KEY `warning-user` (`user_id`),
  KEY `warning-exercise` (`exercise_id`),
  CONSTRAINT `warning-exercise` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON UPDATE CASCADE,
  CONSTRAINT `warning-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `warning_counter` (
  `user_id` bigint unsigned NOT NULL,
  `warning_id` smallint unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`user_id`),
  KEY `warning_counter-warning` (`warning_id`),
  CONSTRAINT `warning_counter-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `warning_counter-warning` FOREIGN KEY (`warning_id`) REFERENCES `warning` (`warning_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `penalty` (
  `penalty_id` smallint unsigned NOT NULL,
  `type` varchar(16) NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `amount` tinyint unsigned NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `penalty_date` date NOT NULL,
  PRIMARY KEY (`penalty_id`),
  KEY `penalty-user` (`user_id`),
  CONSTRAINT `penalty-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `transaction` (
  `transaction_id` tinyint unsigned NOT NULL,
  `penalty_id` smallint unsigned NOT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `transaction-penalty` (`penalty_id`),
  CONSTRAINT `transaction-penalty` FOREIGN KEY (`penalty_id`) REFERENCES `penalty` (`penalty_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` bigint unsigned NOT NULL,
  `reason_description` text,
  `block_date` date NOT NULL,
  `unblock_date` date DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `blacklist-user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `exercise`(name, norm, unit) VALUES
	('Отжимания', 150, 'раз'),
	('Приседания', 220, 'раз'),
    ('Подтягивания', 65, 'раз'),
    ('Планка', 10, 'минут');