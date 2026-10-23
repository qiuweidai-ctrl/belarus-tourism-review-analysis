# Belarus Tourism Review & Analysis System

A Flask + Vue 3 web application for Belarus tourism attractions with AI-powered sentiment analysis and personalized recommendations.

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, MySQL 8
- **Frontend**: Vue 3, Vue Router, vue-i18n, Axios, Pinia
- **AI**: DeepSeek API (sentiment analysis & recommendation)
- **UI**: Custom CSS with responsive design

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python init_db.py
python app.py
```

The default local connection is `root:123456@localhost:3306/belarus_tourism`.
Set `SQLALCHEMY_DATABASE_URI` in the environment to use a different MySQL
account or host. The API runs at `http://localhost:5000`.

### Add Attraction Data

The Wikidata importer adds new English attraction records without changing
the existing records:

```bash
cd backend
python scrape_wikidata.py --limit 100 --new-only --output scraped_data.json
python enrich_attractions.py
```

The importer skips duplicate names and incomplete records, downloads available
Wikimedia Commons images, and stores local image paths in the database. The
enrichment step fills the remaining approved images and adds demo reviews to
new attractions that do not have a rating yet.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

On Windows PowerShell, use `npm.cmd run dev` if script execution policy blocks
`npm.ps1`. The development site runs at `http://localhost:3000` and proxies API
requests to Flask.

## Default Accounts

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| demo     | demo123   | user  |

## Features

- User registration and login (JWT auth)
- Attraction browsing, search, and filtering
- Write and view reviews
- AI sentiment analysis on reviews (DeepSeek API)
- AI-powered personalized recommendations
- Rating prediction based on user history
- English interface (i18n ready)
- Responsive design

## 前端页面与角色操作指南

系统页面显示语言为英文，本节使用中文说明每个页面的用途和操作方法。

### 公共界面

- 左侧导航按照 `Overview`、`Explore`、`Analytics`、`Community`、`My Trip` 和 `Administration` 分组。
- 顶部搜索框输入景点名称或城市后，会跳转到景点列表并执行搜索。
- 月亮/太阳按钮用于切换浅色和深色主题。
- 桌面端可折叠左侧导航；移动端使用抽屉菜单。
- 登录后，顶部会显示用户头像、用户名、角色和退出按钮。
- `For You`、`My Profile` 只对已登录用户显示；`Admin Panel` 只对管理员和版主显示。

### 角色与权限

| 角色 | 可以访问的内容 | 主要操作 |
|---|---|---|
| 访客（未登录） | 首页、景点、地图、排行榜、对比、数据分析、词云、文章、问答、行程规划 | 浏览和搜索数据、查看评论和文章、使用本地行程规划、注册或登录 |
| 普通用户（`user`） | 访客页面以及个性化推荐、收藏夹和个人中心 | 收藏景点、提交或删除自己的评论、点赞和评论文章、发布和管理自己的文章、发布问题、编辑资料和头像、查看登录记录 |
| 版主（`moderator`） | 普通用户页面以及管理后台 | 管理用户角色和状态、审核评论、设置精选/认证景点、查看登录事件、运行算法管理工具 |
| 管理员（`admin`） | 全部页面 | 拥有版主的全部能力；还可以在景点详情页点击主图上传新图片 |

普通用户只能修改或删除自己创建的评论和文章。未登录时尝试使用收藏、评论、个性化推荐等功能，会看到登录提示或被接口拒绝。

### 页面说明

#### 1. Dashboard — 首页

- 路由：`/`
- 权限：所有人
- 展示景点数量、评论数量、平均评分、浏览量等关键指标。
- 展示地区分布、热门景点、评分最高的景点和最近评论。
- 点击 `View insights`、`Explore attractions`、地区、排行榜或快捷入口，可进入对应页面。

#### 2. Attractions — 景点列表

- 路由：`/attractions`
- 权限：所有人
- 按卡片展示景点图片、城市、地区、评分、评论数量、类别和票价。
- 可通过关键词搜索，通过类别筛选，并按最新、评分或名称排序。
- 每页显示 9 个景点，使用 `Prev` 和 `Next` 翻页。
- 点击卡片进入景点详情；登录用户可点击卡片上的心形按钮切换收藏状态。

