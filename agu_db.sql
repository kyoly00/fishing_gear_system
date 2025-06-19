-- 1. 외래키 체크 일시 해제
SET FOREIGN_KEY_CHECKS = 0;

-- 2. 데이터베이스 생성
DROP DATABASE IF EXISTS agu_db;
CREATE DATABASE agu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE agu_db;

-- 3. 테이블 생성 (의존성 없는 테이블부터)
-- admin (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `admin_id` int NOT NULL,
  `admin_pw` varchar(45) DEFAULT NULL,
  `admin_area` varchar(45) DEFAULT NULL,
  `admin_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- retrieval_boat (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `retrieval_boat`;
CREATE TABLE `retrieval_boat` (
  `boat_id` int NOT NULL,
  `retrieval_company` varchar(45) NOT NULL,
  `company_adrress` varchar(25) NOT NULL,
  `boat_weight` int NOT NULL,
  `boat_ph` varchar(20) NOT NULL,
  `off_date_start` datetime DEFAULT NULL,
  `off_date_end` datetime DEFAULT NULL,
  PRIMARY KEY (`boat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- seller (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `seller`;
CREATE TABLE `seller` (
  `seller_id` varchar(45) NOT NULL,
  `seller_name` varchar(45) NOT NULL,
  `seller_ph` varchar(45) NOT NULL,
  `address` varchar(45) NOT NULL,
  PRIMARY KEY (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- buyer (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `buyer`;
CREATE TABLE `buyer` (
  `buyer_id` int NOT NULL,
  `buyer_name` varchar(45) NOT NULL,
  `buyer_ph` varchar(20) NOT NULL,
  `boat_name` varchar(45) NOT NULL,
  `boat_weight` float NOT NULL,
  PRIMARY KEY (`buyer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- django_content_type (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_permission (django_content_type에 의존)
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_group (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_user (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- assignment (admin, retrieval_boat에 의존)
DROP TABLE IF EXISTS `assignment`;
CREATE TABLE `assignment` (
  `Assignment_id` int NOT NULL,
  `as_admin_id` int NOT NULL,
  `as_boat_id` int NOT NULL,
  PRIMARY KEY (`Assignment_id`),
  KEY `as_admin_id_idx` (`as_admin_id`),
  KEY `as_boat_id_idx` (`as_boat_id`),
  CONSTRAINT `as_admin_id` FOREIGN KEY (`as_admin_id`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `as_boat_id` FOREIGN KEY (`as_boat_id`) REFERENCES `retrieval_boat` (`boat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- fishing_activity (buyer에 의존)
DROP TABLE IF EXISTS `fishing_activity`;
CREATE TABLE `fishing_activity` (
  `fa_number` int NOT NULL,
  `fa_buyer_id` int NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `cast_latitude` decimal(9,6) NOT NULL,
  `cast_longitude` decimal(9,6) NOT NULL,
  `haul_latitude` decimal(9,6) DEFAULT NULL,
  `haul_longitude` decimal(9,6) DEFAULT NULL,
  PRIMARY KEY (`fa_number`),
  KEY `buyer_id_idx` (`fa_buyer_id`),
  CONSTRAINT `fa_buyer_id` FOREIGN KEY (`fa_buyer_id`) REFERENCES `buyer` (`buyer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- fishing_gear (buyer, seller에 의존)
DROP TABLE IF EXISTS `fishing_gear`;
CREATE TABLE `fishing_gear` (
  `gear_id` varchar(20) NOT NULL,
  `seller_id` varchar(45) NOT NULL,
  `buyer_id` int NOT NULL,
  `type` varchar(45) NOT NULL,
  `price` int NOT NULL,
  `buy_date` datetime NOT NULL,
  PRIMARY KEY (`gear_id`),
  KEY `buyer_id_idx` (`buyer_id`),
  KEY `seller_id_idx` (`seller_id`),
  CONSTRAINT `buyer_id` FOREIGN KEY (`buyer_id`) REFERENCES `buyer` (`buyer_id`),
  CONSTRAINT `seller_id` FOREIGN KEY (`seller_id`) REFERENCES `seller` (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- gear_info (fishing_gear에 의존)
DROP TABLE IF EXISTS `gear_info`;
CREATE TABLE `gear_info` (
  `gear_id` varchar(20) NOT NULL,
  `gear_length` int NOT NULL,
  `gear_weight` int NOT NULL,
  `gear_depth` int NOT NULL,
  `gear_material` varchar(45) NOT NULL,
  PRIMARY KEY (`gear_id`),
  CONSTRAINT `gear_id` FOREIGN KEY (`gear_id`) REFERENCES `fishing_gear` (`gear_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- losting_gear (admin, fishing_activity에 의존)
DROP TABLE IF EXISTS `losting_gear`;
CREATE TABLE `losting_gear` (
  `report_id` int NOT NULL,
  `lg_buyer_id` int NOT NULL,
  `lg_admin_id` int NOT NULL,
  `cast_latitude` decimal(9,6) NOT NULL,
  `cast_longitude` decimal(9,6) NOT NULL,
  `cast_time` datetime NOT NULL,
  `report_time` datetime NOT NULL,
  PRIMARY KEY (`report_id`),
  KEY `lg_buyer_id_idx` (`lg_buyer_id`),
  KEY `admin_id` (`lg_admin_id`),
  CONSTRAINT `lg_admin_id` FOREIGN KEY (`lg_admin_id`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `lg_buyer_id` FOREIGN KEY (`lg_buyer_id`) REFERENCES `fishing_activity` (`fa_buyer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_group_permissions (auth_group, auth_permission에 의존)
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_user_groups (auth_user, auth_group에 의존)
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_user_user_permissions (auth_user, auth_permission에 의존)
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- django_admin_log (auth_user, django_content_type에 의존)
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- django_migrations (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT null,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- django_session (아무 테이블에도 의존하지 않음)
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4. 데이터 삽입 (의존성 없는 테이블부터)
-- admin
INSERT INTO `admin` VALUES 
(20001641,'africa4023!','고성군','노성민'),
(20071168,'xmvmlp652$','전라남도 여수시 여서1로 107','손진영'),
(20083144,'mlsdtl047*','전라남도 여수시 여서1로 107','김진천'),
(20083149,'melodic6807!','고흥군','나는야킹왕짱'),
(20090224,'yllnaq968#','부산광역시 동구 충장대로 351','박진건'),
(20114563,'vybllm191*','전라남도 여수시 강남로 20','노혜령'),
(20125456,'ndjujc305%','부산광역시 동구 충장대로 351','진수진'),
(20135648,'gkuglq344&','부산광역시 기장군 기장읍 기장해안로 216','성민주'),
(20194478,'qqexbo541^','전라남도 목포시 산정동 1483','차범수'),
(20200456,'dniviw134!','전라남도 목포시 해안로 148번길14','최영자'),
(20210468,'biqymm734!','전라남도 목포시 통일대로 130','김선후');

-- retrieval_boat
INSERT INTO `retrieval_boat` VALUES 
(156,'(유)동부환경','전라남도 여수시 웅천로 171',15,'061-656-5566','2025-05-11 00:00:00','2025-05-15 00:00:00'),
(158,'자유환경산업','부산광역시 사하구 승학로 76',10,'051-736-1122','2025-05-19 00:00:00','2025-05-23 00:00:00'),
(192,'(유)중앙환경건설','전라남도 여수시 신기남길 40',7,'061-650-1122','2025-05-25 00:00:00','2025-05-30 00:00:00'),
(209,'(주)태승','전라남도 여수시 돌산읍 향일암로 238',9,'061-662-9900','2025-05-17 00:00:00','2025-05-23 00:00:00'),
(305,'여순환경','전라남도 목포시 용당2길 5',11,'061-278-3456','2025-05-12 00:00:00','2025-05-30 00:00:00'),
(374,'(유)금강환경','부산광역시 연제구 월드컵대로 344',9,'051-733-9988','2025-05-25 00:00:00','2025-05-27 00:00:00'),
(382,'정일환경','전라남도 여수시 봉산남4길 22',10,'061-659-7788','2025-05-03 00:00:00','2025-05-16 00:00:00'),
(489,'(유)여천위생공사','전라남도 목포시 평화로 105',8,'061-277-9988','2025-05-7 00:00:00','2025-05-18 00:00:00'),
(490,'(유)조은환경','부산광역시 남구 용호로 148',8,'051-728-7890','2025-05-11 00:00:00','2025-05-16 00:00:00'),
(534,'(주)그린환경','부산광역시 해운대구 센텀동로 45',11,'051-740-1234','2025-05-27 00:00:00','2025-05-31 00:00:0'),
(621,'(주)녹색환경산업','부산광역시 중구 광복로 37',12,'051-724-3456','2025-05-3 00:00:00','2025-05-06 00:00:00'),
(673,'(유)덕산기업','전라남도 목포시 삼학로 92',12,'061-260-7890','2025-05-17 00:00:00','2025-05-25 00:00:00'),
(741,'(유)유성환경','전라남도 목포시 상동 829-3',10,'061-270-1234','2025-05-5 00:00:00','2025-05-19 00:00:00'),
(768,'(유)대한환경','부산광역시 수영구 광안해변로 219',13,'051-752-5678','2025-05-20 00:00:00','2025-05-28 00:00:00'),
(847,'(유)시민환경','전라남도 여수시 문수로 47',12,'061-653-3344','2025-05-7 00:00:0','2025-05-16 00:00:00'),
(928,'(주)청해이엔티','전라남도 목포시 하당로 230',9,'061-275-5678','2025-05-13 00:00:0','2025-05-25 00:00:00');

-- seller
INSERT INTO `seller` VALUES 
('aod340','오인섭','010-8557-2735','경남 남해군 미조면 미조로 89'),
('cka705','최동식','010-6587-7049','경남 남해군 설천면 설천로 78'),
('dqt880','김순이','010-9879-8554','경남 남해군 창선면 지족로 134'),
('emp873','장명숙','010-5795-7014','경남 남해군 남면 당항로 75'),
('epe997','이옥자','010-8613-6556','경남 남해군 삼동면 지족로 788'),
('evi268','한복희','010-6247-4466','경남 남해군 고현면 공룡로 67'),
('grj753','유숙자','010-4575-7505','경남 남해군 상주면 해변로 90'),
('hgj926','조종환','010-4621-4100','경남 남해군 고현면 고현로 321'),
('ikj082','송병구','010-2750-8316','경남 남해군 남면 남서로 202'),
('krs052','박병철','010-1918-9686','경남 남해군 삼동면 동부대로 1234'),
('lso137','윤태석','010-6253-6502','경남 남해군 서면 서상로 147'),
('lye068','정춘자','010-8301-5831','경남 남해군 남해읍 선소로 305'),
('mru843','이명호','010-7158-8701','경남 남해군 이동면 남해대로 456'),
('njq818','박말순','010-6999-8568','경남 남해군 이동면 석현로 22'),
('nko583','최영자','010-1863-7885','경남 남해군 설천면 진목로 41'),
('obj148','조분이','010-2309-5681','경남 남해군 미조면 포구로 121'),
('ojk622','한창수','010-9209-9972','경남 남해군 상주면 상주로 56'),
('reb923','김영수','010-4931-2477','경남 남해군 남해읍 망운로 15'),
('uef779','정상길','010-2739-3231','경남 남해군 창선면 창선로 910'),
('yre910','오순덕','010-6846-4552','경남 남해군 서면 사촌로 232');

-- buyer
INSERT INTO `buyer` VALUES 
(200050,'정영수','010-8540-6580','남해희망98선',9.7),
(200051,'정성호','010-2239-9077','남해한빛79선',13),
(200052,'이병호','010-4142-6642','남해금빛82선',14.4),
(200053,'임영희','010-2717-4567','남해해명선',6),
(200054,'장용준','010-5292-1623','남해희망38선',6.8),
(200055,'이병호','010-2811-9617','남해한빛선',6.4),
(200056,'임철수','010-8420-4071','남해해송39선',14.1),
(200057,'정도현','010-5908-8374','남해청춘100선',5.9),
(200058,'임도현','010-4314-1489','남해한빛48선',6.9),
(200059,'이민정','010-8260-9171','남해은빛선',10.6),
(200060,'임정숙','010-1211-3815','남해청춘11선',6.9),
(200061,'김민정','010-3063-5267','남해금빛선',14.3),
(200062,'장혜진','010-3783-7110','남해명진선',9.1),
(200063,'정성호','010-8881-4839','남해해돋이선',11.4),
(200064,'정진수','010-9323-4266','남해한빛90선',12.7),
(200065,'임정숙','010-1536-5207','남해청솔선',8.9),
(200066,'윤미영','010-8785-4333','남해은파선',14.2),
(200067,'정은주','010-4092-3912','남해한울선',10.9),
(200068,'김기석','010-6168-7139','남해청춘23선',5.3),
(200069,'김순자','010-8813-9688','남해누리봄선',11.4),
(200070,'조경자','010-8866-2531','남해한빛33선',12.9),
(200150,'박지현','010-1246-3836','남해희망42선',14.5),
(200151,'최철수','010-8250-2544','남해풍요선',9.8),
(200152,'강용준','010-8414-3165','남해해금선',7.6),
(200153,'최진수','010-9998-6602','남해희망46선',9.2),
(200154,'김혜진','010-6656-9168','남해청춘1선',14.7),
(200155,'윤은주','010-5706-8006','남해청춘선',5.2),
(200156,'박영수','010-9248-8988','남해청춘7선',5.4),
(200157,'강혜진','010-2783-1725','남해해송70선',14.4),
(200158,'임영수','010-5439-5540','남해누리선',5.2),
(200159,'김용준','010-4518-4276','남해청춘25선',7.3),
(200160,'강지현','010-3891-6153','남해백호선',7.8),
(200161,'강정숙','010-9983-9200','남해청명선',7.6),
(200162,'임진수','010-4394-5357','남해미래선',6), -- 오타 수정 필요: 괄호와 콤마, 따옴표 확인
(200163,'임명훈','010-8952-6190','남해광명선',6.5),
(200164,'강철수','010-3021-8689','남해솔빛선',10.2),
(200165,'박기석','010-3272-9404','남해희망35선',13.8),
(200166,'이민수','010-2335-6969','남해남풍선',6.1),
(200167,'강성호','010-4397-1370','남해해송선',10.5),
(200168,'정성호','010-8169-9673','남해한빛63선',8.4),
(200169,'강민수','010-1411-8766','남해금강선',14.8), -- 오타 수정 필요: 따옴표, 콤마 확인
(200170,'윤혜진','010-5497-3120','남해청춘15선',5.1),
(200250,'조영수','010-8954-6386','남해해바라기선',10.7),
(200251,'강민정','010-6676-1576','남해해송66선',6.7),
(200252,'조도현','010-5844-9843','남해해송30선',11.7),
(200253,'윤병호','010-6406-5359','남해한빛24선',14.6),
(200254,'이지현','010-9226-5715','남해희망선',14.7),
(200255,'이기석','010-2766-1386','남해동백선',8.6),
(200256,'임기석','010-3003-4783','남해금빛29선',10.5),
(200257,'임지현','010-2524-9422','남해해송22선',8.9);

-- django_content_type
INSERT INTO `django_content_type` VALUES 
(1,'admin','logentry'),
(2,'auth','permission'),
(3,'auth','group'),
(4,'auth','user'),
(5,'contenttypes','contenttype'),
(6,'sessions','session'),
(7,'lists','fishinggear'),
(8,'lists','gearinfo');

-- auth_permission
INSERT INTO `auth_permission` VALUES 
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session');

-- assignment (admin, retrieval_boat 데이터가 먼저 들어가 있어야 함)
INSERT INTO `assignment` VALUES 
(1,20200456,928),
(2,20194478,673),
(3,20071168,382),
(4,20135648,374),
(5,20125456,158),
(6,20200456,305),
(7,20135648,847);

-- auth_user
INSERT INTO `auth_user` VALUES 
(1,'pbkdf2_sha256$870000$XBi6XZinIDhqsdlDtqL3Px$vJ4CZVq1FJbdhktl97QQQ7h+DwuOtw84WvS/pzBkyws=','2025-04-01 04:56:32.775221',1,'admin','','','melodic6807@naver.com',1,1,'2025-04-1 04:55:52.554555');

-- fishing_activity (buyer 데이터가 먼저 들어가 있어야 함)
INSERT INTO `fishing_activity` VALUES 
(1,200050,'2025-01-18 15:22:00','2025-01-18 21:22:00',34.806800,126.219700,34.802279,126.226617),
(2,200051,'2025-03-04 09:27:00','2025-03-05 12:48:00',34.749000,126.213700,NULL,NULL),
(3,200052,'2025-03-21 20:56:0','2025-03-22 01:56:00',34.856300,125.942700,34.850191,125.946314),
(4,200053,'2025-04-19 01:25:00','2025-04-19 06:25:00',34.493100,125.921100,34.497406,125.929127),
(5,200054,'2025-02-23 13:09:00','2025-02-24 09:30:00',34.351200,126.365000,NULL,NULL),
(6,200055,'2024-02-04 03:31:00','2024-02-05 01:27:00',34.263000,126.650000,NULL,NULL),
(7,200056,'2025-03-14 04:08:00','2025-03-14 10:08:00',34.460200,125.924000,34.468269,125.923638),
(8,200057,'2025-04-15 01:03:00','2025-04-15 08:03:0',35.028100,125.969800,35.022663,125.972744),
(9,200058,'2025-03-3 04:41:00','2025-03-3 10:41:00',34.159800,126.073100,34.159548,126.082719),
(10,200059,'2025-01-24 05:43:00','2025-1-24 20:26:00',34.282300,126.430600,NULL,NULL),
(11,200060,'2025-03-16 08:23:00','2025-03-16 14:23:00',34.249700,126.288300,34.260026,126.293351),
(12,200061,'2025-01-12 06:35:00','2025-01-12 12:35:00',34.205840,126.123903,34.201125,126.129116),
(13,200062,'2025-02-02 06:22:00','2025-02-02 13:22:00',33.892521,127.492344,33.884480,127.497696),
(14,200063,'2025-04-24 14:2:00','2025-04-24 21:02:00',34.152707,127.469249,34.147635,127.479927),
(15,200064,'2025-04-20 10:17:00','2025-04-20 17:17:00',33.807923,127.915267,33.805055,127.917968),
(16,200065,'2025-03-19 17:04:00','2025-03-19 22:04:00',33.853116,127.252329,33.858724,127.249792),
(17,200066,'2024-03-18 09:14:00','2024-03-19 08:08:00',34.413800,126.726500,NULL,NULL),
(18,200067,'2025-03-21 18:50:00','2025-03-21 23:50:00',34.115241,127.079778,34.119677,127.075032),
(19,200068,'2025-01-16 20:58:00','2025-01-17 01:58:00',34.550900,128.052300,34.538850,128.053558),
(20,200069,'2024-03-02 15:31:00','2024-03-03 09:36:00',34.381700,127.360100,NULL,NULL),
(21,200070,'2025-03-19 02:47:00','2025-03-19 07:47:00',34.268710,127.092045,34.263783,127.081421),
(22,200150,'2025-01-21 03:23:00','2025-01-21 22:30:00',33.982917,128.053416,NULL,NULL),
(23,200151,'2025-03-16 00:04:00','2025-03-16 06:04:00',34.106539,126.842709,34.112286,126.839341),
(24,200152,'2025-03-02 16:14:00','2025-03-02 21:14:00',34.467287,127.685714,34.469799,127.685910),
(25,200153,'2025-02-13 19:42:00','2025-02-14 00:42:00',33.965679,126.989616,33.967370,126.995041),
(26,200154,'2025-03-6 13:18:00','2025-03-6 20:18:00',34.388275,128.140907,34.396875,128.133321),
(27,200155,'2025-03-6 13:49:00','2025-03-7 09:16:00',34.827000,128.835500,NULL,NULL),
(28,200156,'2025-04-02 18:32:00','2025-04-03 00:32:00',34.796000,129.056300,34.806615,129.050974),
(29,200157,'2025-04-20 09:23:00','2025-04-20 14:23:00',34.659600,128.648700,34.660688,128.659319),
(30,200158,'2025-01-22 17:18:00','2025-01-22 23:18:00',34.676600,128.480800,34.675659,128.473303),
(31,200159,'2025-01-08 17:11:00','2025-01-08 23:11:00',35.002400,128.549500,35.006394,128.557930),
(32,200160,'2025-03-7 13:59:0','2025-03-7 19:59:00',34.715600,128.316800,34.704286,128.318714),
(33,200161,'2025-01-7 06:09:00','2025-01-8 02:08:00',34.573300,128.575700,NULL,NULL),
(34,200162,'2025-03-21 21:09:00','2025-03-22 02:09:00',35.341600,129.421700,35.339830,129.410710),
(35,200163,'2025-01-11 03:35:00','2025-01-11 10:35:00',35.262500,129.359200,5.258707,129.351710),
(36,200164,'2025-01-10 21:59:00','2025-01-11 13:16:00',35.094500,129.129900,NULL,NULL),
(37,200165,'2025-03-25 07:10:00','2025-03-25 12:10:00',34.709900,128.377600,34.716959,128.384846),
(38,200166,'2025-02-8 23:29:00','2025-02-9 04:29:00',34.594400,128.450900,34.602966,128.450399);

-- fishing_gear (buyer, seller 데이터가 먼저 들어가 있어야 함)
INSERT INTO `fishing_gear` VALUES 
('02w555160','obj148',200155,'자망',255500,'2024-09-21 00:35:12'),
('04x255412','reb923',200252,'통발',585000,'2024-09-04 22:41:44'),
('04x378544','ikj082',200063,'통발',715500,'2024-09-01 17:26:14'),
('10c300684','krs052',200060,'통발',472500,'2024-09-24 14:37:17'),
('10h346138','hgj926',200257,'자망',496000,'2024-09-09 00:48:51'),
('11q766761','cka705',200165,'통발',254000,'2024-09-08 05:44:27'),
('14r587705','uef779',200166,'자망',318500,'2024-09-25 10:17:09'),
('17o828970','obj148',200256,'자망',461500,'2024-09-05 6:48:21'),
('17v306487','lye068',200060,'자망',655500,'2024-09-29 03:05:24'),
('20u067685','dqt880',200151,'자망',508500,'2024-09-18 03:22:54'),
('21d831133','ikj082',200067,'자망',495500,'2024-09-03 11:38:16'),
('21e771097','nko583',200163,'자망',728500,'2024-09-19 1:46:29'),
('25n902269','krs052',200059,'자망',417500,'2024-09-14 17:07:59'),
('30b710849','aod340',200055,'자망',261500,'2024-09-02 12:05:35'),
('30q572408','cka705',200052,'통발',746500,'2024-09-28 09:53:40'),
('34t893223','grj753',200255,'통발',388000,'2024-09-17 19:56:55'),
('36f165289','epe997',200059,'자망',535500,'2024-09-22 11:36:12'),
('41z949070','yre910',200253,'자망',305000,'2024-09-30 22:04:02'),
('42i253284','evi268',200067,'자망',408000,'2024-09-26 21:14:49'),
('44j837798','cka705',200168,'자망',645000,'2024-09-10 09:05:54'),
('45t227491','nko583',200162,'자망',504000,'2024-10-08 20:44:35'),
('46c830772','njq818',200164,'자망',304000,'2024-10-28 7:43:20'),
('48e901771','lso137',200064,'통발',668000,'2024-10-04 01:14:52'),
('49t063769','mru843',200251,'자망',589500,'2024-10-13 01:51:20'),
('50u817537','njq818',200053,'통발',682500,'2024-10-09 12:17:04'),
('54n907961','uef779',200061,'자망',548500,'2024-10-15 06:58:36'),
('56o940976','dqt880',200167,'자망',600000,'2024-10-21 22:20:13'),
('57o720724','hgj926',200161,'자망',502000,'2024-10-12 20:31:25'),
('58n417805','krs052',200160,'통발',575000,'2024-10-06 20:29:09'),
('58n668395','ojk622',200054,'자망',395000,'2024-10-24 08:08:15'),
('59t104762','aod340',200057,'통발',533500,'2024-10-22 23:35:34'),
('60b087480','emp873',200051,'자망',603500,'2024-10-07 08:47:37'),
('60j120134','yre910',200254,'자망',736500,'2024-10-27 13:57:37'), -- 오타 수정 필요: 따옴표, 콤마 확인
('60w115253','cka705',200056,'자망',340000,'2024-10-03 12:23:14'),
('63c201401','reb923',200054,'자망',276500,'2024-10-23 04:32:31'),
('64e318208','grj753',200058,'자망',400500,'2024-10-31 02:48:03'),
('65m886241','hgj926',200156,'통발',703500,'2024-10-18 03:09:40'), -- 오타 수정 필요: 따옴표, 콤마 확인
('65v805637','aod340',200065,'통발',644000,'2024-10-16 05:50:43'),
('68d568913','grj753',200069,'자망',332000,'2024-10-20 13:38:04'),
('68i965198','ojk622',200069,'자망',729500,'2024-10-05 12:24:38'),
('69e068429','lye068',200169,'통발',379000,'2024-11-15 05:29:00'),
('72f529856','aod340',200152,'자망',291500,'2024-11-17 23:56:46'),
('74d905026','evi268',200158,'자망',557000,'2024-11-09 08:32:48'),
('74g684223','uef779',200052,'통발',664500,'2024-11-18 05:32:58'),
('74t927260','lso137',200056,'자망',595000,'2024-11-01 03:55:40'),
('76f028389','epe997',200063,'통발',259000,'2024-11-22 09:53:40'),
('77r557218','lso137',200053,'자망',563000,'2024-11-24 16:38:12'),
('77t043317','mru843',200070,'자망',309500,'2024-11-04 04:23:48'),
('77u991144','yre910',200068,'자망',523500,'2024-11-25 05:34:49'),
('79l755401','dqt880',200066,'자망',729000,'2024-11-27 16:58:00'),
('80z522293','emp873',200058,'자망',403500,'2024-11-28 19:20:31'),
('83s949914','reb923',200150,'자망',599000,'2024-11-11 00:07:59'),
('85d587344','mru843',200250,'자망',386000,'2024-11-23 11:56:53'),
('85j482464','mru843',200051,'자망',597000,'2024-11-10 09:15:03'),
('85y800144','reb923',200157,'통발',339000,'2024-11-14 07:56:36'),
('87n311377','njq818',200064,'통발',431000,'2024-12-31 19:27:13'),
('90j060868','obj148',200050,'통발',647500,'2024-12-03 17:48:46'),
('90o550504','krs052',200065,'자망',590000,'2024-12-30 22:12:45'),
('93w428632','evi268',200062,'통발',676500,'2024-12-24 09:25:42'),
('94p464483','uef779',200050,'통발',316000,'2024-12-16 20:23:28'),
('95l725657','ojk622',200057,'통발',612500,'2024-12-29 16:28:07'),
('95r165285','epe997',200066,'자망',271000,'2024-12-25 07:14:4'),
('96t747754','ojk622',200062,'통발',629500,'2024-12-18 10:01:37'),
('97o007400','hgj926',200068,'통발',625000,'2024-12-05 17:14:37'),
('97q049522','nko583',200154,'통발',548500,'2024-12-23 07:00:04'),
('97t159421','ikj082',200153,'자망',317000,'2024-12-27 22:40:03'),
('97v800164','emp873',200159,'자망',506500,'2024-12-28 07:04:57'),
('98m303238','ikj082',200055,'자망',331500,'2024-12-06 01:55:21'),
('98m998312','lso137',200061,'통발',618500,'2024-12-09 02:32:15'),
('98r785472','lye068',200170,'통발',677000,'2024-12-17 08:42:31');

-- gear_info (fishing_gear 데이터가 먼저 들어가 있어야 함)
INSERT INTO `gear_info` VALUES 
('02w555160',511,409,5,'Synthetic Fiber'),
('04x255412',1170,936,7,'PE'),
('04x378544',1431,1145,9,'Nylon'),
('10c300684',945,756,7,'Synthetic Fiber'),
('10h346138',992,794,7,'PP'),
('11q766761',508,406,5,'PE'),
('14r587705',637,510,5,'Nylon'),
('17o828970',923,738,7,'Synthetic Fiber'),
('17v306487',1311,1049,9,'PP'),
('20u067685',1017,814,7,'Nylon'),
('21d831133',991,793,7,'Synthetic Fiber'),
('21e771097',1457,1166,9,'PE'),
('25n902269',835,668,7,'Nylon'),
('30b710849',523,418,5,'Nylon'),
('30q572408',1493,1194,9,'PE'),
('34t893223',776,621,5,'PP'),
('36f165289',1071,857,7,'PE'),
('41z949070',610,488,5,'Synthetic Fiber'),
('42i253284',816,653,7,'PE'),
('44j837798',1290,1032,9,'PE'),
('45t227491',1008,806,7,'PE'),
('46c830772',608,486,5,'PP'),
('48e901771',1336,1069,9,'PP'),
('49t063769',1179,943,7,'PP'),
('50u817537',1365,1092,9,'PE'),
('54n907961',1097,878,7,'PE'),
('56o940976',1200,960,9,'Nylon'),
('57o720724',1004,803,7,'Nylon'),
('58n417805',1150,920,7,'PE'),
('58n668395',790,632,5,'Nylon'),
('59t104762',1067,854,7,'PP'),
('60b087480',1207,966,9,'Synthetic Fiber'),
('60j120134',1473,1178,9,'PP'),
('60w115253',680,544,5,'Nylon'),
('63c201401',553,442,5,'Nylon'),
('64e318208',801,641,7,'Synthetic Fiber'),
('65m886241',1407,1126,9,'PP'),
('65v805637',1288,1030,9,'PP'),
('68d568913',664,531,5,'PE'),
('68i965198',1459,1167,9,'Synthetic Fiber'),
('69e068429',758,606,5,'Synthetic Fiber'),
('72f529856',583,466,5,'PE'),
('74d905026',1114,891,7,'PE'),
('74g684223',1329,1063,9,'Synthetic Fiber'),
('74t927260',1190,952,7,'PE'),
('76f028389',518,414,5,'PE'),
('77r557218',1126,901,7,'PP'),
('77t043317',619,495,5,'Nylon'),
('77u991144',1047,838,7,'PP'),
('79l755401',1458,1166,9,'PP'),
('80z522293',807,646,7,'PE'),
('83s949914',1198,958,7,'Synthetic Fiber'),
('85d587344',772,618,5,'PE'),
('85j482464',1194,955,7,'Nylon'),
('85y800144',678,542,5,'Nylon'),
('87n311377',862,690,7,'PE'),
('90j060868',1295,1036,9,'PE'),
('90o550504',1180,944,7,'PP'),
('93w428632',1353,1082,9,'Synthetic Fiber'),
('94p464483',632,506,5,'Nylon'),
('95l725657',1225,980,9,'Synthetic Fiber'),
('95r165285',542,434,5,'PE'),
('96t747754',1259,1007,9,'Nylon'),
('97o007400',1250,1000,9,'PP'),
('97q049522',1097,878,7,'Synthetic Fiber'),
('97t159421',634,507,5,'Nylon'),
('97v800164',1013,810,7,'Synthetic Fiber'),
('98m303238',663,530,5,'PP'),
('98m998312',1237,990,9,'PP'),
('98r785472',1354,1083,9,'PP');

-- losting_gear (admin, fishing_activity 데이터가 먼저 들어가 있어야 함)
INSERT INTO `losting_gear` VALUES 
(1,200051,20200456,34.749000,126.213700,'2025-03-04 12:19:00','2025-03-05 01:13:00'),
(2,200054,20200456,34.351200,126.365000,'2025-02-23 15:39:00','2025-02-24 10:00:00'),
(3,200055,20210468,34.263000,126.650000,'2024-02-04 6:20:00','2024-02-05 01:41:00'),
(4,200059,20071168,34.282300,126.430600,'2025-01-24 08:41:00','2025-01-24 20:46:00'),
(5,200066,20083144,34.413800,126.726500,'2024-03-18 11:41:00','2024-03-19 08:24:00'),
(6,200069,20114563,34.381700,127.360100,'2024-03-02 17:49:00','2024-03-03 10:36:00'),
(7,200150,20135648,33.982917,128.053416,'2025-01-21 05:56:00','2025-01-21 22:35:00'),
(8,200155,20135648,34.827000,128.835500,'2025-03-06 16:01:00','2025-03-07 09:41:00'),
(9,200161,20125456,34.573300,128.575700,'2025-1-7 08:28:00','2025-01-08 02:25:00'),
(10,200164,20194478,35.094500,129.129900,'2025-01-11 00:50:00','2025-01-11 13:31:00');

-- django_migrations
INSERT INTO `django_migrations` VALUES 
(1,'contenttypes','0001_initial','2025-03-28 04:48:55.291972'),
(2,'auth','0001_initial','2025-03-28 04:48:55.929162'),
(3,'admin','0001_initial','2025-3-28 04:48:56.076775'),
(4,'admin','0002_logentry_remove_auto_add','2025-03-28 04:48:56.084927'),
(5,'admin','0003_logentry_add_action_flag_choices','2025-03-28 04:48:56.094421'),
(6,'contenttypes','0002_remove_content_type_name','2025-03-28 04:48:56.218946'),
(7,'auth','0002_alter_permission_name_max_length','2025-03-28 04:48:56.301358'),
(8,'auth','0003_alter_user_email_max_length','2025-03-28 04:48:56.323608'), -- 오타 수정 필요: 따옴표, 콤마 확인
(9,'auth','0004_alter_user_username_opts','2025-03-28 04:48:56.332559'),
(10,'auth','0005_alter_user_last_login_null','2025-03-28 04:48:56.398147'),
(11,'auth','0006_require_contenttypes_0002','2025-03-28 04:48:56.400470'),
(12,'auth','0007_alter_validators_add_error_messages','2025-03-28 04:48:56.407589'),
(13,'auth','0008_alter_user_username_max_length','2025-3-28 04:48:56.490512'),
(14,'auth','0009_alter_user_last_name_max_length','2025-03-28 04:48:56.586270'),
(15,'auth','0010_alter_group_name_max_length','2025-03-28 04:48:56.611302'),
(16,'auth','0011_update_proxy_permissions','2025-03-28 04:48:56.621451'),
(17,'auth','0012_alter_user_first_name_max_length','2025-03-28 04:48:56.697289'),
(18,'sessions','0001_initial','2025-03-28 04:48:56.738338');

-- django_session
INSERT INTO `django_session` VALUES 
('3m4np9k4bn6ytjtkprhe9a1cdyjmq4fh','.eJxVjL0OgzAQg98lM4py-SEJY_e-ARJKLkehLUECMlV990LFwmJL_mx_WEjTmLsxsUYK4RRoXZ1ZDhOxhrUlkBZtQY96191YxbpQtqErKy3_KYNrFgO-KB8gPUN-zBznvC1j5EeFn3Tl9znR-3Z2LwdDWId9jTUa5URSqMBoSGCskbGmCI6U9RiV82BSlFbWUfZaRFIqoEHhbQ-g2fcHsUBH0A:1tzTfs:FONWX6f13wNZqv_o9CDfgV8sXmIs2KKH3USx3fYA_r8','2025-04-15 04:56:32.778021'),
('6a9v230j63jne79uklwhp5uoyfzjpikw','eyJhZG1pbl9pZCI6MjAwMDE2NDEsImFkbWluX25hbWUiOiJcdWIxNzhcdWMxMzFcdWJiZmMifQ:1uCvKa:hvFTWFbFvhlbcHhm19Lqj09PKxRNld1AFridwie5CYg','2025-05-22 07:06:08.985047');

-- 5. 외래키 체크 복구
SET FOREIGN_KEY_CHECKS = 1;
