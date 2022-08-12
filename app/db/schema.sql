CREATE schema if not exists `folderbe`;
use folderbe;


CREATE TABLE if not exists `User` (
  `id` int primary key auto_increment,
  `name` varchar(20) not null,
  `img` text,
  `email` varchar(30) unique,
  `refresh_token` text
);

CREATE TABLE if not exists `Folder` (
  `id` int primary key auto_increment,
  `name` varchar(20) not null,
  `user_id` int not null,
  FOREIGN KEY (`user_id`) REFERENCES `User`(`id`)
  );

CREATE TABLE if not exists `Channel` (
  `id` varchar(200) primary key,
  `playlist_id` varchar(200),
  `icon_img` text,
  `name` varchar(50) not null
);

CREATE TABLE if not exists `Folder_Channel` (
`id` int primary key,
`channel_id` varchar(200) not null,
`folder_id` int not null,
FOREIGN KEY (`channel_id`) REFERENCES `Channel`(`id`),
FOREIGN KEY (`folder_id`) REFERENCES `Folder`(`id`)
);

CREATE TABLE if not exists 'User_Channel' (
  `id` int primary key,
  `user_id` int not null,
  `channel_id` varchar(200) not null,
  foreign key (`user_id`) REFERENCES `User`(`id`),
  foreign key (`channel_id`) REFERENCES `Channel`(`id`)
)