#### 3. Attraction Details — 景点详情

- 路由：`/attractions/:id`
- 权限：所有人可查看；登录用户可互动
- 展示景点主图、位置、介绍、评分、情感分析、相似景点和高质量评论。
- 登录用户会看到预测评分，可以收藏景点并提交 1–5 星英文评论。
- 用户可以删除自己的评论；系统会在提交前提示可能重复的评论。
- 管理员或该景点的创建者可点击 `Change Image` 上传新的主图。

#### 4. Map Explorer — 地图

- 路由：`/map`
- 权限：所有人
- 在地图上展示所有具有经纬度的景点，并统计已映射景点、城市和平均评分。
- 可按名称和类别筛选，使用 `Markers` 与 `Heatmap` 切换显示模式。
- 点击右侧景点卡片可将地图定位到对应地点。

#### 5. Rankings — 排行榜

- 路由：`/rankings`
- 权限：所有人
- 可按 `Rating`、`Reviews`、`Views` 或 `Saves` 查看前 20 名景点。
- 前三名以领奖台卡片显示，其余景点显示在排名列表中。
- 可将后续列表按名称正序或倒序排列，点击任意景点进入详情页。

#### 6. Compare Attractions — 景点对比

- 路由：`/compare`
- 权限：所有人
- 从两个下拉框选择不同景点，进行并排比较。
- 对比图片、城市、地区、类别、评分、评论数、票价、收藏数、浏览量、情感分数、季节、开放时间和认证状态。
- 系统会在评分、评论数、票价、收藏数和浏览量等项目中标出优势方。
- 中间的交换按钮可快速交换左右景点。

#### 7. Data Insights — 数据分析

- 路由：`/insights`
- 权限：所有人
- 展示景点、评论、评分、用户、文章、浏览量和平均票价等汇总数据。
- 图表包括评分分布、游客类型、类别分布、地区分布、票价区间、评论趋势和分类情感分析。
- `Leaderboard` 可在评分、评论、浏览量和收藏量之间切换。
- 页面顶部可将景点、评论或用户数据导出为 CSV 文件。

#### 8. Word Clouds — 词云

- 路由：`/wordcloud`
- 权限：所有人
- 从评论和景点介绍中统计高频英文词汇。
- 可切换 `All content`、`Reviews` 和 `Attractions` 三种统计范围。
- 词云通过文字大小表示频次，并使用多种颜色区分词语。
- 下方 `Top 15` 使用相同的多色方案显示排名、进度条和出现次数。

#### 9. Travel Guides & Articles — 旅游文章

- 路由：`/articles`
- 权限：所有人可浏览；登录用户可发布
- 展示已发布的旅游攻略和文章，支持关键词搜索、精选筛选和分页。
- 点击文章卡片进入文章详情。
- 登录用户可点击 `Write Article` 打开文章编辑页。

#### 10. Article Details — 文章详情

- 路由：`/articles/:id`
- 权限：所有人可阅读；登录用户可互动
- 展示文章封面、作者、正文、标签、浏览量、点赞量和评论。
- 登录用户可点赞/取消点赞文章，并提交文章评论。

#### 11. Write/Edit Article — 撰写或编辑文章

- 路由：`/articles/write`
- 权限：登录用户
- 可填写标题、摘要、正文、封面图片地址、关联景点和标签。
- 新建文章时点击 `Publish` 发布；从个人中心进入时可编辑自己的文章。
- 点击 `Cancel` 返回文章列表。

#### 12. Questions & Answers — 景点问答

- 路由：`/qa`
- 权限：所有人可浏览；登录用户可提问
- 展示问题、回答数量、点赞数量、提问者、日期和关联景点。
- 可按景点筛选问题，并通过分页浏览。
- 登录用户点击 `Ask Question`，选择景点并填写标题和补充说明后提交问题。

#### 13. Trip Itinerary — 行程规划

