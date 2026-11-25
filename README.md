# Belarus Tourism Review & Analysis System

白俄罗斯旅游信息系统用于浏览景点、分享旅行评价和整理行程，结合外部平台评分与本站用户评价提供推荐和统计分析。

## 主要功能

- 景点目录：搜索、分类、排序、详情、地图、排行榜和景点对比。
- 用户功能：注册登录、个人资料、收藏、评分和评价。
- 外部平台信息：展示景点评分和评论摘录，保留来源链接、作者和日期。
- 社区交流：文章、评论、问答和投票。
- 推荐与分析：情感分析、个性推荐、相似景点、用户聚类和统计图表。
- 行程规划：按天安排景点，行程保存在当前浏览器中。
- 后台管理：用户管理、评价管理、景点创建、发布和归档。

系统使用user、moderator和admin三种角色，未登录访客可以浏览公开页面。景点列表每页显示9条，提供搜索、分类和排序；本站评价最多400个字符。

## 技术栈

前端使用Vue 3、JavaScript、Vite、Vue Router、Pinia和Axios，地图采用Leaflet，统计图表采用ECharts。

后端使用Flask、Flask-SQLAlchemy、Flask-JWT-Extended和PyMySQL，数据库采用MySQL 8。系统通过JWT认证和服务端角色检查控制权限。

分析模块包含TF-IDF景点相似度、KMeans用户聚类和MinHash评价相似度计算。情感分析与推荐可调用DeepSeek接口，也保留关键词分析和统计推荐方式。

## 项目数据

项目包含1000条景点数据、1898条外部评论摘录和页面使用的图片，数据模型包含22张表。

景点资料及外部评分主要来自[Ctrip/Trip.com](https://www.trip.com/)和[Yandex Maps](https://yandex.com/maps/)，部分景点保留[Wikidata](https://www.wikidata.org/)标识。记录通过`source_url`、`field_sources`等字段保存具体出处。

外部平台评分和本站用户评分分别保存，外部评论摘录保留原始作者、日期和来源链接。图表中的已保存评论数按数据库中的实际评论记录统计。

## 项目结构

`backend`保存后端接口、数据模型、分析服务、数据和图片；`frontend`保存前端页面、组件和样式；`scripts`保存项目运行脚本。
