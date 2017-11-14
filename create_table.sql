SET NAMES utf8; -- set client connection
alter Table `weiwen_article` DEFAULT CHARACTER  set utf8; # 设置字符编码
-- ----------------------------
--  Table structure for `wechat_user_info`
-- ----------------------------
DROP TABLE IF EXISTS `wechat_user_info`;
CREATE TABLE `wechat_user_info` (
  `wechat_id` varchar(20) NOT NULL,
  `wechat_name` varchar(50) DEFAULT NULL,
  `authentication` varchar(200) DEFAULT NULL,
  `introduction` varchar(500) DEFAULT NULL,
  `headimage` varchar(100) DEFAULT NULL,
  `qrcode` varchar(200) DEFAULT NULL,
  `newrank_uuid` varchar(50) DEFAULT NULL,
  `qbjm_wxname` varchar(50) DEFAULT NULL
  -- UNIQUE KEY `wechat_id` (`wechat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `weiwen_article`
-- ----------------------------
DROP TABLE IF EXISTS `weiwen_article`;
CREATE TABLE `weiwen_article` (
  `title` varchar(50) CHARACTER SET utf8 NOT NULL,
  `digest` varchar(200) DEFAULT NULL,
  `likenum` int(11) DEFAULT NULL,
  `readnum` int(11) DEFAULT NULL,
  `cover` varchar(200) DEFAULT NULL,
  `content_url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