- 路由：`/itinerary`
- 权限：所有人
- 创建行程名称和多个日期，为每一天添加景点站点和备注。
- 支持调整日期和站点顺序、拖动排序、删除日期或站点，并自动计算站点数、预计票价和平均评分。
- 行程保存在当前浏览器的 `localStorage` 中，不会同步到其他设备或账户。
- 可下载为文本文件，或使用 `Print / Save PDF` 打印和保存 PDF。

#### 14. My Wishlist — 收藏夹

- 路由：`/wishlist`
- 权限：登录用户
- 汇总收藏数量、预计票价、平均评分和已访问数量。
- 可按最近添加、评分或票价排序。
- 可调整优先级、标记已访问、查看详情或移除收藏。
- 未登录用户进入时会看到登录提示。

#### 15. Smart Recommendations — 个性化推荐

- 路由：`/recommendations`
- 权限：所有人可查看趋势和类别推荐；个性化内容需要登录
- `Trending Now` 根据评分、评论、情感和时间衰减显示热门景点。
- 登录用户可查看自己的用户分群、偏好特征和基于历史行为的相似景点推荐。
- 可点击 `Refresh` 刷新个性化结果，或切换类别查看分类推荐。

#### 16. My Profile — 个人中心

- 路由：`/profile`
- 权限：登录用户
- 展示用户名、邮箱、昵称、角色、简介、头像和注册时间。
- `Edit Profile` 可修改昵称、简介、头像和密码。
- `My Reviews`：查看并删除自己的景点评论。
- `Wishlist`：查看并移除收藏。
- `Articles`：新建、编辑或删除自己的文章。
- `Security`：查看登录、退出、注册、密码修改等账户事件及设备/IP 信息。

#### 17. Login — 登录

- 路由：`/login`
- 权限：未登录用户
- 输入用户名和密码进行登录，成功后保存 JWT 登录状态并返回首页。
- 可使用 README 中的 `demo` 或 `admin` 默认账户进行测试。

#### 18. Register — 注册

- 路由：`/register`
- 权限：未登录用户
- 填写用户名、邮箱和密码创建账户，新账户默认角色为 `user`。
- 注册成功后进入登录页，再使用新账户登录系统。

#### 19. Admin Dashboard — 管理后台

- 路由：`/admin`
- 权限：`admin`、`moderator`
- 首页统计用户数、景点数、已发布评论和待审核评论。
- `Users`：修改用户角色，封禁或解封用户。
- `Reviews`：按状态查看评论，隐藏已发布评论，批准隐藏或待审核评论。
- `Attractions`：查看评分、评论和浏览量，设置/取消精选并认证景点。
- `Login Events`：按事件类型查看登录、安全和账户操作记录。
- `AI Algorithms`：重新训练用户聚类、查看用户分群、查找重复评论、重建重复索引和重新计算热门分数。

### 推荐操作流程

#### 访客

1. 从首页了解整体数据和热门景点。
2. 在 `Attractions` 搜索或筛选目的地。
3. 使用 `Map Explorer`、`Rankings` 和 `Compare` 缩小选择范围。
4. 在 `Trip Itinerary` 创建行程，并下载或打印结果。
5. 需要收藏、评论或个性化推荐时注册账户。

#### 普通用户

1. 登录后在景点卡片或详情页点击心形按钮收藏景点。
2. 在详情页提交评分和评论，让推荐模型获得偏好数据。
3. 在 `For You` 查看个性化推荐和用户分群。
4. 在 `Wishlist` 管理优先级和访问状态。
5. 在 `My Profile` 管理评论、收藏、文章、头像、密码和登录记录。

#### 版主或管理员

1. 使用具有相应角色的账户登录，左侧会出现 `Administration`。
2. 先在后台概览检查待审核评论和异常登录事件。
3. 在 `Users`、`Reviews` 和 `Attractions` 标签中完成日常内容管理。
4. 需要更新推荐结果时，在 `AI Algorithms` 中重新训练聚类并重新计算热门分数。
5. 管理员如需更换景点图片，可进入景点详情并点击主图上的 `Change Image`。
