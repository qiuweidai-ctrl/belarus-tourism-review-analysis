-- Belarus Tourism System - MySQL Database Schema
-- 19 tables with rigorous relational design

-- ============================================================
-- 1. users: 用户表
-- ============================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'User ID',
    `username`        VARCHAR(50) NOT NULL COMMENT 'Unique username',
    `email`           VARCHAR(120) NOT NULL COMMENT 'Unique email address',
    `password_hash`   VARCHAR(256) NOT NULL COMMENT 'Bcrypt password hash',
    `nickname`        VARCHAR(50) DEFAULT NULL COMMENT 'Display nickname',
    `avatar_url`      VARCHAR(500) DEFAULT NULL COMMENT 'Avatar image URL',
    `role`            ENUM('user', 'admin', 'moderator') NOT NULL DEFAULT 'user' COMMENT 'User role',
    `status`          ENUM('active', 'banned', 'inactive') NOT NULL DEFAULT 'active' COMMENT 'Account status',
    `bio`             TEXT DEFAULT NULL COMMENT 'User biography',
    `last_login_at`   DATETIME DEFAULT NULL COMMENT 'Last login timestamp',
    `last_login_ip`   VARCHAR(45) DEFAULT NULL COMMENT 'Last login IP address',
    `email_verified`  TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Email verified flag',
    `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    INDEX `idx_role` (`role`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User accounts';

-- ============================================================
-- 2. attractions: 景点表
-- ============================================================
DROP TABLE IF EXISTS `attractions`;
CREATE TABLE `attractions` (
    `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Attraction ID',
    `name`             VARCHAR(200) NOT NULL COMMENT 'Attraction name',
    `name_en`          VARCHAR(200) DEFAULT NULL COMMENT 'English name',
    `name_be`          VARCHAR(200) DEFAULT NULL COMMENT 'Belarusian name',
    `description`      TEXT DEFAULT NULL COMMENT 'Description in English',
    `description_en`   TEXT DEFAULT NULL COMMENT 'English description',
    `short_desc`      VARCHAR(500) DEFAULT NULL COMMENT 'Short summary',
    `location`         VARCHAR(300) NOT NULL COMMENT 'Detailed location',
    `city`             VARCHAR(100) DEFAULT NULL COMMENT 'City',
    `region`           VARCHAR(100) DEFAULT NULL COMMENT 'Region/Oblast',
    `latitude`         DECIMAL(10, 7) DEFAULT NULL COMMENT 'GPS latitude',
    `longitude`        DECIMAL(10, 7) DEFAULT NULL COMMENT 'GPS longitude',
    `category`         ENUM('castle', 'nature', 'museum', 'memorial', 'church', 'palace', 'park', 'architecture', 'other') NOT NULL DEFAULT 'other' COMMENT 'Attraction category',
    `suitable_season`  VARCHAR(100) DEFAULT NULL COMMENT 'Best visiting season',
    `opening_hours`   VARCHAR(200) DEFAULT NULL COMMENT 'Opening hours',
    `ticket_price`    DECIMAL(10, 2) DEFAULT NULL COMMENT 'Ticket price (BYN)',
    `image_url`       VARCHAR(500) DEFAULT NULL COMMENT 'Main image URL',
    `images_json`     JSON DEFAULT NULL COMMENT 'Array of additional image URLs',
    `avg_rating`       DECIMAL(3, 2) NOT NULL DEFAULT 0.00 COMMENT 'Average rating (1-5)',
    `total_reviews`    INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Total review count',
    `sentiment_score`  DECIMAL(4, 3) DEFAULT 0.000 COMMENT 'Avg sentiment score (-1 to 1)',
    `sentiment_pos_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Positive review count',
    `sentiment_neg_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Negative review count',
    `wishlist_count`  INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Times added to wishlist',
    `view_count`      INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Page view count',
    `is_featured`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Featured attraction flag',
    `is_verified`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Verified by admin flag',
    `created_by`      BIGINT UNSIGNED DEFAULT NULL COMMENT 'Creator user ID',
    `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    INDEX `idx_category` (`category`),
    INDEX `idx_region` (`region`),
    INDEX `idx_avg_rating` (`avg_rating`),
    INDEX `idx_is_featured` (`is_featured`),
    INDEX `idx_created_at` (`created_at`),
    CONSTRAINT `fk_attractions_created_by` FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tourist attractions';

-- ============================================================
-- 3. reviews: 游记/评论表
-- ============================================================
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews` (
    `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Review ID',
    `user_id`          BIGINT UNSIGNED NOT NULL COMMENT 'Author user ID',
    `attraction_id`    BIGINT UNSIGNED NOT NULL COMMENT 'Reviewed attraction ID',
    `title`            VARCHAR(200) DEFAULT NULL COMMENT 'Review title',
    `content`          TEXT NOT NULL COMMENT 'Review text content',
    `rating`           TINYINT UNSIGNED NOT NULL COMMENT 'Star rating (1-5)',
    `travel_type`      ENUM('solo', 'couple', 'family', 'friends', 'business') DEFAULT NULL COMMENT 'Travel type',
    `travel_date`      DATE DEFAULT NULL COMMENT 'Date of visit',
    `travel_month`     VARCHAR(20) DEFAULT NULL COMMENT 'Month of visit',
    `helpful_count`    INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Helpful votes count',
    `reply_count`      INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Owner replies count',
    `sentiment_label`  ENUM('positive', 'neutral', 'negative') DEFAULT NULL COMMENT 'AI sentiment label',
    `sentiment_score`  DECIMAL(4, 3) DEFAULT 0.000 COMMENT 'AI sentiment score (-1 to 1)',
    `ai_processed`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'AI analysis completed flag',
    `status`           ENUM('published', 'pending', 'hidden', 'deleted') NOT NULL DEFAULT 'published' COMMENT 'Review status',
    `ip_address`       VARCHAR(45) DEFAULT NULL COMMENT 'Submitter IP',
    `created_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `updated_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    `deleted_at`       DATETIME DEFAULT NULL COMMENT 'Soft delete time',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_attraction_id` (`attraction_id`),
    INDEX `idx_rating` (`rating`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_sentiment` (`sentiment_label`),
    UNIQUE KEY `uk_user_attraction` (`user_id`, `attraction_id`),
    CONSTRAINT `fk_reviews_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reviews_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `chk_rating` CHECK (`rating` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Travel reviews/diaries';

-- ============================================================
-- 4. ratings: 用户评分表（独立于评论，支持多次更新）
-- ============================================================
DROP TABLE IF EXISTS `ratings`;
CREATE TABLE `ratings` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Rating ID',
    `user_id`       BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
    `attraction_id` BIGINT UNSIGNED NOT NULL COMMENT 'Attraction ID',
    `score`         TINYINT UNSIGNED NOT NULL COMMENT 'Rating score (1-5)',
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Rating time',
    `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    UNIQUE KEY `uk_user_attraction` (`user_id`, `attraction_id`),
    INDEX `idx_attraction_id` (`attraction_id`),
    CONSTRAINT `fk_ratings_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ratings_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `chk_score` CHECK (`score` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User ratings for attractions';

-- ============================================================
-- 5. review_replies: 评论回复表
-- ============================================================
DROP TABLE IF EXISTS `review_replies`;
CREATE TABLE `review_replies` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Reply ID',
    `review_id`  BIGINT UNSIGNED NOT NULL COMMENT 'Parent review ID',
    `user_id`    BIGINT UNSIGNED NOT NULL COMMENT 'Reply author user ID',
    `content`    TEXT NOT NULL COMMENT 'Reply content',
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Like count',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    `deleted_at` DATETIME DEFAULT NULL COMMENT 'Soft delete time',
    INDEX `idx_review_id` (`review_id`),
    INDEX `idx_user_id` (`user_id`),
    CONSTRAINT `fk_replies_review` FOREIGN KEY (`review_id`) REFERENCES `reviews`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_replies_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Owner replies to reviews';

-- ============================================================
-- 6. wishlists: 收藏/心愿单表
-- ============================================================
DROP TABLE IF EXISTS `wishlists`;
CREATE TABLE `wishlists` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Wishlist ID',
    `user_id`       BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
    `attraction_id` BIGINT UNSIGNED NOT NULL COMMENT 'Attraction ID',
    `note`          VARCHAR(500) DEFAULT NULL COMMENT 'Personal note',
    `priority`      TINYINT UNSIGNED NOT NULL DEFAULT 3 COMMENT 'Priority (1=high, 3=normal)',
    `visited`       TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Has visited flag',
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Added time',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_attraction_id` (`attraction_id`),
    UNIQUE KEY `uk_user_attraction` (`user_id`, `attraction_id`),
    CONSTRAINT `fk_wishlists_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_wishlists_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User wishlists/favorites';

-- ============================================================
-- 7. review_helpful_votes: 评论有用投票表
-- ============================================================
DROP TABLE IF EXISTS `review_helpful_votes`;
CREATE TABLE `review_helpful_votes` (
    `id`        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Vote ID',
    `review_id` BIGINT UNSIGNED NOT NULL COMMENT 'Review ID',
    `user_id`   BIGINT UNSIGNED NOT NULL COMMENT 'Voting user ID',
    `is_helpful` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Is helpful (1=yes, 0=no)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Vote time',
    UNIQUE KEY `uk_review_user` (`review_id`, `user_id`),
    INDEX `idx_review_id` (`review_id`),
    CONSTRAINT `fk_votes_review` FOREIGN KEY (`review_id`) REFERENCES `reviews`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_votes_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Helpful votes on reviews';

-- ============================================================
-- 8. login_tokens: 登录令牌表
-- ============================================================
DROP TABLE IF EXISTS `login_tokens`;
CREATE TABLE `login_tokens` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Token ID',
    `user_id`     BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
    `token`       VARCHAR(512) NOT NULL COMMENT 'JWT access token hash',
    `refresh_token` VARCHAR(512) DEFAULT NULL COMMENT 'Refresh token hash',
    `device_info` VARCHAR(200) DEFAULT NULL COMMENT 'Device/browser info',
    `ip_address`  VARCHAR(45) DEFAULT NULL COMMENT 'Login IP address',
    `expires_at`  DATETIME NOT NULL COMMENT 'Token expiration time',
    `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Login time',
    `revoked_at`  DATETIME DEFAULT NULL COMMENT 'Revocation time',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_token` (`token`(255)),
    INDEX `idx_expires_at` (`expires_at`),
    CONSTRAINT `fk_tokens_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Login session tokens';

-- ============================================================
-- 9. sentiment_analysis_log: 情感分析日志表
-- ============================================================
DROP TABLE IF EXISTS `sentiment_analysis_log`;
CREATE TABLE `sentiment_analysis_log` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Log ID',
    `review_id`      BIGINT UNSIGNED NOT NULL COMMENT 'Review ID',
    `content_hash`   VARCHAR(64) DEFAULT NULL COMMENT 'SHA256 hash of content (dedup)',
    `raw_response`   JSON DEFAULT NULL COMMENT 'Full API response',
    `sentiment_label` ENUM('positive', 'neutral', 'negative') NOT NULL COMMENT 'Classified label',
    `sentiment_score` DECIMAL(4, 3) NOT NULL COMMENT 'Sentiment score (-1 to 1)',
    `confidence`     DECIMAL(5, 4) DEFAULT NULL COMMENT 'Model confidence (0-1)',
    `model_used`     VARCHAR(100) DEFAULT 'deepseek-chat' COMMENT 'AI model used',
    `processing_time_ms` INT UNSIGNED DEFAULT NULL COMMENT 'API processing time in ms',
    `api_cost`       DECIMAL(8, 4) DEFAULT NULL COMMENT 'API cost in USD',
    `status`         ENUM('success', 'failed', 'fallback') NOT NULL DEFAULT 'success' COMMENT 'Analysis status',
    `fallback_method` VARCHAR(50) DEFAULT NULL COMMENT 'Fallback method used if failed',
    `created_at`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Analysis time',
    INDEX `idx_review_id` (`review_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_sentiment_label` (`sentiment_label`),
    INDEX `idx_created_at` (`created_at`),
    UNIQUE KEY `uk_review_id` (`review_id`),
    CONSTRAINT `fk_sentiment_review` FOREIGN KEY (`review_id`) REFERENCES `reviews`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI sentiment analysis log';

-- ============================================================
-- 10. articles: Travel guides and blog posts
-- ============================================================
CREATE TABLE IF NOT EXISTS `articles` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `attraction_id` BIGINT UNSIGNED DEFAULT NULL,
    `title` VARCHAR(300) NOT NULL,
    `summary` VARCHAR(600) DEFAULT NULL,
    `content` TEXT NOT NULL,
    `cover_image_url` VARCHAR(500) DEFAULT NULL,
    `tags_json` JSON DEFAULT NULL,
    `view_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `comment_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `is_featured` TINYINT(1) NOT NULL DEFAULT 0,
    `is_published` TINYINT(1) NOT NULL DEFAULT 1,
    `status` VARCHAR(20) NOT NULL DEFAULT 'published',
    `ip_address` VARCHAR(45) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `published_at` DATETIME DEFAULT NULL,
    `deleted_at` DATETIME DEFAULT NULL,
    INDEX `idx_articles_user_id` (`user_id`),
    INDEX `idx_articles_attraction_id` (`attraction_id`),
    INDEX `idx_articles_status` (`status`),
    INDEX `idx_articles_created_at` (`created_at`),
    INDEX `idx_articles_is_featured` (`is_featured`),
    CONSTRAINT `fk_article_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_article_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Travel guides and blog posts';

-- ============================================================
-- 11. article_likes: Article like records
-- ============================================================
CREATE TABLE IF NOT EXISTS `article_likes` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `article_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_article_user_like` (`article_id`, `user_id`),
    INDEX `idx_likes_article_id` (`article_id`),
    CONSTRAINT `fk_like_article` FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Article like records';

-- ============================================================
-- 12. article_comments: Article comments
-- ============================================================
CREATE TABLE IF NOT EXISTS `article_comments` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `article_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `parent_id` BIGINT UNSIGNED DEFAULT NULL,
    `content` TEXT NOT NULL,
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    INDEX `idx_comments_article_id` (`article_id`),
    INDEX `idx_comments_user_id` (`user_id`),
    CONSTRAINT `fk_comment_article` FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Article comments';

-- ============================================================
-- 13. questions: Q&A questions per attraction
-- ============================================================
CREATE TABLE IF NOT EXISTS `questions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `attraction_id` BIGINT UNSIGNED NOT NULL,
    `title` VARCHAR(300) NOT NULL,
    `content` TEXT NOT NULL,
    `view_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `answer_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `upvote_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `has_accepted_answer` TINYINT(1) NOT NULL DEFAULT 0,
    `status` VARCHAR(20) NOT NULL DEFAULT 'published',
    `ip_address` VARCHAR(45) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    INDEX `idx_questions_user_id` (`user_id`),
    INDEX `idx_questions_attraction_id` (`attraction_id`),
    INDEX `idx_questions_status` (`status`),
    INDEX `idx_questions_created_at` (`created_at`),
    CONSTRAINT `fk_question_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_question_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Q&A questions for attractions';

-- ============================================================
-- 14. answers: Answers to questions
-- ============================================================
CREATE TABLE IF NOT EXISTS `answers` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `question_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `content` TEXT NOT NULL,
    `upvote_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `is_accepted` TINYINT(1) NOT NULL DEFAULT 0,
    `status` VARCHAR(20) NOT NULL DEFAULT 'published',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    INDEX `idx_answers_question_id` (`question_id`),
    INDEX `idx_answers_user_id` (`user_id`),
    INDEX `idx_answers_is_accepted` (`is_accepted`),
    CONSTRAINT `fk_answer_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_answer_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Answers to questions';

-- ============================================================
-- 15. question_upvotes: Question upvote records
-- ============================================================
CREATE TABLE IF NOT EXISTS `question_upvotes` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `question_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_question_user_upvote` (`question_id`, `user_id`),
    INDEX `idx_qup_question_id` (`question_id`),
    CONSTRAINT `fk_qup_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_qup_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Question upvote records';

-- ============================================================
-- 16. answer_upvotes: Answer upvote records
-- ============================================================
CREATE TABLE IF NOT EXISTS `answer_upvotes` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `answer_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_answer_user_upvote` (`answer_id`, `user_id`),
    INDEX `idx_aup_answer_id` (`answer_id`),
    CONSTRAINT `fk_aup_answer` FOREIGN KEY (`answer_id`) REFERENCES `answers`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_aup_author` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Answer upvote records';

-- ============================================================
-- 17. tags: Attraction and article tags
-- ============================================================
CREATE TABLE IF NOT EXISTS `tags` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `slug` VARCHAR(50) NOT NULL,
    `description` VARCHAR(300) DEFAULT NULL,
    `color` VARCHAR(20) DEFAULT '#1a5e63',
    `article_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `use_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_tag_name` (`name`),
    UNIQUE KEY `uk_tag_slug` (`slug`),
    INDEX `idx_tags_slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tags for attractions and articles';

-- ============================================================
-- 18. attraction_tags: Many-to-many relation between attractions and tags
-- ============================================================
CREATE TABLE IF NOT EXISTS `attraction_tags` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `attraction_id` BIGINT UNSIGNED NOT NULL,
    `tag_id` BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_attraction_tag` (`attraction_id`, `tag_id`),
    INDEX `idx_attag_attraction_id` (`attraction_id`),
    INDEX `idx_attag_tag_id` (`tag_id`),
    CONSTRAINT `fk_attag_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_attag_tag` FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Attraction-tag many-to-many relation';

-- ============================================================
-- 19. rating_dimensions: Multi-dimensional ratings
-- ============================================================
CREATE TABLE IF NOT EXISTS `rating_dimensions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `attraction_id` BIGINT UNSIGNED NOT NULL,
    `scenery` TINYINT UNSIGNED DEFAULT NULL,
    `service` TINYINT UNSIGNED DEFAULT NULL,
    `value` TINYINT UNSIGNED DEFAULT NULL,
    `facilities` TINYINT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_attraction_dimension` (`user_id`, `attraction_id`),
    INDEX `idx_dim_attraction_id` (`attraction_id`),
    CONSTRAINT `fk_dim_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dim_attraction` FOREIGN KEY (`attraction_id`) REFERENCES `attractions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Multi-dimensional ratings (scenery/service/value/facilities)';

SELECT 'All 19 tables created successfully!' AS Result;

