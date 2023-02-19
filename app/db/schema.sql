-- drop schema if exists `folderbe`;
CREATE schema if not exists `folderbe`;
use folderbe;


CREATE TABLE if not exists `User` (
  `id` varchar(30) primary key,
  `name` varchar(20) not null,
  `img` text,
  `email` varchar(30) unique,
  `refresh_token` text
);

CREATE TABLE if not exists `Folder` (
  `id` int primary key auto_increment,
  `name` varchar(20) not null,
  `user_id` varchar(30) not null
  );

CREATE TABLE if not exists `Channel` (
  `id` varchar(200) primary key,
  `playlist_id` varchar(200),
  `icon_img` text,
  `name` varchar(50) not null
);

CREATE TABLE if not exists `Folder_Channel` (
`channel_id` varchar(200) not null,
`folder_id` int not null,
primary key (`channel_id`, `folder_id`)
);


CREATE TABLE if not exists `User_Channel` (
  `user_id` varchar(30) not null,
  `channel_id` varchar(200) not null,
  primary key (`user_id`, `channel_id`)
);