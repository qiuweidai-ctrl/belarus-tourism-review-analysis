/*
 Navicat Premium Data Transfer

 Source Server         : course
 Source Server Type    : MySQL
 Source Server Version : 80036
 Source Host           : localhost:3306
 Source Schema         : belarus_tourism

 Target Server Type    : MySQL
 Target Server Version : 80036
 File Encoding         : 65001

 Date: 06/07/2026 21:30:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for answer_upvotes
-- ----------------------------
DROP TABLE IF EXISTS `answer_upvotes`;
CREATE TABLE `answer_upvotes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `answer_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_answer_user_upvote`(`answer_id` ASC, `user_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_aup_answer_id`(`answer_id` ASC) USING BTREE,
  CONSTRAINT `answer_upvotes_ibfk_1` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `answer_upvotes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of answer_upvotes
-- ----------------------------

-- ----------------------------
-- Table structure for answers
-- ----------------------------
DROP TABLE IF EXISTS `answers`;
CREATE TABLE `answers`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `upvote_count` int NOT NULL,
  `is_accepted` tinyint(1) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_answers_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_answers_is_accepted`(`is_accepted` ASC) USING BTREE,
  INDEX `idx_answers_question_id`(`question_id` ASC) USING BTREE,
  CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `answers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of answers
-- ----------------------------
INSERT INTO `answers` VALUES (1, 1, 1, 'I would recommend late April to early June for the best weather and photos. The castle grounds are green and blooming, and summer crowds have not yet arrived. October is also beautiful for autumn foliage. Avoid July-August if you dislike crowds.', 5, 1, 'published', '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL);

-- ----------------------------
-- Table structure for article_comments
-- ----------------------------
DROP TABLE IF EXISTS `article_comments`;
CREATE TABLE `article_comments`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `article_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `parent_id` bigint NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `like_count` int NOT NULL,
  `created_at` datetime NOT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_comments_article_id`(`article_id` ASC) USING BTREE,
  INDEX `idx_comments_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `article_comments_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `article_comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of article_comments
-- ----------------------------
INSERT INTO `article_comments` VALUES (1, 6, 2, NULL, 'Great article, very helpful for my trip planning.', 0, '2026-07-01 18:21:21', NULL);
INSERT INTO `article_comments` VALUES (2, 7, 2, NULL, 'Loved the photography tips, going to try them next month.', 1, '2026-07-01 18:21:21', NULL);
INSERT INTO `article_comments` VALUES (3, 8, 2, NULL, 'Is the road to Braslav really that rough?', 1, '2026-07-01 18:21:21', NULL);
INSERT INTO `article_comments` VALUES (4, 9, 2, NULL, 'I went last summer and totally agree with point #3.', 4, '2026-07-01 18:21:21', NULL);

-- ----------------------------
-- Table structure for article_likes
-- ----------------------------
DROP TABLE IF EXISTS `article_likes`;
CREATE TABLE `article_likes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `article_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_article_user_like`(`article_id` ASC, `user_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_likes_article_id`(`article_id` ASC) USING BTREE,
  CONSTRAINT `article_likes_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `article_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of article_likes
-- ----------------------------
INSERT INTO `article_likes` VALUES (2, 6, 2, '2026-06-23 18:21:21');
INSERT INTO `article_likes` VALUES (3, 7, 2, '2026-06-16 18:21:21');
INSERT INTO `article_likes` VALUES (4, 8, 2, '2026-06-16 18:21:21');
INSERT INTO `article_likes` VALUES (5, 9, 2, '2026-06-26 18:21:21');
INSERT INTO `article_likes` VALUES (6, 11, 2, '2026-06-03 18:21:21');
INSERT INTO `article_likes` VALUES (7, 12, 2, '2026-06-11 18:21:21');
INSERT INTO `article_likes` VALUES (8, 1, 2, '2026-06-12 18:21:21');
INSERT INTO `article_likes` VALUES (9, 2, 2, '2026-06-25 18:21:21');

-- ----------------------------
-- Table structure for articles
-- ----------------------------
DROP TABLE IF EXISTS `articles`;
CREATE TABLE `articles`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NULL DEFAULT NULL,
  `title` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary` varchar(600) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cover_image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `tags_json` json NULL,
  `view_count` int NOT NULL,
  `like_count` int NOT NULL,
  `comment_count` int NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `is_published` tinyint(1) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `published_at` datetime NULL DEFAULT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_articles_is_featured`(`is_featured` ASC) USING BTREE,
  INDEX `idx_articles_attraction_id`(`attraction_id` ASC) USING BTREE,
  INDEX `idx_articles_status`(`status` ASC) USING BTREE,
  INDEX `idx_articles_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_articles_created_at`(`created_at` ASC) USING BTREE,
  CONSTRAINT `articles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `articles_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of articles
-- ----------------------------
INSERT INTO `articles` VALUES (1, 1, 1, 'A Complete Guide to Visiting Mir Castle Complex', 'Everything you need for a perfect day trip to Belarus most iconic UNESCO World Heritage Site.', 'Mir Castle Complex is one of the most impressive historical monuments in Belarus. Built in the late 16th century, this Gothic-Renaissance masterpiece stands as a testament to the rich cultural heritage of the Polish-Lithuanian Commonwealth.\n\nGetting There: The castle is about 120km from Minsk. Most convenient by car or organized tour. Public buses available from Minsk Central Bus Station.\n\nBest Time to Visit: Spring and autumn offer the most dramatic photos — blooming gardens in spring and golden foliage in autumn. Summer weekends can be crowded.\n\nInside the Castle: The museum features exhibitions on castle history, the Radziwill family, and medieval life. The restored chambers with original frescoes are not to be missed.\n\nPhotography Tips: The castle looks best in early morning or late afternoon light. The lake reflection makes for stunning photographs.', '/static/images/attractions/1.jpg', '[\"UNESCO World Heritage\", \"History\", \"Medieval\", \"Architecture\"]', 314, 45, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-06 13:01:44', NULL, NULL);
INSERT INTO `articles` VALUES (2, 1, 3, 'European Bison Encounter: Belovezhskaya Pushcha in One Day', 'How to make the most of a day trip to Europe last primeval forest and spot the majestic wisent.', 'Belovezhskaya Pushcha is one of those places that reminds you of how magnificent untouched nature can be. As the last primeval forest in Europe, it offers a window into what the continent looked like before human civilization reshaped it.\n\nThe main attraction is the European bison (wisent). These magnificent animals roam freely in the park, and with a bit of patience you can observe them from safe viewing platforms. The park is home to over 600 bison.\n\nWhat to See: Start at the Nature Museum, then take the forest train to the bison feeding areas. The ancient oak trees — some over 600 years old — are equally impressive. Don\'t miss the Tsars Oak.\n\nPractical Tips: Wear comfortable walking shoes. The forest can be muddy. Bring binoculars for bird watching — 253 species live here!', '/static/images/attractions/3.jpg', '[\"Nature\", \"UNESCO World Heritage\", \"Family Friendly\", \"Photography\"]', 245, 38, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (3, 1, 2, 'Nesvizh Castle: Walking Through the Radziwill Legacy', 'A detailed itinerary for exploring the most beautiful palace-park ensemble in Belarus.', 'Nesvizh Castle was the seat of the powerful Radziwill family for more than four centuries. Today it stands as a UNESCO World Heritage Site and is widely considered the most beautiful palace complex in Belarus.\n\nThe Tour: Begin at the Corpus Christi Church with its famous family crypt, then walk through the manicured park to the main palace. Inside, do not miss the gilded ballroom, the portrait gallery, and the chapel.\n\nGetting There: Nesvizh is about 150km southwest of Minsk. Regular buses and marshrutkas run from Minsk Central Bus Station. The journey takes roughly 2.5 hours.\n\nWhen to Visit: Late spring and early autumn are perfect. The park is in full bloom from May to June, and autumn colors peak in October.\n\nFamily Tip: Children love the knight-themed photo zones near the courtyard and the open park for picnics.', '/static/images/attractions/2.jpg', '[\"UNESCO World Heritage\", \"History\", \"Architecture\"]', 198, 27, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (4, 2, 11, 'Brest Fortress: A Pilgrimage of Memory', 'Why every visitor to Belarus should spend a full day at the symbol of Soviet wartime endurance.', 'Brest Fortress is more than a historical monument. It is a place of pilgrimage. On 22 June 1941, this 19th-century citadel became one of the first targets of Operation Barbarossa. The garrison held out for weeks against overwhelming force.\n\nThe Centrepiece: The colossal \"Courage\" sculpture — a concrete head emerging from a rock face — is one of the largest portrait sculptures in the world. Stand at its base and look up. It is overwhelming.\n\nMuseum Visit: The Defence of Brest Fortress Museum holds personal belongings, recovered weapons, photographs, and documents that bring the story to life. Plan at least two hours.\n\nThe Surrounding Complex: Walk the perimeter walls, the eternal flame courtyard, and the obelisk. Audio guides are available in English, Russian, and Belarusian.', '/static/images/attractions/11.jpg', '[\"History\", \"Memorial\", \"WWII\"]', 410, 56, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (5, 1, 28, 'Minsk City Guide: 72 Hours in the Belarusian Capital', 'A long-weekend itinerary covering architecture, museums, food, and nightlife in Minsk.', 'Minsk is one of the cleanest and most underrated capitals in Eastern Europe. Rebuilt almost entirely after WWII, the city blends Soviet monumental architecture with modern glass towers and an extensive green park system.\n\nDay 1 — Independence Avenue: Walk the 15km main boulevard from Victory Square south, stopping at Independence Square, the Government House, the GUM department store, and the Holy Trinity Cathedral in the Upper Town.\n\nDay 2 — Museums: Spend the morning at the Great Patriotic War Museum with its 8,000 artefacts and rooftop observation deck. In the afternoon, visit the National Art Museum — over 30,000 works spanning 900 years.\n\nDay 3 — Nature: Visit the National Library of Belarus with its iconic diamond shape and panoramic rooftop. Stroll the Svislach River embankment and end at Gorky Park.\n\nFood: Try draniki (potato pancakes), machanka (pork stew), and Belarusian kvass.', '/static/images/attractions/28.jpg', '[\"City Guide\", \"Architecture\", \"Urban\"]', 522, 71, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (6, 1, 25, 'Grodno Old Town: A Stroll Through Eight Centuries', 'Why Grodno is the best-preserved historic city in Belarus.', 'Grodno is the rare Belarusian city that survived World War II largely intact. Its old town preserves buildings from the 13th to 19th centuries along cobblestone streets that follow their original medieval layout.\n\nKey Sights: The New Town area with Polish-era merchant houses, the former Royal Castle site, the old market square, and the Old Town walking streets. The SS. Boris and Gleb Church (Kalozha) — one of the oldest surviving structures in Belarus — is just a few minutes walk.\n\nDay Trips from Grodno: Holy Trinity Church in Gierviaty (\"Belarusian Notre-Dame\"), Augustow Canal, and Lida Castle are all within an hour.\n\nWhen to Visit: Summer evenings are magical — outdoor cafes along the Neman River fill with locals and visitors.', '/static/images/attractions/25.jpg', '[\"City Guide\", \"Architecture\", \"History\"]', 167, 23, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (7, 2, 24, 'Polotsk: The Cradle of Belarusian Christianity', 'A walking guide to Belarus oldest city, founded in 862 AD.', 'Polotsk is one of the oldest cities in the entire former Kievan Rus. Founded in 862 AD, it served as the capital of an independent principality and is the birthplace of Belarusian Christianity.\n\nThe Saint Sophia Cathedral: Originally built in the 11th century, rebuilt in Baroque style after the Great Northern War. The interior features an impressive iconostasis and acoustically perfect nave for choral performances.\n\nThe Bogoyavlensky Monastery and the Copernicus House: The latter commemorates Copernicus maternal family connection to Polotsk.\n\nThe Western Dvina River Embankment: A scenic walk that ties all the historic sights together.', '/static/images/attractions/24.jpg', '[\"History\", \"Architecture\", \"City Guide\"]', 134, 19, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (8, 1, 23, 'Vitebsk for Art Lovers: The Chagall Trail', 'A self-guided walking tour of Marc Chagall birthplace and his artistic legacy.', 'Vitebsk is the hometown of Marc Chagall (1887-1985), one of the 20th century most influential artists. Even if you only have a day, you can follow his footsteps through the city.\n\nThe Marc Chagall Museum: Housed in the building where Chagall lived and worked during his years as art director of the Vitebsk Art School (1919-1920). The collection includes paintings, graphic works, and personal belongings.\n\nThe Vitebsk Regional Museum: A broader history of the region with a notable Chagall-period section.\n\nThe Summer Festival: Every July the city hosts the Slavianski Bazaar international arts festival, drawing performers from across the Slavic world.', '/static/images/attractions/23.jpg', '[\"Art\", \"Culture\", \"Museums\"]', 121, 17, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (9, 1, 22, 'Lake Naroch: A Belarusian Seaside Escape', 'How to plan a summer holiday at the largest lake in Belarus.', 'Lake Naroch is the largest lake in Belarus at 79.6 square kilometres. With its sandy beaches, clear water, and surrounding pine forests, it is often called the Belarusian seaside.\n\nWhere to Stay: The town of Naroch has sanatoriums and guesthouses catering to families. Book in advance for July and August.\n\nWhat to Do: Swimming, sunbathing on sandy beaches, kayaking on the lake, cycling along forest paths. Several smaller lakes nearby are worth a half-day visit.\n\nBest Time: June to early September. July water temperatures are warmest.', '/static/images/attractions/22.jpg', '[\"Nature\", \"Lakes\", \"Family Friendly\"]', 178, 26, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (10, 2, 21, 'Braslau Lakes: Kayaking the Belarusian Lakeland', 'A three-day paddling itinerary through the most scenic lake district in Belarus.', 'The Braslau Lakes National Park in northern Vitebsk Oblast encompasses over 30 glacial lakes connected by rivers. The rolling hills, pine forests, and crystal-clear water make it the most beautiful lake district in the country.\n\nSuggested Route (3 days, 50km): Day 1 — Start at Lake Drysvyaty and paddle south. Day 2 — Cross to Lake Snudy via a short portage. Day 3 — Finish at Lake Strusto.\n\nGear: Rent kayaks and dry bags at the park visitor centre. Bring layers — even in summer evenings can be cool.\n\nWildlife: Watch for white-tailed eagles, kingfishers, and — if lucky — beavers along the shoreline.', '/static/images/attractions/21.jpg', '[\"Nature\", \"Lakes\", \"Adventure\"]', 211, 31, 0, 1, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (11, 1, 47, 'Rumyantsev-Paskevich Palace in Gomel: A Day Trip from Minsk', 'A complete visit guide to the neoclassical palace featured on the 20-ruble banknote.', 'Gomel Palace is one of the most beautiful architectural monuments in Belarus. Featured on the 20-ruble banknote, it stretches 800 metres along the Sozh River.\n\nThe Main Building: Housed in the neoclassical palace of the Rumyantsev and Paskevich families. Inside, the decorative arts collection, weaponry, and portrait gallery are highlights.\n\nThe Park: The ancient park contains the Chapel of St. Nicholas, a watchtower, the winter garden, and riverside walkways.\n\nGetting There: Gomel is about 300km southeast of Minsk. The high-speed train takes 3 hours. The palace is a 15-minute walk from Gomel railway station.', '/static/images/attractions/47.jpg', '[\"Architecture\", \"History\", \"Museums\"]', 156, 22, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);
INSERT INTO `articles` VALUES (12, 1, 16, 'Belarusian Cuisine: A Foodie Introduction', 'The ten dishes every visitor to Belarus must try at least once.', 'Belarusian cuisine is hearty, rustic, and built around potatoes, pork, mushrooms, and dairy. If you only have a week, here are the dishes not to miss.\n\n1. Draniki: Shredded potato pancakes, pan-fried until golden and served with sour cream or mushroom sauce. The national dish.\n\n2. Machanka: A pork stew with sausage and onions served over draniki or pancakes.\n\n3. Borscht: The classic beet soup, often served with a meat-stuffed pasty called vushanka.\n\n4. Kolduny: Potato dumplings stuffed with minced meat.\n\n5. Babka: A potato-and-meat casserole baked in the oven.\n\n6. Vereshchaka: A sweet-and-sour pork dish served at Christmas.\n\n7. Smetannik: A layered honey cake with sour cream frosting.\n\n8. Kvass: A fermented bread drink, perfect on a hot day.\n\n9. Medovukha: A traditional honey-based alcoholic drink, lighter than mead.\n\n10. Kletsky: Cep mushroom dumplings.\n\nWhere to Try: Traditional restaurants in Minsk include Grablyn Kletz, Vasilki, and the Lidskaya Kafe chain.', '/static/images/attractions/16.jpg', '[\"Food\", \"Culture\"]', 289, 42, 0, 0, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL, NULL);

-- ----------------------------
-- Table structure for attraction_tags
-- ----------------------------
DROP TABLE IF EXISTS `attraction_tags`;
CREATE TABLE `attraction_tags`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attraction_id` bigint NOT NULL,
  `tag_id` bigint NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_attraction_tag`(`attraction_id` ASC, `tag_id` ASC) USING BTREE,
  INDEX `idx_attag_tag_id`(`tag_id` ASC) USING BTREE,
  INDEX `idx_attag_attraction_id`(`attraction_id` ASC) USING BTREE,
  CONSTRAINT `attraction_tags_ibfk_1` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `attraction_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 172 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attraction_tags
-- ----------------------------
INSERT INTO `attraction_tags` VALUES (1, 1, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (2, 1, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (3, 1, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (4, 2, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (5, 2, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (6, 2, 5, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (7, 3, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (8, 3, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (9, 3, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (10, 3, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (11, 3, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (12, 4, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (13, 4, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (14, 5, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (15, 6, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (16, 6, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (17, 7, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (18, 7, 5, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (19, 8, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (20, 9, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (21, 9, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (22, 10, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (23, 10, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (24, 11, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (25, 11, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (26, 11, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (27, 11, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (28, 12, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (29, 12, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (30, 12, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (31, 13, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (32, 13, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (33, 14, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (34, 15, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (35, 16, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (36, 16, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (37, 16, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (38, 16, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (39, 17, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (40, 17, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (41, 17, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (42, 18, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (43, 19, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (44, 20, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (45, 21, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (46, 22, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (47, 23, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (48, 23, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (49, 23, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (50, 24, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (51, 24, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (52, 24, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (53, 25, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (54, 25, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (55, 26, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (56, 26, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (57, 26, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (58, 27, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (59, 27, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (60, 28, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (61, 28, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (62, 29, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (63, 29, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (64, 30, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (65, 30, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (66, 31, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (67, 32, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (68, 32, 5, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (69, 33, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (70, 34, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (71, 34, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (72, 35, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (73, 35, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (74, 35, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (75, 35, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (76, 35, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (77, 36, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (78, 36, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (79, 37, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (80, 37, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (81, 37, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (82, 37, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (83, 38, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (84, 38, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (85, 38, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (86, 38, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (87, 39, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (88, 39, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (89, 39, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (90, 39, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (91, 40, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (92, 40, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (93, 40, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (94, 41, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (95, 41, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (96, 41, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (97, 41, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (98, 42, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (99, 43, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (100, 43, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (101, 44, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (102, 45, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (103, 45, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (104, 46, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (105, 46, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (106, 46, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (107, 46, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (108, 47, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (109, 47, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (110, 48, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (111, 48, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (112, 49, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (113, 49, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (114, 50, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (115, 50, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (116, 50, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (117, 51, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (118, 52, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (119, 53, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (120, 53, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (121, 54, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (122, 55, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (123, 56, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (124, 56, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (125, 57, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (126, 57, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (127, 58, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (128, 58, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (129, 58, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (130, 59, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (131, 59, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (132, 59, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (133, 60, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (134, 60, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (135, 60, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (136, 61, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (137, 61, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (138, 62, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (139, 62, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (140, 62, 1, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (141, 63, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (142, 64, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (143, 65, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (144, 66, 9, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (145, 67, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (146, 67, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (147, 67, 13, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (148, 68, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (149, 68, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (150, 68, 11, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (151, 69, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (152, 69, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (153, 70, 3, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (154, 70, 12, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (155, 70, 6, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (156, 71, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (157, 71, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (158, 72, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (159, 72, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (160, 73, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (161, 74, 4, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (162, 74, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (163, 75, 7, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (164, 76, 8, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (165, 77, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (166, 77, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (167, 78, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (168, 78, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (169, 79, 10, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (170, 79, 2, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (171, 79, 14, '2026-07-04 19:24:17');
INSERT INTO `attraction_tags` VALUES (172, 80, 4, '2026-07-04 19:24:17');

-- ----------------------------
-- Table structure for attractions
-- ----------------------------
DROP TABLE IF EXISTS `attractions`;
CREATE TABLE `attractions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_en` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `name_be` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `short_desc` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `location` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `region` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `latitude` decimal(10, 7) NULL DEFAULT NULL,
  `longitude` decimal(10, 7) NULL DEFAULT NULL,
  `category` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `suitable_season` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `opening_hours` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ticket_price` decimal(10, 2) NULL DEFAULT NULL,
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `images_json` json NULL,
  `avg_rating` decimal(3, 2) NOT NULL,
  `total_reviews` int NOT NULL,
  `sentiment_score` decimal(4, 3) NULL DEFAULT NULL,
  `sentiment_pos_count` int NOT NULL,
  `sentiment_neg_count` int NOT NULL,
  `wishlist_count` int NOT NULL,
  `view_count` int NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `created_by` bigint NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `created_by`(`created_by` ASC) USING BTREE,
  INDEX `idx_category`(`category` ASC) USING BTREE,
  INDEX `idx_is_featured`(`is_featured` ASC) USING BTREE,
  INDEX `idx_avg_rating`(`avg_rating` ASC) USING BTREE,
  INDEX `idx_region`(`region` ASC) USING BTREE,
  CONSTRAINT `attractions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 81 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attractions
-- ----------------------------
INSERT INTO `attractions` VALUES (1, 'Mir Castle Complex', 'Mir Castle Complex', NULL, 'A UNESCO World Heritage Site since 2000. Built in the early 16th century in late Brick Gothic style, Mir Castle is one of the finest examples of fortified architecture from the former Polish-Lithuanian Commonwealth. Five towers rise 27 metres above the defensive moat, surrounding a central courtyard. Later Renaissance and Baroque additions created a unique blend of architectural styles. Located beside a picturesque lake whose waters perfectly mirror the castle silhouette. Houses a museum with period furniture, weaponry, tapestries, and portraits tracing 500 years of history through Lithuanian, Polish, Russian, and Belarusian ownership.', 'UNESCO World Heritage Site — a 16th-century Gothic-Renaissance fortified castle with five towers.', 'Mir, Karelichy District, Grodno Oblast', 'Mir', 'Grodno Oblast', 53.4512389, 26.4730000, 'castle', 'Spring, Summer, Autumn', '09:00 - 18:00', 10.00, '/static/images/attractions/1.jpg', NULL, 5.00, 1, 0.000, 0, 0, 0, 10, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-05 09:14:51');
INSERT INTO `attractions` VALUES (2, 'Nesvizh Castle (Radziwill Palace)', 'Nesvizh Castle', NULL, 'A UNESCO World Heritage Site since 2005. The seat of the powerful Radziwill dynasty for over 400 years, this architectural masterpiece combines Renaissance, Baroque, Classicism, Gothic Revival, and Modernism. The complex comprises the residential palace and Corpus Christi mausoleum-church with its landscaped setting. The gilded ballroom, portrait gallery, armoury, and palace chapel (one of the earliest Jesuit churches outside Rome with the largest family crypt in Europe) are must-sees. The surrounding park spans over 100 hectares with English, French, and Japanese-style garden sections and interconnected ponds.', 'UNESCO World Heritage Site — Radziwill family palace and park complex, the most beautiful castle in Belarus.', 'Nesvizh, Minsk Oblast', 'Nesvizh', 'Minsk Oblast', 53.2269444, 26.5777778, 'palace', 'Spring, Summer, Autumn', '10:00 - 17:00 (Tue-Sun)', 8.00, '/static/images/attractions/2.jpg', NULL, 4.70, 0, 0.000, 0, 0, 1, 4, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:59:23');
INSERT INTO `attractions` VALUES (3, 'Belovezhskaya Pushcha National Park', 'Belovezhskaya Pushcha National Park', NULL, 'A UNESCO World Heritage Site shared with Poland. One of the last remaining fragments of the primeval forest that once covered the European Plain. The forest is home to over 600 European bison (the continent\'s heaviest land animal), wolves, lynx, wild boar, and over 250 bird species. Ancient oaks exceed 600 years old, and spruces reach 50 metres in height. Visitors can explore on marked hiking and cycling trails, or by horse-drawn cart on guided tours. The park\'s Nature Museum offers an excellent introduction to the ecosystem. In winter, it operates as the official residence of Ded Moroz (Grandfather Frost), drawing families from across the region.', 'UNESCO World Heritage Site — Europe\'s last primeval forest, home to 600+ European bison.', 'Kamieniuki, Brest Oblast', 'Kamieniuki', 'Brest Oblast', 52.5833333, 23.8666667, 'nature', 'All seasons (best May-Sep)', '09:00 - 17:00', 5.00, '/static/images/attractions/3.jpg', NULL, 4.60, 0, 0.000, 0, 0, 0, 3, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 13:01:37');
INSERT INTO `attractions` VALUES (4, 'Struve Geodetic Arc (Belarus Points)', 'Struve Geodetic Arc', NULL, 'A UNESCO World Heritage Site since 2005 (transnational, shared with 9 other countries). A series of triangulation points stretching 2,820 km from Hammerfest, Norway to the Black Sea, established by astronomer Friedrich Georg Wilhelm von Struve to measure the shape of the Earth. Five of the original 265 station points are located in Belarus, near the towns of Tupiški and near Minsk. These geodetic markers represent a remarkable scientific achievement that helped establish the size and shape of our planet.', 'UNESCO World Heritage — 19th-century geodetic survey points across 10 countries.', 'Tupiški, Grodno Oblast', 'Tupiški', 'Grodno Oblast', 54.2833000, 26.0500000, 'memorial', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/4.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (5, 'Lida Castle', 'Lida Castle', NULL, 'A well-preserved 14th-century fortified castle built by Prince Gediminas of the Grand Duchy of Lithuania. One of the few medieval brick castles in Belarus that retains much of its original defensive structure, including four corner towers and fortified walls. The castle played a key role in defending the western borders of the Grand Duchy. According to legend, Grand Duke Vytautas the Great ordered its construction. The castle hosts medieval reenactment festivals and knight tournaments during summer months.', '14th-century Gediminas-era castle — one of the best-preserved medieval brick castles in Belarus.', 'Lida, Grodno Oblast', 'Lida', 'Grodno Oblast', 53.8833000, 25.3000000, 'castle', 'Spring, Summer, Autumn', '09:00 - 17:00', 4.00, '/static/images/attractions/5.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (6, 'Navahrudak Castle (Kamyenyets Tower)', 'Navahrudak Castle', NULL, 'A 13th-century fortified castle on a rocky hill in the legendary birthplace of the Lithuanian state. The castle is associated with the founding of the Grand Duchy of Lithuania and features massive defensive walls built from local limestone. Navahrudak (also called Novogrudok) was the seat of the Gediminas princes and retains ruins of the tower, walls, and a 17th-century church. The town itself is surrounded by seven hills and offers panoramic views over the surrounding landscape.', '13th-century castle ruins on the legendary birthplace of the Lithuanian state.', 'Navahrudak, Grodno Oblast', 'Navahrudak', 'Grodno Oblast', 53.5833000, 25.8167000, 'castle', 'Spring, Summer, Autumn', '09:00 - 17:00', 3.00, '/static/images/attractions/6.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (7, 'Krevo Castle', 'Krevo Castle', NULL, 'A partially preserved medieval castle originally built in the 13th century. Once the residence of the Gediminas family — one of the most powerful dynasties in Eastern Europe — it is one of the oldest stone castles in Belarus. The castle was built at the confluence of the Awsłaŭ and Swisłocz rivers as part of the Grand Duchy of Lithuania\'s western defensive line. The ruins include sections of the defensive walls and towers.', '13th-century castle — former residence of the Gediminas dynasty, one of the oldest stone castles in Belarus.', 'Krevo, Volozhin District, Minsk Oblast', 'Krevo', 'Minsk Oblast', 54.1500000, 26.8333000, 'castle', 'Spring, Summer, Autumn', '09:00 - 17:00', 3.00, '/static/images/attractions/7.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (8, 'Lubcha Castle', 'Lubcha Castle', NULL, 'Once the largest fortified castle in the Grand Duchy of Lithuania, built in the 16th century. The castle featured massive walls, deep moats, and a sophisticated defensive system. Its massive ruins still convey the grandeur of what was once a major defensive and residential complex. The castle was damaged during the Napoleonic Wars and fell into disrepair, but ongoing restoration efforts aim to preserve its significant historical legacy.', 'Ruins of the once-largest castle in the Grand Duchy of Lithuania.', 'Lubcha, Kletsk District, Minsk Oblast', 'Lubcha', 'Minsk Oblast', 53.0333000, 27.0500000, 'castle', 'Spring, Summer, Autumn', '09:00 - 18:00', 3.00, '/static/images/attractions/8.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (9, 'Kamyanets Tower (Belaya Vezha)', 'Kamyanets Tower', NULL, 'A 13th-century defensive tower built during the time of Prince Vytautas, one of the most important defensive structures in the Grand Duchy of Lithuania. The tower stands 30 metres tall and is one of the oldest fortifications in Belarus. It became one of the most photographed landmarks in the country due to its dramatic silhouette and association with the borderland history between Lithuania and Poland.', '13th-century defensive tower — one of the oldest fortifications in Belarus.', 'Kamenets, Brest Oblast', 'Kamenets', 'Brest Oblast', 52.2167000, 23.8167000, 'castle', 'All seasons', '09:00 - 17:00', 2.00, '/static/images/attractions/9.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 7, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:59:08');
INSERT INTO `attractions` VALUES (10, 'Minsk Castle (Menski Castle)', 'Minsk Castle', NULL, 'The historic fortified castle of Minsk, originally built in the 12th century. The castle was severely damaged during the Great Northern War and subsequently demolished. Only fragments of the original walls and foundations remain near the Svislach River. A reconstruction project has been discussed, and archaeological excavations continue to reveal the castle\'s history.', '12th-century castle ruins — the historic fortified seat of Minsk princes.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9053000, 27.5558000, 'castle', 'All seasons', 'External viewing only', 0.00, '/static/images/attractions/10.jpg', NULL, 3.50, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 08:37:23');
INSERT INTO `attractions` VALUES (11, 'Brest Hero Fortress', 'Brest Fortress', NULL, 'A sprawling memorial complex on the border with Poland. On 22 June 1941, this 19th-century citadel was among the very first targets of Operation Barbarossa. The garrison held out for over a month against overwhelming German forces — one of the longest last-stand battles of WWII. The centrepiece is the colossal \"Courage\" sculpture, a concrete head emerging from a rock face ranking among the largest portrait sculptures in the world. The Defence of Brest Fortress Museum displays maps, personal belongings, and recovered weaponry. The fortress has drawn 2.8 million visitors over the past five years and held about 55,000 guided tours.', 'Heroic WWII fortress — first battle site of the Great Patriotic War, symbol of endurance.', 'Brest, Belarus', 'Brest', 'Brest Oblast', 52.0833000, 23.9167000, 'memorial', 'All seasons', '09:00 - 18:00', 0.00, '/static/images/attractions/11.jpg', NULL, 4.70, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (12, 'Khatyn Memorial Complex', 'Khatyn Memorial Complex', NULL, 'A national memorial commemorating the victims of the Khatyn massacre of March 1943 and the destruction of over 400 Belarusian villages by Nazi forces. The memorial features 185 chimneys — one for each burned village — each with a bell that chimes in the wind. The iconic 20-tonne \"Never Again\" bell, a sculpture of a dying mother holding her dead child, a cemetery of symbolic graves, and a 26-metre obelisk form the centrepiece. As of 2026, Khatyn ranks as the second-most-visited monument in Belarus after Lida Castle, with approximately 17,000 visitors in the first five months of 2026.', 'National memorial to victims of Nazi atrocities and 400+ destroyed Belarusian villages.', 'Khatyn, Minsk Region', 'Khatyn', 'Minsk Region', 54.3000000, 27.9000000, 'memorial', 'All seasons', '10:00 - 18:00', 0.00, '/static/images/attractions/12.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (13, 'Kurapaty Mass Graves', 'Kurapaty', NULL, 'A memorial site marking mass executions carried out by the NKVD between 1937 and 1941 under Stalin\'s Great Purge. Located in a forest on the outskirts of Minsk, the site contains the remains of thousands of Belarusians executed as \"enemies of the people.\" The site serves as a memorial to victims of Stalinist repressions and is an important place of historical memory and civic education in Belarus. Visitors walk through the forest along marked trails past unmarked pits.', 'Memorial to victims of Stalinist repressions — mass grave site of NKVD killings (1937-1941).', 'Kurapaty, Minsk', 'Minsk', 'Minsk', 53.9333000, 27.5833000, 'memorial', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/13.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (14, 'Island of Tears Memorial', 'Island of Tears Memorial', NULL, 'A poignant memorial on an islet in the Svislach River in Minsk, dedicated to Belarusian soldiers who died in the Soviet-Afghan War (1979-1989). The memorial features a sculpture of a weeping mother, walls inscribed with the names of fallen soldiers, and a small chapel. It is one of the most emotionally powerful memorials in Belarus.', 'Memorial to Belarusian soldiers who died in the Soviet-Afghan War, on an island in the Svislach River.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9083000, 27.5550000, 'memorial', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/14.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (15, 'Plamya (Eternal Flame) Memorial', 'Plamya Memorial', NULL, 'An eternal flame memorial in Victory Square, Minsk, dedicated to all Belarusians who died in wars. The monument consists of a four-sided granite obelisk topped by the eternal flame. A relief sculpture depicts soldiers, workers, and partisans. Located in central Minsk\'s most symbolic square, it is one of the most visited war memorials in the country.', 'Eternal flame memorial in central Minsk honouring all Belarusian war casualties.', 'Victory Square, Minsk', 'Minsk', 'Minsk', 53.9083000, 27.5725000, 'memorial', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/15.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 3, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:54:02');
INSERT INTO `attractions` VALUES (16, 'Great Patriotic War Museum', 'Museum of the Great Patriotic War', NULL, 'The largest military history museum in Belarus, opened in 2014 on the 70th anniversary of the liberation of Minsk. Located near the Svislach River, the modern building holds over 8,000 artefacts with immersive dioramas and multimedia installations. The story of Belarus during WWII — in which the country lost approximately a quarter of its population — is told through personal belongings, weapons, uniforms, and interactive exhibits. The rooftop observation deck offers panoramic views of Minsk.', 'Largest WWII museum in Belarus — 8,000+ artefacts, immersive multimedia exhibits, rooftop views.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9208000, 27.5378000, 'museum', 'All seasons', '10:00 - 18:00 (Tue-Sun)', 5.00, '/static/images/attractions/16.jpg', NULL, 4.60, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (17, 'National Art Museum of Belarus', 'National Art Museum of Belarus', NULL, 'The largest collection of fine arts in Belarus, with over 30,000 works spanning 900 years from 12th-century religious icons to contemporary Belarusian art. The collection includes paintings by Ilya Repin, Ivan Shishkin, and Marc Chagall (including works from his Vitebsk period), as well as a comprehensive survey of Belarusian artists. Sculptures, graphics, and applied arts complete the picture.', 'Over 30,000 artworks spanning 900 years — from medieval icons to Marc Chagall and Belarusian masters.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9114000, 27.5692000, 'museum', 'All seasons', '11:00 - 19:00 (Wed-Mon)', 6.00, '/static/images/attractions/17.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (18, 'Museum of Belarusian Folk Architecture', 'Museum of Belarusian Folk Architecture', NULL, 'An open-air ethnographical museum in Ozertsy, 45 km from Minsk, showcasing traditional Belarusian village architecture from the 17th to early 20th centuries. Features authentic wooden houses, churches, windmills, and farm buildings relocated from different regions of Belarus, set in a natural landscape. Visitors can see how rural Belarusians lived, worked, and worshipped across centuries.', 'Open-air ethnographical museum — authentic relocated wooden village buildings from across Belarus.', 'Ozertsy, Minsk Oblast', 'Ozertsy', 'Minsk Oblast', 54.0167000, 27.6333000, 'museum', 'Spring, Summer, Autumn', '10:00 - 17:00 (Wed-Mon)', 4.00, '/static/images/attractions/18.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 5, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:36');
INSERT INTO `attractions` VALUES (19, 'Gomel Palace Museum', 'Gomel Palace Museum', NULL, 'Housed in the historic Rumyantsev-Paskevich Palace, one of the most beautiful architectural monuments in Belarus. The palace is featured on the Belarusian 20-ruble banknote. Collections include decorative arts, weapons, paintings, and archaeological artifacts from the Gomel region spanning several centuries. The estate complex stretches 800 metres along the Sozh River.', 'Decorative arts, weapons, and paintings in the historic Rumyantsev-Paskevich Palace.', 'Gomel, Belarus', 'Gomel', 'Gomel Oblast', 52.4411000, 30.9933000, 'museum', 'All seasons', '10:00 - 18:00 (Wed-Mon)', 5.00, '/static/images/attractions/19.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (20, 'Marc Chagall Museum', 'Marc Chagall Museum', NULL, 'Located in Vitebsk, the hometown of the renowned artist Marc Chagall (1887-1985). The museum is housed in a building where Chagall lived and worked during his years as an artist in Vitebsk (1919-1920), when he served as art director of the Vitebsk Art School. Contains the largest collection of Chagall\'s works in Belarus, including paintings, graphic works, and personal belongings. A must-visit for art lovers.', 'Largest Belarusian collection of Marc Chagall\'s works — in the artist\'s hometown of Vitebsk.', 'Vitebsk, Belarus', 'Vitebsk', 'Vitebsk Oblast', 55.1950000, 30.2050000, 'museum', 'All seasons', '10:00 - 17:00 (Tue-Sun)', 4.00, '/static/images/attractions/20.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (21, 'Mogilev Regional Museum', 'Mogilev Regional Museum', NULL, 'A museum of local history and culture in Mogilev, one of the oldest cities in Belarus (founded in the 13th century). Collections include archaeology, history, fine arts, and ethnography from the Dnieper River region. The museum building itself is a historic architectural monument in the centre of the city.', 'Local history of Mogilev — one of Belarus oldest cities, on the Dnieper River.', 'Mogilev, Belarus', 'Mogilev', 'Mogilev Oblast', 53.9167000, 30.3500000, 'museum', 'All seasons', '10:00 - 17:00 (Tue-Sun)', 3.00, '/static/images/attractions/21.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (22, 'Berestye Archaeological Museum', 'Berestye Museum', NULL, 'Built over the excavated remains of a 13th-century Slavic settlement on the banks of the Mukhavets River, the Berestye Museum in Brest offers a rare look at medieval life in the region. The settlement was an important trading post on the route from the Varangians to the Greeks. Artifacts on display include tools, ceramics, jewellery, and reconstructed period interiors.', 'Medieval Slavic settlement museum — 13th-century ruins with reconstructed period interiors.', 'Brest, Belarus', 'Brest', 'Brest Oblast', 52.0950000, 23.6900000, 'museum', 'All seasons', '10:00 - 18:00', 3.00, '/static/images/attractions/22.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (23, 'SS. Boris and Gleb Church (Kalozha)', 'SS. Boris and Gleb Church, Grodno', NULL, 'Built in the 1180s in brick and stone, this church in Grodno is one of the oldest surviving examples of Belarusian architecture. Only two walls, three apses, and two pillars remain from the original 12th-century structure; the rest collapsed during a landslide of the high bank of the Neman River. Still an active place of worship, it is one of the most-visited religious sites in Belarus, ranking as the third-most-popular monument with approximately 16,000 visitors in 2026.', '12th-century church — one of the oldest surviving structures in Belarus, in active worship.', 'Grodno, Belarus', 'Grodno', 'Grodno Oblast', 53.6833000, 23.8333000, 'church', 'All seasons', '07:00 - 19:00', 0.00, '/static/images/attractions/23.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (24, 'Holy Trinity Church in Gierviaty', 'Holy Trinity Church, Gierviaty', NULL, 'A magnificent neo-Gothic Roman Catholic church built between 1868 and 1903. Often called the \"Belarusian Notre-Dame\" or \"Little Switzerland,\" this church is one of the most impressive architectural achievements in Belarus. Its twin 75-metre spires are visible for kilometres in every direction. The interior features ornate altar pieces, stained glass, and carved wooden confessionals. One of the most photographed religious sites in the country.', '\"Belarusian Notre-Dame\" — stunning neo-Gothic church, one of the most photographed in Belarus.', 'Gierviaty, Grodno Oblast', 'Gierviaty', 'Grodno Oblast', 54.2833000, 25.7833000, 'church', 'Spring, Summer, Autumn', 'By arrangement', 0.00, '/static/images/attractions/24.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 2, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:39');
INSERT INTO `attractions` VALUES (25, 'Saint Sophia Cathedral, Polotsk', 'Saint Sophia Cathedral, Polotsk', NULL, 'The oldest cathedral in Belarus, originally built in the 11th century in the Pskovian style of ancient Rus architecture. It was rebuilt several times — first after a 1447 fire and again in the 18th century after the Great Northern War, when it received its Baroque-style facade with Rococo ornamental elements. The cathedral was built to match the grandeur of Constantinople\'s Hagia Sophia, symbolising the spiritual importance of Polotsk. Today it functions as a museum and occasional concert venue for choral performances.', 'The oldest cathedral in Belarus — 11th century, rebuilt in Baroque style with Rococo facade.', 'Polotsk, Vitebsk Oblast', 'Polotsk', 'Vitebsk Oblast', 55.5000000, 28.7667000, 'church', 'All seasons', '09:00 - 18:00', 4.00, '/static/images/attractions/25.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (26, 'Holy Trinity Cathedral, Minsk', 'Holy Trinity Cathedral, Minsk', NULL, 'Also known as the Barysauka Church, this 17th-century Eastern Orthodox cathedral in the historic Upper Town of Minsk is one of the oldest surviving buildings in the city. Built in the Baroque style with influences from Belarusian and Ukrainian church architecture, it features a three-tiered tent-roof belfry. The cathedral is surrounded by the remains of the old city wall and forms part of a historic ensemble with the Minsk Town Hall.', '17th-century Eastern Orthodox cathedral — one of the oldest buildings in Minsk.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9053000, 27.5558000, 'church', 'All seasons', '07:00 - 20:00', 0.00, '/static/images/attractions/26.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (27, 'St. Simon and Helena Church (Red Church)', 'Red Church, Minsk', NULL, 'An outstanding Neo-Gothic Roman Catholic church built between 1905 and 1910. Its distinctive red brick facade and twin 73-metre spires make it one of the most recognizable buildings in Minsk. The interior features soaring vaulted ceilings, stained glass windows, and ornate altar pieces. The church was closed during the Soviet period and reopened in 1990. It hosts regular concerts of organ music.', 'Neo-Gothic Roman Catholic church — iconic red brick twin-spire landmark in central Minsk.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9086000, 27.5631000, 'church', 'All seasons', '10:00 - 18:00', 0.00, '/static/images/attractions/27.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:34:13');
INSERT INTO `attractions` VALUES (28, 'St. Nicholas Monastery, Gomel', 'St. Nicholas Monastery, Gomel', NULL, 'An active Orthodox monastery founded in the 16th century, featuring the Church of St. Nicholas with its distinctive multi-tiered tent-roof belfry that has become a symbol of Gomel. The monastery complex sits along the Sozh River and includes a cathedral, residential buildings, and a museum of monastery history. The Church of St. Nicholas is one of the finest examples of Belarusian baroque church architecture.', '16th-century Orthodox monastery with iconic tent-roof belfry on the Sozh River.', 'Gomel, Belarus', 'Gomel', 'Gomel Oblast', 52.4333000, 30.9833000, 'church', 'All seasons', '06:00 - 20:00', 0.00, '/static/images/attractions/28.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (29, 'Zhyrovichy Monastery', 'Zhyrovichy Monastery', NULL, 'A 16th-century Orthodox monastery famous for the \"Zhyrovichy Mother of God\" icon, believed to have miraculous healing powers. The monastery has been a major pilgrimage site for centuries. The current church buildings date from the 18th-19th centuries and feature a distinctive exterior painted in bright colours with elaborate frescoes. Pilgrims come from across Belarus and beyond to venerate the icon.', '16th-century Orthodox monastery — major pilgrimage site for the miraculous Zhyrovichy icon.', 'Zhyrovichy, Slavgorod District, Mogilev Oblast', 'Zhyrovichy', 'Mogilev Oblast', 53.4333000, 31.5500000, 'church', 'All seasons', '06:00 - 20:00', 0.00, '/static/images/attractions/29.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (30, 'Borisoglebskaya Church, Mogilev', 'Borisoglebskaya Church, Mogilev', NULL, 'A late 17th-century wooden church in the style of Belarusian baroque architecture. One of the oldest wooden churches in eastern Belarus, it features a distinctive multi-tiered tent-roof belfry, carved wooden iconostasis, and original floor tiles. The church has survived wars and political upheavals and remains an active place of worship.', 'Late 17th-century wooden baroque church — one of the oldest in eastern Belarus.', 'Mogilev, Belarus', 'Mogilev', 'Mogilev Oblast', 53.9167000, 30.3333000, 'church', 'Spring, Summer, Autumn', 'By arrangement', 0.00, '/static/images/attractions/30.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (31, 'Gomel Palace and Park Ensemble', 'Rumyantsev-Paskevich Palace', NULL, 'One of the most beautiful architectural monuments in Belarus, featured on the Belarusian 20-ruble banknote. The palace complex includes the main neoclassical building, the Church of St. Nicholas, a chapel with burial vault, a winter garden, a watchtower, and an 800-metre-long ancient park along the Sozh River. Home to the Rumyantsev and Paskevich families. Today it serves as a major museum complex and cultural centre.', 'Palace featured on the 20-ruble note — neoclassical ensemble with park on the Sozh River.', 'Gomel, Belarus', 'Gomel', 'Gomel Oblast', 52.4411000, 30.9933000, 'palace', 'Spring, Summer, Autumn', '10:00 - 18:00 (Wed-Mon)', 6.00, '/static/images/attractions/31.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (32, 'Kosava Palace', 'Kosava Palace', NULL, 'An 18th-century magnate palace built in the Baroque style, once the seat of the Sapeika family. The palace features ornate stucco ceilings, a collection of period paintings, and an English-style landscape park. One of the most dynamically visited sites in 2026 according to tourist analytics. Currently undergoing restoration and open for guided tours.', 'Baroque magnate palace of the 18th century — one of the most visited sites in 2026.', 'Kosava, Pruzhany District, Brest Oblast', 'Kosava', 'Brest Oblast', 52.4167000, 24.3667000, 'palace', 'Spring, Summer, Autumn', '10:00 - 17:00', 5.00, '/static/images/attractions/32.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (33, 'Mikhail Kleofas Oginski Museum-Estate', 'Oginski Museum-Estate', NULL, 'The estate of Prince Mikhail Kleofas Oginski (1765-1833), a Polish-Lithuanian nobleman, composer, and politician. Oginski composed the famous polandaise \" Thoughts\" here and was a patron of the arts. The estate includes the palace, a park with ponds, and an exhibition dedicated to Oginski\'s life and work. One of the most dynamically growing tourist sites in 2026.', 'Estate of Prince Oginski — composer of the famous polandaise, patron of the arts.', 'Zalessye, Mogilev Oblast', 'Zalessye', 'Mogilev Oblast', 54.0000000, 31.3500000, 'palace', 'Spring, Summer, Autumn', '10:00 - 17:00 (Tue-Sun)', 4.00, '/static/images/attractions/33.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (34, 'Narochansky National Park', 'Narochansky National Park', NULL, 'Named after Lake Naroch — the largest lake in Belarus at 79.6 square kilometres — this park encompasses the lake, surrounding pine forests, and several smaller lakes. The area is known for its sandy beaches, clear water, pine forests, and tranquil natural beauty. Water sports, swimming, and beach recreation are popular in summer. The town of Naroch is a popular resort destination with sanatoriums and guesthouses.', 'Largest lake in Belarus (79.6 km²) with sandy beaches and pine forests.', 'Naroch, Myadel District, Minsk Oblast', 'Naroch', 'Minsk Oblast', 54.9833000, 26.7333000, 'nature', 'Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/34.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (35, 'Braslau Lakes National Park', 'Braslau Lakes National Park', NULL, 'Located in the north of Belarus near the borders with Latvia and Russia, this park encompasses over 30 glacial lakes connected by rivers and streams. The rolling hills, pine forests, and crystal-clear lakes of the Braslau region make it the most picturesque lake district in Belarus. Ideal for kayaking, birdwatching, lakeside camping, and cycling. The landscape was shaped by glacial activity during the last Ice Age.', '30+ glacial lakes in northern Belarus — kayaking, birdwatching, and lakeside camping.', 'Braslau, Miory District, Vitebsk Oblast', 'Braslau', 'Vitebsk Oblast', 55.7333000, 27.0500000, 'nature', 'Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/35.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (36, 'Pripyatsky National Park', 'Pripyatsky National Park', NULL, 'A vast protected area covering the Belarusian section of the Pripyat River wetlands and floodplains. Features primeval forests, meadows, and marshes that provide habitat for rare species including the European bison (wisent), lynx, wolf, and white-tailed eagle. The park protects one of the most significant wetland ecosystems in Europe.', 'Pripyat River wetlands with primeval forests — bison, wolves, and white-tailed eagles.', 'Turov, Zhitkovichi District, Gomel Oblast', 'Turov', 'Gomel Oblast', 52.0500000, 27.7333000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/36.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:42');
INSERT INTO `attractions` VALUES (37, 'Berezina Biosphere Reserve', 'Berezina Biosphere Reserve', NULL, 'A UNESCO Biosphere Reserve covering one of the largest river floodplain systems in Europe. The Berezina River and its tributaries support exceptional biodiversity. The reserve is home to the European bison and Eurasian lynx, along with 280 species of birds. Visitor facilities include nature trails, observation towers, and guided boat tours through the floodplain.', 'UNESCO Biosphere Reserve — Europe\'s largest river floodplain ecosystem with bison.', 'Zhonka, Berezina District, Minsk Oblast', 'Zhonka', 'Minsk Oblast', 53.5000000, 28.5000000, 'nature', 'Spring, Summer, Autumn', '09:00 - 17:00', 2.00, '/static/images/attractions/37.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (38, 'Turov Riverside (Bison Crossing)', 'Turov Riverside', NULL, 'A picturesque section of the Pripyat River at Turov, famous for its high concentration of European bison that cross the river at this location. The town of Turov is one of the oldest in Belarus and the surrounding floodplain offers excellent wildlife observation. A prime destination for nature photographers.', 'Pripyat River at Turov — famous for bison crossing, one of Belarus oldest towns.', 'Turov, Zhitkovichi District, Gomel Oblast', 'Turov', 'Gomel Oblast', 52.0667000, 27.7333000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/38.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (39, 'Khotlitsa River Canyon', 'Khotlitsa River Canyon', NULL, 'A scenic canyon formed by the Khotitsa River in the Vitebsk Oblast, featuring steep Devonian sandstone cliffs reaching 20-40 metres in height, forested slopes, and hiking trails along the river. One of the most dramatic natural landscapes in northern Belarus, with geological strata visible in the cliff walls.', 'Dramatic sandstone river canyon — steep cliffs and spectacular hiking trails.', 'Beshankovichy District, Vitebsk Oblast', 'Beshankovichy', 'Vitebsk Oblast', 55.0333000, 29.3333000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/39.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:44');
INSERT INTO `attractions` VALUES (40, 'Mikashevichy Chalk Quarries', 'Mikashevichy Chalk Quarries', NULL, 'Dramatic white chalk quarry walls create an otherworldly landscape near the village of Mikashevichy. The exposed chalk layers, some millions of years old, make for striking geological formations. Popular with photographers, hikers, and geology enthusiasts.', 'White chalk quarry walls — striking geological formations and landscape photography.', 'Mikashevichy, Zhlobin District, Gomel Oblast', 'Mikashevichy', 'Gomel Oblast', 52.9167000, 29.8333000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/40.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (41, 'National Library of Belarus', 'National Library of Belarus', NULL, 'One of the most recognizable symbols of modern Minsk, this rhombicuboctahedron-shaped building holds over 10 million items and features a rooftop observation deck with panoramic 360-degree views of Minsk. The building is illuminated at night with a massive LED display. The library is a major research institution and hosts cultural events, exhibitions, and conferences.', 'Iconic diamond-shaped building — 10M+ items, rooftop observation deck, symbol of modern Minsk.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9317000, 27.6406000, 'architecture', 'All seasons', '09:00 - 21:00', 5.00, '/static/images/attractions/41.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 1, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (42, 'Independence Avenue (Praspiekt Niezaliežnasci)', 'Independence Avenue, Minsk', NULL, 'The main thoroughfare of Minsk, stretching 15 kilometres from Victory Square to the southern outskirts. Lined with Stalinist neoclassical buildings, government institutions, department stores, theatres, and cafes. Walking this single avenue gives a comprehensive overview of Minsk\'s Soviet-era monumental architecture and modern city life. Key landmarks include Independence Square, the Government House, and the GUM department store.', '15km main boulevard — Stalinist neoclassical architecture, government buildings, and city life.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9167000, 27.5667000, 'architecture', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/42.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (43, 'Minsk Metro (Ornate Stations)', 'Minsk Metro Stations', NULL, 'The Minsk Metro is renowned for its ornate underground stations — many function as underground palaces with marble columns, crystal chandeliers, stained glass panels, and mosaics depicting Belarusian history, culture, and industry. Notable stations include Kastryčnickaja (October), Nyamiha, and Uschod. The metro runs from 05:30 to 01:00 daily.', 'Underground palaces — marble, chandeliers, stained glass, and Belarusian history mosaics.', 'Minsk Metro', 'Minsk', 'Minsk', 53.9167000, 27.5667000, 'architecture', 'All seasons', '05:30 - 01:00', 0.65, '/static/images/attractions/43.jpg', NULL, 4.60, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (44, 'Upper Town (Vyšni Horad)', 'Upper Town, Minsk', NULL, 'The oldest surviving district of Minsk, rebuilt after WWII but retaining the baroque layout and scale of the 17th-century town. Features the Holy Trinity Cathedral, the reconstructed Town Hall, the former Bernardine Monastery, and riverside terraces. The best spot for outdoor dining in summer.', 'Minsk\'s oldest district — baroque churches, cobblestone streets, and riverside terraces.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9053000, 27.5558000, 'architecture', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/44.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (45, 'Gorky Central Park of Culture and Rest', 'Gorky Park, Minsk', NULL, 'The most popular park in Minsk, located along the Svislach River. Features amusement rides, sports facilities, a lake with boat rentals, walking and cycling paths, cafes, and regular cultural events and concerts. The park connects to Victory Park and the Svislach embankment promenade.', 'Minsk\'s most popular park — rides, lake, boat rentals, sports facilities, and concerts.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9167000, 27.5333000, 'park', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/45.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (46, 'Minsk Sea Reservoir', 'Minsk Sea', NULL, 'A large artificial reservoir on the Svislach River, popular for swimming, windsurfing, and beach recreation. The area includes sandy beaches, campgrounds, and hiking trails. The reservoir is also known as a spot for ice sailing in winter.', 'Large artificial reservoir — swimming, windsurfing, beach recreation, and ice sailing in winter.', 'Minsk District, Minsk Oblast', 'Minsk', 'Minsk Oblast', 53.9500000, 27.5000000, 'nature', 'Summer', 'Open all day', 0.00, '/static/images/attractions/46.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (47, 'Pripyat Floodplain Landscape Reserve', 'Pripyat Floodplain Reserve', NULL, 'A nature reserve protecting the unique floodplain landscape of the Pripyat River wetlands. Features oxbow lakes, marshes, floodplain forests, and meadows teeming with waterfowl and aquatic life. An important ecological corridor for migratory birds between Central Europe and Russia.', 'Pripyat River wetlands — oxbow lakes, waterfowl, and migratory bird corridor.', 'Drahichyn District, Brest Oblast', 'Drahichyn', 'Brest Oblast', 52.1833000, 25.1500000, 'nature', 'Spring, Summer', 'Open all day', 0.00, '/static/images/attractions/47.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (48, 'Yelnya Bog', 'Yelnya Peat Bog', NULL, 'The largest high moor (bog) in Belarus, covering over 20,000 hectares. Formed during the glacial period, Yelnya is one of the oldest ecosystems in Europe. The bog has preserved a unique environment with sphagnum mosses, bog plants, and specialized wildlife that has existed continuously for millennia.', 'Belarus\'s largest high moor — ancient ecosystem formed during the glacial period.', 'Krychaw District, Gomel Oblast', 'Krychaw', 'Gomel Oblast', 53.7000000, 31.8500000, 'nature', 'Summer', 'Open all day', 0.00, '/static/images/attractions/48.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (49, 'Mogilev Botanical Garden', 'Mogilev Botanical Garden', NULL, 'A botanical garden covering 67 hectares featuring plant collections from Belarus and around the world. Includes thematic sections, greenhouses, an ornamental pond, and a nature education centre. Known for its collection of lilies and ornamental shrubs.', '67-hectare botanical garden — ornamental plants, greenhouses, and a nature education centre.', 'Mogilev, Belarus', 'Mogilev', 'Mogilev Oblast', 53.9333000, 30.3667000, 'nature', 'Spring, Summer, Autumn', '08:00 - 18:00', 2.00, '/static/images/attractions/49.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (50, 'Vitebsk Botanical Garden', 'Vitebsk Botanical Garden', NULL, 'A botanical garden established in 1910, featuring extensive plant collections, ornamental gardens, an arboretum, and greenhouses. Known for its outstanding displays of roses, lilies, and hostas. The garden sits on the banks of the Western Dvina River.', '1910 botanical garden — renowned rose, lily, and hosta collections on the Western Dvina.', 'Vitebsk, Belarus', 'Vitebsk', 'Vitebsk Oblast', 55.1833000, 30.2167000, 'nature', 'Spring, Summer, Autumn', '08:00 - 18:00', 2.00, '/static/images/attractions/50.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (51, 'Grodno Old Town', 'Grodno Old Town', NULL, 'Grodno is one of the few Belarusian cities with a well-preserved historic old town, featuring buildings from the 13th to 19th centuries. Highlights include the former Royal Castle site, the old market square, the New Town area with Polish-era merchant houses, and the Old Town\'s cobblestone streets. The city survived WWII largely intact and retains a genuine historical atmosphere.', 'Well-preserved old town — buildings from the 13th to 19th centuries, genuine historical atmosphere.', 'Grodno, Belarus', 'Grodno', 'Grodno Oblast', 53.6833000, 23.8333000, 'architecture', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/51.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (52, 'Polotsk Old Town', 'Polotsk Old Town', NULL, 'Polotsk is one of the oldest cities in Belarus, founded in the 9th century as the capital of a medieval principality. Its old town contains historic churches, merchant houses, the ruins of ancient fortifications, and the 12th-century Sophia Cathedral. Polotsk was a major centre of trade and culture in medieval Eastern Europe.', 'One of Belarus\'s oldest cities — 9th-century principality capital with medieval churches.', 'Polotsk, Vitebsk Oblast', 'Polotsk', 'Vitebsk Oblast', 55.5000000, 28.7667000, 'architecture', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/52.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (53, 'Krychaw Old Town', 'Krychaw', NULL, 'An ancient town on the Sozh River founded in the 12th century. Krychaw is known for its wooden churches, historic market square, the Trinity Monastery on the riverbank, and scenic views along the Sozh. The town has a quiet, artistic character and is popular with painters and photographers.', '12th-century town on the Sozh River — wooden churches and the Trinity Monastery.', 'Krychaw, Gomel Oblast', 'Krychaw', 'Gomel Oblast', 53.7167000, 31.7167000, 'architecture', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/53.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (54, 'Pyetrykaw', 'Pyetrykaw', NULL, 'One of the oldest towns in Belarus, located at the confluence of the Dnieper and Sozh rivers. Features historic churches, an old market square, and a museum of local history. The surrounding countryside is known for its landscapes and traditional villages.', 'One of Belarus\'s oldest towns — at the confluence of the Dnieper and Sozh rivers.', 'Pyetrykaw, Gomel Oblast', 'Pyetrykaw', 'Gomel Oblast', 52.1333000, 28.5000000, 'architecture', 'All seasons', 'Open all day', 0.00, '/static/images/attractions/54.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:48');
INSERT INTO `attractions` VALUES (55, 'Slavianski Bazaar Amphitheatre', 'Slavianski Bazaar Venue', NULL, 'The annual Slavianski Bazaar international arts festival in Vitebsk is one of the largest cultural events in Eastern Europe, held every July since 1992. The festival attracts performers and visitors from across the Slavic world and beyond. The main amphitheatre venue seats thousands and hosts concerts, theatre performances, and dance competitions.', 'Venue for the annual Slavianski Bazaar — the largest cultural festival in Eastern Europe.', 'Vitebsk, Belarus', 'Vitebsk', 'Vitebsk Oblast', 55.1967000, 30.2100000, 'architecture', 'Summer (July)', 'Festival season only', 10.00, '/static/images/attractions/55.jpg', NULL, 4.50, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (56, 'Vitebsk Regional Museum', 'Vitebsk Regional Museum', NULL, 'Located in the former Governorate building, this museum holds collections on the history of Vitebsk Oblast from prehistoric times through World War II. Includes archaeology, ethnography, fine arts, and a notable collection related to Marc Chagall\'s Vitebsk period.', 'History of Vitebsk Oblast — archaeology, Chagall period, and regional culture.', 'Vitebsk, Belarus', 'Vitebsk', 'Vitebsk Oblast', 55.1900000, 30.2050000, 'museum', 'All seasons', '10:00 - 17:00 (Wed-Sun)', 3.00, '/static/images/attractions/56.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (57, 'Brest Regional Museum', 'Brest Regional Museum', NULL, 'A regional museum showcasing the history, nature, and culture of the Brest Oblast from prehistoric times to the present day. Features exhibits on the region\'s archaeology, flora and fauna, and the history of the borderland.', 'Brest Oblast history, nature, and culture — from prehistoric times to today.', 'Brest, Belarus', 'Brest', 'Brest Oblast', 52.0983000, 23.6917000, 'museum', 'All seasons', '10:00 - 18:00 (Tue-Sun)', 3.00, '/static/images/attractions/57.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 1, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-06 09:53:50');
INSERT INTO `attractions` VALUES (58, 'Vileyka Lake District', 'Vileyka Lake District', NULL, 'A cluster of small glacial lakes around the town of Vileyka in northern Minsk Oblast. Known for its tranquil environment, excellent fishing, and opportunities for kayaking. The lakes were formed by glacial activity during the last Ice Age and vary in depth and character.', 'Glacial lake cluster near Vileyka — fishing, kayaking, and a tranquil environment.', 'Vileyka, Minsk Oblast', 'Vileyka', 'Minsk Oblast', 54.7500000, 26.9000000, 'nature', 'Summer', 'Open all day', 0.00, '/static/images/attractions/58.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (59, 'Sozh River Valley', 'Sozh River Valley', NULL, 'The Sozh River, a tributary of the Dnieper, flows through picturesque landscapes of Belarus. The river valley is known for its scenic beauty, historic villages, and opportunities for boating and fishing. The valley has been inhabited since ancient times and contains numerous archaeological sites.', 'Scenic Sozh River valley — historic villages, boating, and fishing.', 'Krychaw, Gomel Oblast', 'Krychaw', 'Gomel Oblast', 53.7167000, 31.7167000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/59.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (60, 'Svislach River Embankment', 'Svislach River Embankment, Minsk', NULL, 'A scenic riverside promenade along the Svislach River in central Minsk. Features fountains, sculptures, landscaped parks, and illuminated walkways. The embankment connects many of the city\'s major landmarks and is especially beautiful in the evening when the buildings are illuminated.', 'Scenic riverside promenade — fountains, sculptures, and illuminated walkways in central Minsk.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9083000, 27.5550000, 'park', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/60.jpg', NULL, 4.40, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (61, 'Loshitsa Park (Mikhail Lositsky Estate)', 'Loshitsa Park, Minsk', NULL, 'A historic park and estate complex featuring a neoclassical manor house, French-style regular garden, and natural landscape park. The estate belonged to various noble families and now serves as a cultural venue with concerts, exhibitions, and festivals.', 'Historic estate park — neoclassical manor, French-style garden, cultural venue.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.8833000, 27.5500000, 'park', 'Spring, Summer, Autumn', '08:00 - 22:00', 0.00, '/static/images/attractions/61.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (62, 'Augustow Canal', 'Augustow Canal', NULL, 'A UNESCO tentative list site built in 1823-1839 to connect the Neman River with the Vistula River. A remarkable feat of 19th-century engineering, the canal includes 18 locks and enables navigation between the Baltic and Black Sea basins. The surrounding landscape of forests and lakes makes it popular for canoeing, cycling, and nature observation.', '19th-century canal — engineering feat with 18 locks, popular for canoeing and cycling.', 'Augustow Canal, Grodno Oblast', 'Augustow', 'Grodno Oblast', 53.8333000, 23.0000000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/62.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (63, 'Berezina Canal Locks', 'Berezina Canal Locks', NULL, 'A system of historic canal locks built in the 18th-19th centuries as part of the Berezina waterway connecting the Dnieper and Daugava basins. The engineering feat is considered one of the most impressive canal systems in Eastern Europe. Surrounded by forests and wetlands, it is popular with kayakers and history enthusiasts.', '18th-century canal lock system — engineering feat connecting major river basins.', 'Berezina Canal, Minsk Oblast', 'Borisov', 'Minsk Oblast', 54.2500000, 28.5000000, 'architecture', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/63.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (64, 'Polotsk Museum of Local History', 'Polotsk Museum of Local History', NULL, 'Housed in the 18th-century Jesuit college, this museum showcases the 1,000-year history of Polotsk — one of the oldest cities in Belarus and the former capital of a medieval principality. Collections include archaeology from the Viking Age, medieval manuscripts, and documents relating to the Polotsk Principality.', '1,000-year history of Polotsk — housed in an 18th-century Jesuit college.', 'Polotsk, Vitebsk Oblast', 'Polotsk', 'Vitebsk Oblast', 55.5000000, 28.8000000, 'museum', 'All seasons', '10:00 - 17:00 (Wed-Sun)', 3.00, '/static/images/attractions/64.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (65, 'Dudutki Folk Museum', 'Dudutki Open-Air Museum', NULL, 'An open-air ethnographic museum south of Minsk where visitors can try traditional crafts — pottery, weaving, blacksmithing, cheese-making, and samogon (moonshine) distillation — taste traditional Belarusian food, ride horses, and experience rural life. One of the most popular attractions for families.', 'Open-air ethnographic museum — traditional crafts, food, and horse riding south of Minsk.', 'Dukora, Pukhovichi District, Minsk Oblast', 'Dukora', 'Minsk Oblast', 53.6167000, 28.0333000, 'museum', 'Spring, Summer, Autumn', '10:00 - 17:00', 6.00, '/static/images/attractions/65.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (66, 'Copernicus House, Polotsk', 'Copernicus House, Polotsk', NULL, 'The presumed birthplace of Nicolaus Copernicus (1473-1543), the astronomer who proposed the heliocentric model of the solar system. Copernicus was born in Torun, but his maternal uncle Lucas Watzenrode lived and worked in Polotsk as a canon of the cathedral chapter. The building houses a museum dedicated to Copernicus\'s scientific work and the intellectual history of Renaissance Europe.', 'Museum dedicated to Copernicus — linked to his maternal family in Polotsk.', 'Polotsk, Vitebsk Oblast', 'Polotsk', 'Vitebsk Oblast', 55.5000000, 28.7667000, 'museum', 'All seasons', '10:00 - 17:00 (Tue-Sun)', 3.00, '/static/images/attractions/66.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (67, 'Drahichyn Forest', 'Drahichyn Forest', NULL, 'A vast forested area near Drahichyn, part of the Pripyat floodplain landscape reserve. The forest is home to elk, deer, wild boar, and numerous bird species. Nature trails allow visitors to explore the ecosystem without disturbing sensitive habitats.', 'Vast Pripyat floodplain forest — elk, deer, wild boar, and nature trails.', 'Drahichyn, Brest Oblast', 'Drahichyn', 'Brest Oblast', 52.2000000, 25.1500000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/67.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (68, 'Rossony Lake District', 'Rossony', NULL, 'A remote area in the Vitebsk Oblast near the borders with Latvia and Russia, known for its beautiful forested landscapes and interconnected lake system. Popular with nature lovers, kayakers, and those seeking solitude in nature. Remote and unspoiled by mass tourism.', 'Remote lake district near borders — kayaking, nature observation, and solitude.', 'Rossony, Vitebsk Oblast', 'Rossony', 'Vitebsk Oblast', 56.0000000, 28.8333000, 'nature', 'Summer', 'Open all day', 0.00, '/static/images/attractions/68.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (69, 'Logoisk Forests', 'Logoisk', NULL, 'A forested area of central Minsk Oblast that was once the preferred hunting ground of the Russian tsars. The forests are now part of a protected area near the Berezina Biosphere Reserve, offering hiking, birdwatching, and foraging. Rich in mushrooms and berries in season.', 'Former tsarist hunting grounds — forests near Berezina Reserve, mushroom picking.', 'Logoisk, Minsk Oblast', 'Logoisk', 'Minsk Oblast', 53.9833000, 27.7000000, 'nature', 'Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/69.jpg', NULL, 3.90, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (70, 'Svislach Hills', 'Svislach Hills', NULL, 'Rolling hills along the Svislach River north of Minsk offering scenic hiking opportunities. The area is known for its beautiful autumn foliage, panoramic views over the river valley, and proximity to the historic town of Smolevichi.', 'Rolling hills north of Minsk — scenic hiking and beautiful autumn foliage.', 'Smolevichi District, Minsk Oblast', 'Smolevichi', 'Minsk Oblast', 54.1500000, 26.8333000, 'nature', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/70.jpg', NULL, 3.90, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (71, 'Minsk Central Railway Station', 'Minsk Central Railway Station', NULL, 'The main railway station of Minsk, a major hub serving connections across Belarus and international routes to Moscow, Warsaw, Vilnius, and Berlin. The current building dates from 1993 and replaced the original Soviet-era station. The hall features murals depicting Belarusian history and culture.', 'Minsk main railway hub — connections across Belarus and international routes.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.8858000, 27.5472000, 'architecture', 'All seasons', 'Open 24 hours', 0.00, '/static/images/attractions/71.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (72, 'Minsk Drama Theater', 'Minsk Drama Theater', NULL, 'One of the oldest theatres in Belarus, founded in 1888. The current building in eclectic style with elements of neoclassicism opened in 1902. It is the national theatre of Belarus and hosts productions of classic and contemporary drama in the Belarusian and Russian languages.', 'National theatre founded in 1888 — eclectic architecture, classic and contemporary drama.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9111000, 27.5656000, 'architecture', 'All seasons', 'By performance', 15.00, '/static/images/attractions/72.jpg', NULL, 4.20, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (73, 'Motherland Monument', 'Motherland Monument', NULL, 'The massive Motherland Monument in Minsk, one of the tallest structures in Belarus, stands as a symbol of victory and patriotism. The monument complex includes the figure of the Motherland, eternal flame, and a WWII memorial museum. The view from the top platform offers sweeping panoramas of Minsk.', 'Massive WWII monument — sweeping views of Minsk from the top platform.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9083000, 27.5725000, 'architecture', 'All seasons', '10:00 - 18:00', 3.00, '/static/images/attractions/73.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (74, 'Minsk Sports Complex (Minsk Arena)', 'Minsk Arena', NULL, 'A modern multi-purpose sports and entertainment complex with a 15,000-seat ice arena, velodrome, swimming pool, and fitness centre. Hosted events at the 2014 Ice Hockey World Championship. Open daily for sports activities and events.', 'Modern multi-sport complex — 15,000-seat arena, velodrome, swimming pool.', 'Minsk, Belarus', 'Minsk', 'Minsk', 53.9367000, 27.4817000, 'architecture', 'All seasons', '08:00 - 22:00', 10.00, '/static/images/attractions/74.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (75, 'Babruysk Fortress', 'Babruysk Fortress', NULL, 'An 18th-century fortress on the Berezina River built during the Russian Empire period. The fortress played a role in the Battle of Berezina during the Napoleonic Wars and later served as a military installation. Partially preserved walls and bastions can still be seen in the city centre of Babruysk.', '18th-century fortress on the Berezina River — played a role in the Napoleonic Wars.', 'Babruysk, Mogilev Oblast', 'Babruysk', 'Mogilev Oblast', 53.1333000, 29.2500000, 'castle', 'All seasons', 'External viewing only', 0.00, '/static/images/attractions/75.jpg', NULL, 3.80, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (76, 'Bruzdzitsy Ancient Settlement', 'Bruzdzitsy Ancient Settlement', NULL, 'An archaeological site dating to the 6th-4th centuries BCE, containing the remains of an ancient settlement of the Bielanovichy culture. The site provides important insights into early Iron Age life in the region. Ongoing excavations continue to reveal more about this prehistoric community.', 'Iron Age archaeological site — 6th-4th century BCE ancient settlement.', 'Bruzdzitsy, Grodno Oblast', 'Bruzdzitsy', 'Grodno Oblast', 53.7500000, 24.5000000, 'memorial', 'Spring, Summer, Autumn', 'Open all day', 0.00, '/static/images/attractions/76.jpg', NULL, 3.90, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (77, 'Muravanka Church (Fortress Church)', 'Muravanka Church', NULL, 'A 16th-century Roman Catholic fortress church (defensive church) in the village of Muravanka. One of the finest examples of fortified churches in Belarus, built during the time of the Polish-Lithuanian Commonwealth. The church served both as a place of worship and a defensive refuge during times of conflict.', '16th-century fortified church — defensive architecture of the Polish-Lithuanian Commonwealth.', 'Muravanka, Pruzhany District, Brest Oblast', 'Muravanka', 'Brest Oblast', 52.4500000, 24.3000000, 'church', 'Spring, Summer, Autumn', 'By arrangement', 0.00, '/static/images/attractions/77.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (78, 'Kasianikitsy Church', 'Kasianikitsy Church', NULL, 'A 16th-century Orthodox church famous for its unique architectural design — the interior is structured in the shape of an equilateral cross, making it one of the most visually distinctive churches in Belarus. Located in a quiet rural setting near the border with Lithuania.', '16th-century Orthodox church — unique equilateral cross-shaped interior design.', 'Kasianikitsy, Vitebsk Oblast', 'Kasianikitsy', 'Vitebsk Oblast', 55.6500000, 29.0500000, 'church', 'Spring, Summer, Autumn', 'By arrangement', 0.00, '/static/images/attractions/78.jpg', NULL, 4.10, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (79, 'Holy Trinity Cathedral, Vitebsk', 'Holy Trinity Cathedral, Vitebsk', NULL, 'A historic Russian Revival Orthodox cathedral built between 1750 and 1772. It is the oldest stone building in Vitebsk and one of the most significant religious monuments in the region. The cathedral features baroque-influenced iconostases and a notable collection of 18th-century icons.', 'Oldest stone building in Vitebsk — Russian Revival Orthodox cathedral from 1750-1772.', 'Vitebsk, Belarus', 'Vitebsk', 'Vitebsk Oblast', 55.1917000, 30.2033000, 'church', 'All seasons', '07:00 - 19:00', 0.00, '/static/images/attractions/79.jpg', NULL, 4.00, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');
INSERT INTO `attractions` VALUES (80, 'Residence of Ded Moroz (Father Frost)', 'Father Frost Estate', NULL, 'The estate of Ded Moroz (Belarusian/Slavic Grandfather Frost) within the Belovezhskaya Pushcha National Park. Draws approximately 150,000 visitors annually, making it one of the most popular tourist attractions in Belarus. Features animated fairy-tale characters carved from wood, a workshop where gifts are made, and a New Year\'s train. Open year-round but busiest during the winter holiday season.', 'Residence of Slavic Grandfather Frost — 150,000 visitors annually, fairy-tale wood carvings.', 'Kamieniuki, Brest Oblast', 'Kamieniuki', 'Brest Oblast', 52.5833000, 23.8667000, 'architecture', 'All seasons (best winter)', '09:00 - 17:00', 5.00, '/static/images/attractions/80.jpg', NULL, 4.30, 0, 0.000, 0, 0, 0, 0, 0, 1, NULL, '2026-07-04 19:24:16', '2026-07-04 19:24:17');

-- ----------------------------
-- Table structure for login_events
-- ----------------------------
DROP TABLE IF EXISTS `login_events`;
CREATE TABLE `login_events`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NULL DEFAULT NULL,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `event_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `user_agent` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `detail` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_events_ip`(`ip_address` ASC) USING BTREE,
  INDEX `idx_events_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_events_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_events_event_type`(`event_type` ASC) USING BTREE,
  CONSTRAINT `login_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of login_events
-- ----------------------------
INSERT INTO `login_events` VALUES (1, 3, '123', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/3.6.21 Chrome/142.0.7444.265 Electron/39.8.1 Safari/537.36', 'success', 'Login success', '2026-07-04 19:31:50');
INSERT INTO `login_events` VALUES (2, 2, NULL, 'register', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'success', 'Account created', '2026-06-04 19:45:50');
INSERT INTO `login_events` VALUES (3, 2, NULL, 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'success', 'Login from Chrome on Windows', '2026-06-05 19:45:50');
INSERT INTO `login_events` VALUES (4, 2, NULL, 'login', '192.168.1.42', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'success', 'Login from iPhone Safari', '2026-06-20 19:45:50');
INSERT INTO `login_events` VALUES (5, 2, NULL, 'password_changed', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'success', 'Password updated', '2026-06-27 19:45:50');
INSERT INTO `login_events` VALUES (6, 2, NULL, 'login_failed', '203.0.113.45', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36', 'failure', 'Wrong password', '2026-07-02 19:45:50');
INSERT INTO `login_events` VALUES (7, 2, 'demo', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'success', 'Login success', '2026-07-04 19:46:12');
INSERT INTO `login_events` VALUES (8, NULL, 'demo', 'login_failed', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'failure', 'Wrong password', '2026-07-04 19:46:12');
INSERT INTO `login_events` VALUES (9, 3, '123', 'logout', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/3.6.21 Chrome/142.0.7444.265 Electron/39.8.1 Safari/537.36', 'success', 'User logged out', '2026-07-05 06:50:45');
INSERT INTO `login_events` VALUES (10, 3, '123', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/3.6.21 Chrome/142.0.7444.265 Electron/39.8.1 Safari/537.36', 'success', 'Login success', '2026-07-05 06:50:49');
INSERT INTO `login_events` VALUES (11, 2, 'demo', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'success', 'Login success', '2026-07-05 06:55:37');
INSERT INTO `login_events` VALUES (12, 2, 'demo', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'success', 'Login success', '2026-07-05 06:56:20');
INSERT INTO `login_events` VALUES (13, 2, 'demo', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'success', 'Login success', '2026-07-05 06:58:33');
INSERT INTO `login_events` VALUES (14, 2, 'demo', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.8737', 'success', 'Login success', '2026-07-05 06:58:49');
INSERT INTO `login_events` VALUES (15, 3, '123', 'logout', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/3.6.21 Chrome/142.0.7444.265 Electron/39.8.1 Safari/537.36', 'success', 'User logged out', '2026-07-05 09:11:27');
INSERT INTO `login_events` VALUES (16, 1, 'admin', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/3.6.21 Chrome/142.0.7444.265 Electron/39.8.1 Safari/537.36', 'success', 'Login success', '2026-07-05 09:11:31');
INSERT INTO `login_events` VALUES (17, 3, '123', 'login', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36', 'success', 'Login success', '2026-07-06 09:53:57');

-- ----------------------------
-- Table structure for login_tokens
-- ----------------------------
DROP TABLE IF EXISTS `login_tokens`;
CREATE TABLE `login_tokens`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `token` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `refresh_token` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `device_info` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  `revoked_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_tokens_expires_at`(`expires_at` ASC) USING BTREE,
  INDEX `idx_tokens_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `login_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of login_tokens
-- ----------------------------

-- ----------------------------
-- Table structure for question_upvotes
-- ----------------------------
DROP TABLE IF EXISTS `question_upvotes`;
CREATE TABLE `question_upvotes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_question_user_upvote`(`question_id` ASC, `user_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_qup_question_id`(`question_id` ASC) USING BTREE,
  CONSTRAINT `question_upvotes_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `question_upvotes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of question_upvotes
-- ----------------------------
INSERT INTO `question_upvotes` VALUES (1, 1, 2, '2026-07-03 18:21:21');
INSERT INTO `question_upvotes` VALUES (2, 2, 2, '2026-07-03 18:21:21');

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NOT NULL,
  `title` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `view_count` int NOT NULL,
  `answer_count` int NOT NULL,
  `upvote_count` int NOT NULL,
  `has_accepted_answer` tinyint(1) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_questions_status`(`status` ASC) USING BTREE,
  INDEX `idx_questions_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_questions_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_questions_attraction_id`(`attraction_id` ASC) USING BTREE,
  CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `questions_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of questions
-- ----------------------------
INSERT INTO `questions` VALUES (1, 2, 1, 'What is the best time of year to visit Mir Castle?', 'Planning a trip to Mir Castle and wondering when would be the best time to visit for photography and fewer crowds.', 45, 1, 3, 1, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL);
INSERT INTO `questions` VALUES (2, 2, 3, 'Are there English guides available at Belovezhskaya Pushcha?', 'My family does not speak Russian or Belarusian. Are there English-speaking guides for the forest tour?', 32, 0, 1, 0, 'published', NULL, '2026-07-04 19:24:17', '2026-07-04 19:24:17', NULL);

-- ----------------------------
-- Table structure for rating_dimensions
-- ----------------------------
DROP TABLE IF EXISTS `rating_dimensions`;
CREATE TABLE `rating_dimensions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NOT NULL,
  `scenery` smallint NULL DEFAULT NULL,
  `service` smallint NULL DEFAULT NULL,
  `value` smallint NULL DEFAULT NULL,
  `facilities` smallint NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_attraction_dimension`(`user_id` ASC, `attraction_id` ASC) USING BTREE,
  INDEX `idx_dim_attraction_id`(`attraction_id` ASC) USING BTREE,
  CONSTRAINT `rating_dimensions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `rating_dimensions_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of rating_dimensions
-- ----------------------------

-- ----------------------------
-- Table structure for ratings
-- ----------------------------
DROP TABLE IF EXISTS `ratings`;
CREATE TABLE `ratings`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NOT NULL,
  `score` smallint NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_attraction_rating`(`user_id` ASC, `attraction_id` ASC) USING BTREE,
  INDEX `idx_ratings_attraction_id`(`attraction_id` ASC) USING BTREE,
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 39 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of ratings
-- ----------------------------
INSERT INTO `ratings` VALUES (13, 2, 66, 3, '2026-05-31 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (14, 2, 1, 5, '2026-06-22 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (15, 2, 44, 2, '2026-06-11 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (16, 2, 32, 4, '2026-05-04 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (17, 2, 80, 5, '2026-06-06 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (18, 2, 63, 3, '2026-05-21 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (19, 2, 29, 3, '2026-05-15 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (20, 2, 39, 5, '2026-05-27 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (21, 2, 17, 2, '2026-05-07 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (22, 2, 49, 2, '2026-06-12 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (23, 2, 25, 4, '2026-05-19 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (24, 2, 61, 4, '2026-05-25 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (25, 2, 33, 5, '2026-05-26 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (26, 2, 64, 2, '2026-06-03 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (27, 2, 75, 3, '2026-05-10 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (28, 2, 40, 3, '2026-06-15 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (29, 2, 21, 5, '2026-05-19 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (30, 2, 73, 5, '2026-06-28 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (31, 2, 11, 3, '2026-05-17 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (32, 2, 14, 5, '2026-06-13 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (33, 2, 30, 5, '2026-05-27 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (34, 2, 22, 5, '2026-05-11 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (35, 2, 16, 5, '2026-06-14 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (36, 2, 34, 5, '2026-06-08 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (37, 2, 50, 5, '2026-06-10 18:29:16', '2026-07-03 18:29:16');
INSERT INTO `ratings` VALUES (38, 3, 1, 5, '2026-07-05 06:48:28', '2026-07-05 06:48:28');

-- ----------------------------
-- Table structure for review_helpful_votes
-- ----------------------------
DROP TABLE IF EXISTS `review_helpful_votes`;
CREATE TABLE `review_helpful_votes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `review_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `is_helpful` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_review_user_vote`(`review_id` ASC, `user_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_votes_review_id`(`review_id` ASC) USING BTREE,
  CONSTRAINT `review_helpful_votes_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `reviews` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `review_helpful_votes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of review_helpful_votes
-- ----------------------------

-- ----------------------------
-- Table structure for review_replies
-- ----------------------------
DROP TABLE IF EXISTS `review_replies`;
CREATE TABLE `review_replies`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `review_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `like_count` int NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_replies_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_replies_review_id`(`review_id` ASC) USING BTREE,
  CONSTRAINT `review_replies_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `reviews` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `review_replies_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of review_replies
-- ----------------------------

-- ----------------------------
-- Table structure for reviews
-- ----------------------------
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NOT NULL,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rating` smallint NOT NULL,
  `travel_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `travel_date` date NULL DEFAULT NULL,
  `travel_month` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `helpful_count` int NOT NULL,
  `reply_count` int NOT NULL,
  `sentiment_label` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sentiment_score` decimal(4, 3) NULL DEFAULT NULL,
  `ai_processed` tinyint(1) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_attraction_id`(`attraction_id` ASC) USING BTREE,
  INDEX `idx_rating`(`rating` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 50 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reviews
-- ----------------------------
INSERT INTO `reviews` VALUES (37, 2, 44, 'Quick note on Upper Town (Vyšni Horad)', 'Loved this place, would come back again.', 5, 'couple', '2026-04-06', 'April', 12, 0, 'positive', 0.440, 1, 'published', '127.0.0.1', '2026-04-06 18:29:16', '2026-04-06 18:29:16', NULL);
INSERT INTO `reviews` VALUES (38, 2, 4, 'Quick note on Struve Geodetic Arc (Belarus Points)', 'Loved this place, would come back again.', 5, 'couple', '2026-05-13', 'May', 12, 0, 'positive', 0.670, 1, 'published', '127.0.0.1', '2026-05-13 18:29:16', '2026-05-13 18:29:16', NULL);
INSERT INTO `reviews` VALUES (39, 2, 3, 'Quick note on Belovezhskaya Pushcha National Park', 'Loved this place, would come back again.', 4, 'couple', '2026-05-13', 'May', 3, 0, 'positive', 0.830, 1, 'published', '127.0.0.1', '2026-05-13 18:29:16', '2026-05-13 18:29:16', NULL);
INSERT INTO `reviews` VALUES (40, 2, 22, 'Quick note on Berestye Archaeological Museum', 'Loved this place, would come back again.', 5, 'family', '2026-05-02', 'May', 12, 0, 'positive', 0.610, 1, 'published', '127.0.0.1', '2026-05-02 18:29:16', '2026-05-02 18:29:16', NULL);
INSERT INTO `reviews` VALUES (41, 2, 75, 'Quick note on Babruysk Fortress', 'Loved this place, would come back again.', 5, 'family', '2026-06-25', 'June', 6, 0, 'positive', 0.840, 1, 'published', '127.0.0.1', '2026-06-25 18:29:16', '2026-06-25 18:29:16', NULL);
INSERT INTO `reviews` VALUES (42, 2, 31, 'Quick note on Gomel Palace and Park Ensemble', 'Loved this place, would come back again.', 4, 'solo', '2026-06-24', 'June', 6, 0, 'positive', 0.440, 1, 'published', '127.0.0.1', '2026-06-24 18:29:16', '2026-06-24 18:29:16', NULL);
INSERT INTO `reviews` VALUES (43, 2, 39, 'Quick note on Khotlitsa River Canyon', 'Loved this place, would come back again.', 4, 'solo', '2026-05-07', 'May', 5, 0, 'positive', 0.730, 1, 'published', '127.0.0.1', '2026-05-07 18:29:16', '2026-05-07 18:29:16', NULL);
INSERT INTO `reviews` VALUES (44, 2, 46, 'Quick note on Minsk Sea Reservoir', 'Loved this place, would come back again.', 3, 'couple', '2026-06-18', 'June', 10, 0, 'positive', 0.820, 1, 'published', '127.0.0.1', '2026-06-18 18:29:16', '2026-06-18 18:29:16', NULL);
INSERT INTO `reviews` VALUES (45, 2, 79, 'Quick note on Holy Trinity Cathedral, Vitebsk', 'Loved this place, would come back again.', 4, 'couple', '2026-04-17', 'April', 1, 0, 'positive', 0.540, 1, 'published', '127.0.0.1', '2026-04-17 18:29:16', '2026-04-17 18:29:16', NULL);
INSERT INTO `reviews` VALUES (46, 2, 21, 'Quick note on Mogilev Regional Museum', 'Loved this place, would come back again.', 4, 'couple', '2026-06-19', 'June', 0, 0, 'positive', 0.670, 1, 'published', '127.0.0.1', '2026-06-19 18:29:16', '2026-06-19 18:29:16', NULL);
INSERT INTO `reviews` VALUES (47, 2, 24, 'Quick note on Holy Trinity Church in Gierviaty', 'Loved this place, would come back again.', 5, 'solo', '2026-04-21', 'April', 4, 0, 'positive', 0.750, 1, 'published', '127.0.0.1', '2026-04-21 18:29:16', '2026-04-21 18:29:16', NULL);
INSERT INTO `reviews` VALUES (48, 2, 58, 'Quick note on Vileyka Lake District', 'Loved this place, would come back again.', 3, 'couple', '2026-04-25', 'April', 3, 0, 'positive', 0.850, 1, 'published', '127.0.0.1', '2026-04-25 18:29:16', '2026-04-25 18:29:16', NULL);
INSERT INTO `reviews` VALUES (49, 3, 1, NULL, 'test demo', 5, NULL, NULL, NULL, 0, 0, 'neutral', 0.000, 1, 'published', '127.0.0.1', '2026-07-05 06:48:28', '2026-07-05 06:48:28', NULL);

-- ----------------------------
-- Table structure for sentiment_analysis_log
-- ----------------------------
DROP TABLE IF EXISTS `sentiment_analysis_log`;
CREATE TABLE `sentiment_analysis_log`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `review_id` bigint NOT NULL,
  `content_hash` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `raw_response` json NULL,
  `sentiment_label` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sentiment_score` decimal(4, 3) NOT NULL,
  `confidence` decimal(5, 4) NULL DEFAULT NULL,
  `model_used` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `processing_time_ms` int NULL DEFAULT NULL,
  `api_cost` decimal(8, 4) NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fallback_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_sentiment_review_id`(`review_id` ASC) USING BTREE,
  INDEX `idx_sentiment_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_sentiment_status`(`status` ASC) USING BTREE,
  CONSTRAINT `sentiment_analysis_log_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `reviews` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentiment_analysis_log
-- ----------------------------
INSERT INTO `sentiment_analysis_log` VALUES (37, 49, '0e17daca5f3e175f448bacace3bc0da47d0655a74c8dd0dc497a3afbdad95f1f', 'null', 'neutral', 0.000, NULL, 'fallback_keyword', 810, NULL, 'fallback', NULL, '2026-07-05 06:48:28');

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `color` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `article_count` int NOT NULL,
  `use_count` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `slug`(`slug` ASC) USING BTREE,
  INDEX `idx_tags_slug`(`slug` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tags
-- ----------------------------
INSERT INTO `tags` VALUES (1, 'UNESCO World Heritage', 'unesco', 'UNESCO World Heritage Sites in Belarus', '#f5a623', 0, 3, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (2, 'History', 'history', 'Historical sites and monuments', '#8b4513', 0, 8, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (3, 'Nature', 'nature', 'Parks, forests, and natural landscapes', '#2a9d5c', 0, 8, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (4, 'Architecture', 'architecture', 'Architectural landmarks', '#1a5e63', 0, 6, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (5, 'Family Friendly', 'family', 'Great for families with children', '#e91e63', 0, 2, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (6, 'Photography', 'photography', 'Top photography spots', '#9c27b0', 0, 5, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (7, 'Medieval', 'medieval', 'Medieval-era castles and ruins', '#795548', 0, 5, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (8, 'Memorial', 'memorial', 'Memorials and war monuments', '#607d8b', 0, 4, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (9, 'Museums', 'museums', 'Museums and exhibitions', '#ff5722', 0, 6, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (10, 'Religious Sites', 'religious', 'Churches, monasteries, and religious monuments', '#673ab7', 0, 6, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (11, 'Lakes', 'lakes', 'Lakes and water recreation', '#2196f3', 0, 5, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (12, 'Forests', 'forests', 'Forests and woodland areas', '#4caf50', 0, 4, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (13, 'Hiking', 'hiking', 'Hiking and outdoor activities', '#795548', 0, 3, '2026-06-28 10:55:36');
INSERT INTO `tags` VALUES (14, 'Urban', 'urban', 'City landmarks and urban exploration', '#9e9e9e', 0, 5, '2026-06-28 10:55:36');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `last_login_at` datetime NULL DEFAULT NULL,
  `last_login_ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `email_verified` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin@belarus-tourism.com', 'scrypt:32768:8:1$2XQjsyi9iGoATWxw$88af8a3ebcd8388b335af233bd26853c73915092bef2d0e23d916c59fbf860eba852e9658018ecfabe400d280495f4d7c79824ebea9f2648941fc25b5274cb88', 'Administrator', '/api/upload/files/avatars/2026-07/6f4fecd501034564af6bb6a33701330b.png', 'admin', 'active', NULL, '2026-07-05 09:11:31', '127.0.0.1', 1, '2026-06-28 10:55:36', '2026-07-05 09:11:31');
INSERT INTO `users` VALUES (2, 'demo', 'demo@example.com', 'scrypt:32768:8:1$tsqBVPyF0V38st7J$b0f3399622b359fb3ec46fc8359c35a684ce0b8769f652b7cbdc6fac4720811b1098d8012425299a00e19fb239c43743a6f961327b5b136f4b90c8673a02aafa', 'Demo User', '', 'user', 'active', NULL, '2026-07-05 06:58:49', '127.0.0.1', 1, '2026-06-28 10:55:36', '2026-07-05 06:58:49');
INSERT INTO `users` VALUES (3, '123', '123@qq.com', 'scrypt:32768:8:1$qwrqSruooyfN1CTd$89b736ec4f01ac1dacf571e27d162c0e1bef71bfd5a6afd0e54b69bd6892eb9c5d2bfa58841a876db5a9d8dcf89a5661f091282cf9529a761f51775aabb9009f', '123', '/static/uploads/avatars/3_1783207063_74443c.jpg', 'user', 'active', NULL, '2026-07-06 09:53:57', '127.0.0.1', 0, '2026-07-03 11:10:56', '2026-07-06 09:53:57');

-- ----------------------------
-- Table structure for wishlists
-- ----------------------------
DROP TABLE IF EXISTS `wishlists`;
CREATE TABLE `wishlists`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `attraction_id` bigint NOT NULL,
  `note` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `priority` smallint NOT NULL,
  `visited` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_attraction_wishlist`(`user_id` ASC, `attraction_id` ASC) USING BTREE,
  INDEX `idx_wishlists_attraction_id`(`attraction_id` ASC) USING BTREE,
  CONSTRAINT `wishlists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `wishlists_ibfk_2` FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of wishlists
-- ----------------------------
INSERT INTO `wishlists` VALUES (1, 2, 3, 'Want to see the bison in autumn!', 1, 0, '2026-06-29 18:21:21');
INSERT INTO `wishlists` VALUES (2, 2, 4, 'Bucket-list: stand on the meridian.', 1, 0, '2026-05-18 18:21:21');
INSERT INTO `wishlists` VALUES (3, 2, 8, 'Plan for the next summer holiday.', 2, 0, '2026-06-06 18:21:21');
INSERT INTO `wishlists` VALUES (4, 2, 18, 'Family trip in July.', 1, 0, '2026-05-13 18:21:21');
INSERT INTO `wishlists` VALUES (5, 2, 20, 'Camping gear is ready.', 2, 0, '2026-06-01 18:21:21');
INSERT INTO `wishlists` VALUES (6, 2, 1, 'Already visited, want to revisit next spring.', 3, 1, '2026-06-06 18:21:21');
INSERT INTO `wishlists` VALUES (7, 3, 2, NULL, 3, 0, '2026-07-06 09:59:23');

SET FOREIGN_KEY_CHECKS = 1;
