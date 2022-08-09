DROP schema if exists `folderbe`;

CREATE schema `folderbe`;
use folderbe;

DROP TABLE if exists `User`;
DROP TABLE if exists `Folder`;
DROP TABLE if exists `Channel`;
DROP TABLE if exists `Folder_Channel`;

CREATE TABLE `User` (
  `id` int primary key,
  `img` text(100),
  `name` varchar(20) not null,
  `email` varchar(20),
  `access_token` text(100)
);

CREATE TABLE `Folder` (
  `id` int primary key,
  `name` varchar(20) not null,
  `user_id` int not null,
  FOREIGN KEY (`user_id`) REFERENCES `User`(`id`)
  );

CREATE TABLE `Channel` (
  `id` int primary key,
  `playlist_id` text(100),
  `icon_img` text(100),
  `name` text(40) not null
);

CREATE TABLE `Folder_Channel` (
`id` int primary key,
`channel_id` int not null,
`folder_id` int not null,
FOREIGN KEY (`channel_id`) REFERENCES `Channel`(`id`),
FOREIGN KEY (`folder_id`) REFERENCES `Folder`(`id`)
);

CREATE TABLE 'User_Channel' (
  `id` int primary key,
  `user_id` int not null,
  `channel_id` int not null,
  foreign key (`user_id`) REFERENCES `User`(`id`),
  foreign key (`channel_id`) REFERENCES `Channel`(`id`)
)