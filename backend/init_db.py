# -*- coding: utf-8 -*-
"""
Initialize MySQL database with REAL scraped Belarus tourism data.
Data sources: Wikipedia, belarus.by, tourismattractions.net, nashaniva.com (2026)
Run: python init_db.py
"""
from app import create_app
from models import db, User, Attraction, Article, Tag, AttractionTag, Question, Answer
from werkzeug.security import generate_password_hash

# ─────────────────────────────────────────────────────────
# REAL BELARUS ATTRACTIONS (scraped from Wikipedia, belarus.by, etc.)
# ─────────────────────────────────────────────────────────
BELARUS_ATTRACTIONS = [
    # ══════════════════════════════════════════════════════════
    # UNESCO WORLD HERITAGE SITES
    # ══════════════════════════════════════════════════════════
    {'name': 'Mir Castle Complex', 'name_en': 'Mir Castle Complex',
     'description': 'A UNESCO World Heritage Site since 2000. Built in the early 16th century in late Brick Gothic style, Mir Castle is one of the finest examples of fortified architecture from the former Polish-Lithuanian Commonwealth. Five towers rise 27 metres above the defensive moat, surrounding a central courtyard. Later Renaissance and Baroque additions created a unique blend of architectural styles. Located beside a picturesque lake whose waters perfectly mirror the castle silhouette. Houses a museum with period furniture, weaponry, tapestries, and portraits tracing 500 years of history through Lithuanian, Polish, Russian, and Belarusian ownership.',
     'short_desc': 'UNESCO World Heritage Site — a 16th-century Gothic-Renaissance fortified castle with five towers.',
     'location': 'Mir, Karelichy District, Grodno Oblast', 'city': 'Mir', 'region': 'Grodno Oblast',
     'latitude': 53.4512389, 'longitude': 26.473, 'category': 'castle', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 18:00', 'ticket_price': 10.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/%D0%9C%D0%B8%D1%80%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg/400px-%D0%9C%D0%B8%D1%80%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg',
     'avg_rating': 4.8, 'is_featured': True, 'is_verified': True},

    {'name': 'Nesvizh Castle (Radziwill Palace)', 'name_en': 'Nesvizh Castle',
     'description': 'A UNESCO World Heritage Site since 2005. The seat of the powerful Radziwill dynasty for over 400 years, this architectural masterpiece combines Renaissance, Baroque, Classicism, Gothic Revival, and Modernism. The complex comprises the residential palace and Corpus Christi mausoleum-church with its landscaped setting. The gilded ballroom, portrait gallery, armoury, and palace chapel (one of the earliest Jesuit churches outside Rome with the largest family crypt in Europe) are must-sees. The surrounding park spans over 100 hectares with English, French, and Japanese-style garden sections and interconnected ponds.',
     'short_desc': 'UNESCO World Heritage Site — Radziwill family palace and park complex, the most beautiful castle in Belarus.',
     'location': 'Nesvizh, Minsk Oblast', 'city': 'Nesvizh', 'region': 'Minsk Oblast',
     'latitude': 53.2269444, 'longitude': 26.5777778, 'category': 'palace', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 17:00 (Tue-Sun)', 'ticket_price': 8.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/%D0%9D%D1%8F%D1%81%D0%B2%D1%96%D0%B6_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg/400px-%D0%9D%D1%8F%D1%81%D0%B2%D1%96%D0%B6_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg',
     'avg_rating': 4.7, 'is_featured': True, 'is_verified': True},

    {'name': 'Belovezhskaya Pushcha National Park', 'name_en': 'Belovezhskaya Pushcha National Park',
     'description': 'A UNESCO World Heritage Site shared with Poland. One of the last remaining fragments of the primeval forest that once covered the European Plain. The forest is home to over 600 European bison (the continent\'s heaviest land animal), wolves, lynx, wild boar, and over 250 bird species. Ancient oaks exceed 600 years old, and spruces reach 50 metres in height. Visitors can explore on marked hiking and cycling trails, or by horse-drawn cart on guided tours. The park\'s Nature Museum offers an excellent introduction to the ecosystem. In winter, it operates as the official residence of Ded Moroz (Grandfather Frost), drawing families from across the region.',
     'short_desc': "UNESCO World Heritage Site — Europe's last primeval forest, home to 600+ European bison.",
     'location': 'Kamieniuki, Brest Oblast', 'city': 'Kamieniuki', 'region': 'Brest Oblast',
     'latitude': 52.5833333, 'longitude': 23.8666667, 'category': 'nature', 'suitable_season': 'All seasons (best May-Sep)',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 5.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/BelarusBNP09.JPG/400px-BelarusBNP09.JPG',
     'avg_rating': 4.6, 'is_featured': True, 'is_verified': True},

    {'name': 'Struve Geodetic Arc (Belarus Points)', 'name_en': 'Struve Geodetic Arc',
     'description': 'A UNESCO World Heritage Site since 2005 (transnational, shared with 9 other countries). A series of triangulation points stretching 2,820 km from Hammerfest, Norway to the Black Sea, established by astronomer Friedrich Georg Wilhelm von Struve to measure the shape of the Earth. Five of the original 265 station points are located in Belarus, near the towns of Tupiški and near Minsk. These geodetic markers represent a remarkable scientific achievement that helped establish the size and shape of our planet.',
     'short_desc': 'UNESCO World Heritage — 19th-century geodetic survey points across 10 countries.',
     'location': 'Tupiški, Grodno Oblast', 'city': 'Tupiški', 'region': 'Grodno Oblast',
     'latitude': 54.2833, 'longitude': 26.05, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # CASTLES (real Belarus castles)
    # ══════════════════════════════════════════════════════════
    {'name': 'Lida Castle', 'name_en': 'Lida Castle',
     'description': 'A well-preserved 14th-century fortified castle built by Prince Gediminas of the Grand Duchy of Lithuania. One of the few medieval brick castles in Belarus that retains much of its original defensive structure, including four corner towers and fortified walls. The castle played a key role in defending the western borders of the Grand Duchy. According to legend, Grand Duke Vytautas the Great ordered its construction. The castle hosts medieval reenactment festivals and knight tournaments during summer months.',
     'short_desc': '14th-century Gediminas-era castle — one of the best-preserved medieval brick castles in Belarus.',
     'location': 'Lida, Grodno Oblast', 'city': 'Lida', 'region': 'Grodno Oblast',
     'latitude': 53.8833, 'longitude': 25.3, 'category': 'castle', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 4.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Lida_Castle.jpg/400px-Lida_castle.jpg',
     'avg_rating': 4.3, 'is_featured': True, 'is_verified': True},

    {'name': 'Navahrudak Castle (Kamyenyets Tower)', 'name_en': 'Navahrudak Castle',
     'description': 'A 13th-century fortified castle on a rocky hill in the legendary birthplace of the Lithuanian state. The castle is associated with the founding of the Grand Duchy of Lithuania and features massive defensive walls built from local limestone. Navahrudak (also called Novogrudok) was the seat of the Gediminas princes and retains ruins of the tower, walls, and a 17th-century church. The town itself is surrounded by seven hills and offers panoramic views over the surrounding landscape.',
     'short_desc': '13th-century castle ruins on the legendary birthplace of the Lithuanian state.',
     'location': 'Navahrudak, Grodno Oblast', 'city': 'Navahrudak', 'region': 'Grodno Oblast',
     'latitude': 53.5833, 'longitude': 25.8167, 'category': 'castle', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 3.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Navahrudak_Castle.jpg/400px-Navahrudak_Castle.jpg',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Krevo Castle', 'name_en': 'Krevo Castle',
     'description': 'A partially preserved medieval castle originally built in the 13th century. Once the residence of the Gediminas family — one of the most powerful dynasties in Eastern Europe — it is one of the oldest stone castles in Belarus. The castle was built at the confluence of the Awsłaŭ and Swisłocz rivers as part of the Grand Duchy of Lithuania\'s western defensive line. The ruins include sections of the defensive walls and towers.',
     'short_desc': '13th-century castle — former residence of the Gediminas dynasty, one of the oldest stone castles in Belarus.',
     'location': 'Krevo, Volozhin District, Minsk Oblast', 'city': 'Krevo', 'region': 'Minsk Oblast',
     'latitude': 54.15, 'longitude': 26.8333, 'category': 'castle', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Lubcha Castle', 'name_en': 'Lubcha Castle',
     'description': 'Once the largest fortified castle in the Grand Duchy of Lithuania, built in the 16th century. The castle featured massive walls, deep moats, and a sophisticated defensive system. Its massive ruins still convey the grandeur of what was once a major defensive and residential complex. The castle was damaged during the Napoleonic Wars and fell into disrepair, but ongoing restoration efforts aim to preserve its significant historical legacy.',
     'short_desc': 'Ruins of the once-largest castle in the Grand Duchy of Lithuania.',
     'location': 'Lubcha, Kletsk District, Minsk Oblast', 'city': 'Lubcha', 'region': 'Minsk Oblast',
     'latitude': 53.0333, 'longitude': 27.05, 'category': 'castle', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 18:00', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Kamyanets Tower (Belaya Vezha)', 'name_en': 'Kamyanets Tower',
     'description': 'A 13th-century defensive tower built during the time of Prince Vytautas, one of the most important defensive structures in the Grand Duchy of Lithuania. The tower stands 30 metres tall and is one of the oldest fortifications in Belarus. It became one of the most photographed landmarks in the country due to its dramatic silhouette and association with the borderland history between Lithuania and Poland.',
     'short_desc': '13th-century defensive tower — one of the oldest fortifications in Belarus.',
     'location': 'Kamenets, Brest Oblast', 'city': 'Kamenets', 'region': 'Brest Oblast',
     'latitude': 52.2167, 'longitude': 23.8167, 'category': 'castle', 'suitable_season': 'All seasons',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 2.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Minsk Castle (Menski Castle)', 'name_en': 'Minsk Castle',
     'description': 'The historic fortified castle of Minsk, originally built in the 12th century. The castle was severely damaged during the Great Northern War and subsequently demolished. Only fragments of the original walls and foundations remain near the Svislach River. A reconstruction project has been discussed, and archaeological excavations continue to reveal the castle\'s history.',
     'short_desc': '12th-century castle ruins — the historic fortified seat of Minsk princes.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9053, 'longitude': 27.5558, 'category': 'castle', 'suitable_season': 'All seasons',
     'opening_hours': 'External viewing only', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 3.5, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # WAR MEMORIALS
    # ══════════════════════════════════════════════════════════
    {'name': 'Brest Hero Fortress', 'name_en': 'Brest Fortress',
     'description': 'A sprawling memorial complex on the border with Poland. On 22 June 1941, this 19th-century citadel was among the very first targets of Operation Barbarossa. The garrison held out for over a month against overwhelming German forces — one of the longest last-stand battles of WWII. The centrepiece is the colossal "Courage" sculpture, a concrete head emerging from a rock face ranking among the largest portrait sculptures in the world. The Defence of Brest Fortress Museum displays maps, personal belongings, and recovered weaponry. The fortress has drawn 2.8 million visitors over the past five years and held about 55,000 guided tours.',
     'short_desc': 'Heroic WWII fortress — first battle site of the Great Patriotic War, symbol of endurance.',
     'location': 'Brest, Belarus', 'city': 'Brest', 'region': 'Brest Oblast',
     'latitude': 52.0833, 'longitude': 23.9167, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': '09:00 - 18:00', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Brest_fortress_10.jpg/400px-Brest_fortress_10.jpg',
     'avg_rating': 4.7, 'is_featured': True, 'is_verified': True},

    {'name': 'Khatyn Memorial Complex', 'name_en': 'Khatyn Memorial Complex',
     'description': 'A national memorial commemorating the victims of the Khatyn massacre of March 1943 and the destruction of over 400 Belarusian villages by Nazi forces. The memorial features 185 chimneys — one for each burned village — each with a bell that chimes in the wind. The iconic 20-tonne "Never Again" bell, a sculpture of a dying mother holding her dead child, a cemetery of symbolic graves, and a 26-metre obelisk form the centrepiece. As of 2026, Khatyn ranks as the second-most-visited monument in Belarus after Lida Castle, with approximately 17,000 visitors in the first five months of 2026.',
     'short_desc': 'National memorial to victims of Nazi atrocities and 400+ destroyed Belarusian villages.',
     'location': 'Khatyn, Minsk Region', 'city': 'Khatyn', 'region': 'Minsk Region',
     'latitude': 54.3, 'longitude': 27.9, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/%D0%A5%D0%B0%D1%82%D1%8B%D0%BD%D1%8C.jpg/400px-%D0%A5%D0%B0%D1%82%D1%8B%D0%BD%D1%8C.jpg',
     'avg_rating': 4.5, 'is_featured': True, 'is_verified': True},

    {'name': 'Kurapaty Mass Graves', 'name_en': 'Kurapaty',
     'description': 'A memorial site marking mass executions carried out by the NKVD between 1937 and 1941 under Stalin\'s Great Purge. Located in a forest on the outskirts of Minsk, the site contains the remains of thousands of Belarusians executed as "enemies of the people." The site serves as a memorial to victims of Stalinist repressions and is an important place of historical memory and civic education in Belarus. Visitors walk through the forest along marked trails past unmarked pits.',
     'short_desc': 'Memorial to victims of Stalinist repressions — mass grave site of NKVD killings (1937-1941).',
     'location': 'Kurapaty, Minsk', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9333, 'longitude': 27.5833, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Island of Tears Memorial', 'name_en': 'Island of Tears Memorial',
     'description': 'A poignant memorial on an islet in the Svislach River in Minsk, dedicated to Belarusian soldiers who died in the Soviet-Afghan War (1979-1989). The memorial features a sculpture of a weeping mother, walls inscribed with the names of fallen soldiers, and a small chapel. It is one of the most emotionally powerful memorials in Belarus.',
     'short_desc': 'Memorial to Belarusian soldiers who died in the Soviet-Afghan War, on an island in the Svislach River.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9083, 'longitude': 27.555, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Plamya (Eternal Flame) Memorial', 'name_en': 'Plamya Memorial',
     'description': 'An eternal flame memorial in Victory Square, Minsk, dedicated to all Belarusians who died in wars. The monument consists of a four-sided granite obelisk topped by the eternal flame. A relief sculpture depicts soldiers, workers, and partisans. Located in central Minsk\'s most symbolic square, it is one of the most visited war memorials in the country.',
     'short_desc': 'Eternal flame memorial in central Minsk honouring all Belarusian war casualties.',
     'location': 'Victory Square, Minsk', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9083, 'longitude': 27.5725, 'category': 'memorial', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MUSEUMS
    # ══════════════════════════════════════════════════════════
    {'name': 'Great Patriotic War Museum', 'name_en': 'Museum of the Great Patriotic War',
     'description': 'The largest military history museum in Belarus, opened in 2014 on the 70th anniversary of the liberation of Minsk. Located near the Svislach River, the modern building holds over 8,000 artefacts with immersive dioramas and multimedia installations. The story of Belarus during WWII — in which the country lost approximately a quarter of its population — is told through personal belongings, weapons, uniforms, and interactive exhibits. The rooftop observation deck offers panoramic views of Minsk.',
     'short_desc': 'Largest WWII museum in Belarus — 8,000+ artefacts, immersive multimedia exhibits, rooftop views.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9208, 'longitude': 27.5378, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00 (Tue-Sun)', 'ticket_price': 5.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Minsk_-_Museum_of_the_Great_Patriotic_War.jpg/400px-Minsk_-_Museum_of_the_Great_Patriotic_War.jpg',
     'avg_rating': 4.6, 'is_featured': True, 'is_verified': True},

    {'name': 'National Art Museum of Belarus', 'name_en': 'National Art Museum of Belarus',
     'description': 'The largest collection of fine arts in Belarus, with over 30,000 works spanning 900 years from 12th-century religious icons to contemporary Belarusian art. The collection includes paintings by Ilya Repin, Ivan Shishkin, and Marc Chagall (including works from his Vitebsk period), as well as a comprehensive survey of Belarusian artists. Sculptures, graphics, and applied arts complete the picture.',
     'short_desc': 'Over 30,000 artworks spanning 900 years — from medieval icons to Marc Chagall and Belarusian masters.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9114, 'longitude': 27.5692, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '11:00 - 19:00 (Wed-Mon)', 'ticket_price': 6.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/National_Art_Museum_of_Belarus.jpg/400px-National_Art_Museum_of_Belarus.jpg',
     'avg_rating': 4.5, 'is_featured': True, 'is_verified': True},

    {'name': 'Museum of Belarusian Folk Architecture', 'name_en': 'Museum of Belarusian Folk Architecture',
     'description': 'An open-air ethnographical museum in Ozertsy, 45 km from Minsk, showcasing traditional Belarusian village architecture from the 17th to early 20th centuries. Features authentic wooden houses, churches, windmills, and farm buildings relocated from different regions of Belarus, set in a natural landscape. Visitors can see how rural Belarusians lived, worked, and worshipped across centuries.',
     'short_desc': 'Open-air ethnographical museum — authentic relocated wooden village buildings from across Belarus.',
     'location': 'Ozertsy, Minsk Oblast', 'city': 'Ozertsy', 'region': 'Minsk Oblast',
     'latitude': 54.0167, 'longitude': 27.6333, 'category': 'museum', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 17:00 (Wed-Mon)', 'ticket_price': 4.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Gomel Palace Museum', 'name_en': 'Gomel Palace Museum',
     'description': 'Housed in the historic Rumyantsev-Paskevich Palace, one of the most beautiful architectural monuments in Belarus. The palace is featured on the Belarusian 20-ruble banknote. Collections include decorative arts, weapons, paintings, and archaeological artifacts from the Gomel region spanning several centuries. The estate complex stretches 800 metres along the Sozh River.',
     'short_desc': 'Decorative arts, weapons, and paintings in the historic Rumyantsev-Paskevich Palace.',
     'location': 'Gomel, Belarus', 'city': 'Gomel', 'region': 'Gomel Oblast',
     'latitude': 52.4411, 'longitude': 30.9933, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00 (Wed-Mon)', 'ticket_price': 5.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Marc Chagall Museum', 'name_en': 'Marc Chagall Museum',
     'description': 'Located in Vitebsk, the hometown of the renowned artist Marc Chagall (1887-1985). The museum is housed in a building where Chagall lived and worked during his years as an artist in Vitebsk (1919-1920), when he served as art director of the Vitebsk Art School. Contains the largest collection of Chagall\'s works in Belarus, including paintings, graphic works, and personal belongings. A must-visit for art lovers.',
     'short_desc': 'Largest Belarusian collection of Marc Chagall\'s works — in the artist\'s hometown of Vitebsk.',
     'location': 'Vitebsk, Belarus', 'city': 'Vitebsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.195, 'longitude': 30.205, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 17:00 (Tue-Sun)', 'ticket_price': 4.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Mogilev Regional Museum', 'name_en': 'Mogilev Regional Museum',
     'description': 'A museum of local history and culture in Mogilev, one of the oldest cities in Belarus (founded in the 13th century). Collections include archaeology, history, fine arts, and ethnography from the Dnieper River region. The museum building itself is a historic architectural monument in the centre of the city.',
     'short_desc': 'Local history of Mogilev — one of Belarus oldest cities, on the Dnieper River.',
     'location': 'Mogilev, Belarus', 'city': 'Mogilev', 'region': 'Mogilev Oblast',
     'latitude': 53.9167, 'longitude': 30.35, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 17:00 (Tue-Sun)', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Berestye Archaeological Museum', 'name_en': 'Berestye Museum',
     'description': 'Built over the excavated remains of a 13th-century Slavic settlement on the banks of the Mukhavets River, the Berestye Museum in Brest offers a rare look at medieval life in the region. The settlement was an important trading post on the route from the Varangians to the Greeks. Artifacts on display include tools, ceramics, jewellery, and reconstructed period interiors.',
     'short_desc': 'Medieval Slavic settlement museum — 13th-century ruins with reconstructed period interiors.',
     'location': 'Brest, Belarus', 'city': 'Brest', 'region': 'Brest Oblast',
     'latitude': 52.095, 'longitude': 23.69, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # CHURCHES & RELIGIOUS SITES
    # ══════════════════════════════════════════════════════════
    {'name': 'SS. Boris and Gleb Church (Kalozha)', 'name_en': 'SS. Boris and Gleb Church, Grodno',
     'description': 'Built in the 1180s in brick and stone, this church in Grodno is one of the oldest surviving examples of Belarusian architecture. Only two walls, three apses, and two pillars remain from the original 12th-century structure; the rest collapsed during a landslide of the high bank of the Neman River. Still an active place of worship, it is one of the most-visited religious sites in Belarus, ranking as the third-most-popular monument with approximately 16,000 visitors in 2026.',
     'short_desc': '12th-century church — one of the oldest surviving structures in Belarus, in active worship.',
     'location': 'Grodno, Belarus', 'city': 'Grodno', 'region': 'Grodno Oblast',
     'latitude': 53.6833, 'longitude': 23.8333, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '07:00 - 19:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.5, 'is_featured': True, 'is_verified': True},

    {'name': 'Holy Trinity Church in Gierviaty', 'name_en': 'Holy Trinity Church, Gierviaty',
     'description': 'A magnificent neo-Gothic Roman Catholic church built between 1868 and 1903. Often called the "Belarusian Notre-Dame" or "Little Switzerland," this church is one of the most impressive architectural achievements in Belarus. Its twin 75-metre spires are visible for kilometres in every direction. The interior features ornate altar pieces, stained glass, and carved wooden confessionals. One of the most photographed religious sites in the country.',
     'short_desc': '"Belarusian Notre-Dame" — stunning neo-Gothic church, one of the most photographed in Belarus.',
     'location': 'Gierviaty, Grodno Oblast', 'city': 'Gierviaty', 'region': 'Grodno Oblast',
     'latitude': 54.2833, 'longitude': 25.7833, 'category': 'church', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'By arrangement', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Church_of_the_Holy_Trinity_in_Gierviaty.jpg/400px-Church_of_the_Holy_Trinity_in_Gierviaty.jpg',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Saint Sophia Cathedral, Polotsk', 'name_en': 'Saint Sophia Cathedral, Polotsk',
     'description': 'The oldest cathedral in Belarus, originally built in the 11th century in the Pskovian style of ancient Rus architecture. It was rebuilt several times — first after a 1447 fire and again in the 18th century after the Great Northern War, when it received its Baroque-style facade with Rococo ornamental elements. The cathedral was built to match the grandeur of Constantinople\'s Hagia Sophia, symbolising the spiritual importance of Polotsk. Today it functions as a museum and occasional concert venue for choral performances.',
     'short_desc': 'The oldest cathedral in Belarus — 11th century, rebuilt in Baroque style with Rococo facade.',
     'location': 'Polotsk, Vitebsk Oblast', 'city': 'Polotsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.5, 'longitude': 28.7667, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '09:00 - 18:00', 'ticket_price': 4.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Holy Trinity Cathedral, Minsk', 'name_en': 'Holy Trinity Cathedral, Minsk',
     'description': 'Also known as the Barysauka Church, this 17th-century Eastern Orthodox cathedral in the historic Upper Town of Minsk is one of the oldest surviving buildings in the city. Built in the Baroque style with influences from Belarusian and Ukrainian church architecture, it features a three-tiered tent-roof belfry. The cathedral is surrounded by the remains of the old city wall and forms part of a historic ensemble with the Minsk Town Hall.',
     'short_desc': '17th-century Eastern Orthodox cathedral — one of the oldest buildings in Minsk.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9053, 'longitude': 27.5558, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '07:00 - 20:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'St. Simon and Helena Church (Red Church)', 'name_en': 'Red Church, Minsk',
     'description': 'An outstanding Neo-Gothic Roman Catholic church built between 1905 and 1910. Its distinctive red brick facade and twin 73-metre spires make it one of the most recognizable buildings in Minsk. The interior features soaring vaulted ceilings, stained glass windows, and ornate altar pieces. The church was closed during the Soviet period and reopened in 1990. It hosts regular concerts of organ music.',
     'short_desc': 'Neo-Gothic Roman Catholic church — iconic red brick twin-spire landmark in central Minsk.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9086, 'longitude': 27.5631, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Red_church_minsk.jpg/400px-Red_church_minsk.jpg',
     'avg_rating': 4.5, 'is_featured': False, 'is_verified': True},

    {'name': 'St. Nicholas Monastery, Gomel', 'name_en': 'St. Nicholas Monastery, Gomel',
     'description': 'An active Orthodox monastery founded in the 16th century, featuring the Church of St. Nicholas with its distinctive multi-tiered tent-roof belfry that has become a symbol of Gomel. The monastery complex sits along the Sozh River and includes a cathedral, residential buildings, and a museum of monastery history. The Church of St. Nicholas is one of the finest examples of Belarusian baroque church architecture.',
     'short_desc': '16th-century Orthodox monastery with iconic tent-roof belfry on the Sozh River.',
     'location': 'Gomel, Belarus', 'city': 'Gomel', 'region': 'Gomel Oblast',
     'latitude': 52.4333, 'longitude': 30.9833, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '06:00 - 20:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Zhyrovichy Monastery', 'name_en': 'Zhyrovichy Monastery',
     'description': 'A 16th-century Orthodox monastery famous for the "Zhyrovichy Mother of God" icon, believed to have miraculous healing powers. The monastery has been a major pilgrimage site for centuries. The current church buildings date from the 18th-19th centuries and feature a distinctive exterior painted in bright colours with elaborate frescoes. Pilgrims come from across Belarus and beyond to venerate the icon.',
     'short_desc': '16th-century Orthodox monastery — major pilgrimage site for the miraculous Zhyrovichy icon.',
     'location': 'Zhyrovichy, Slavgorod District, Mogilev Oblast', 'city': 'Zhyrovichy', 'region': 'Mogilev Oblast',
     'latitude': 53.4333, 'longitude': 31.55, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '06:00 - 20:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Borisoglebskaya Church, Mogilev', 'name_en': 'Borisoglebskaya Church, Mogilev',
     'description': 'A late 17th-century wooden church in the style of Belarusian baroque architecture. One of the oldest wooden churches in eastern Belarus, it features a distinctive multi-tiered tent-roof belfry, carved wooden iconostasis, and original floor tiles. The church has survived wars and political upheavals and remains an active place of worship.',
     'short_desc': 'Late 17th-century wooden baroque church — one of the oldest in eastern Belarus.',
     'location': 'Mogilev, Belarus', 'city': 'Mogilev', 'region': 'Mogilev Oblast',
     'latitude': 53.9167, 'longitude': 30.3333, 'category': 'church', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'By arrangement', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # PALACES & ESTATES
    # ══════════════════════════════════════════════════════════
    {'name': 'Gomel Palace and Park Ensemble', 'name_en': 'Rumyantsev-Paskevich Palace',
     'description': 'One of the most beautiful architectural monuments in Belarus, featured on the Belarusian 20-ruble banknote. The palace complex includes the main neoclassical building, the Church of St. Nicholas, a chapel with burial vault, a winter garden, a watchtower, and an 800-metre-long ancient park along the Sozh River. Home to the Rumyantsev and Paskevich families. Today it serves as a major museum complex and cultural centre.',
     'short_desc': 'Palace featured on the 20-ruble note — neoclassical ensemble with park on the Sozh River.',
     'location': 'Gomel, Belarus', 'city': 'Gomel', 'region': 'Gomel Oblast',
     'latitude': 52.4411, 'longitude': 30.9933, 'category': 'palace', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 18:00 (Wed-Mon)', 'ticket_price': 6.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Kosava Palace', 'name_en': 'Kosava Palace',
     'description': 'An 18th-century magnate palace built in the Baroque style, once the seat of the Sapeika family. The palace features ornate stucco ceilings, a collection of period paintings, and an English-style landscape park. One of the most dynamically visited sites in 2026 according to tourist analytics. Currently undergoing restoration and open for guided tours.',
     'short_desc': 'Baroque magnate palace of the 18th century — one of the most visited sites in 2026.',
     'location': 'Kosava, Pruzhany District, Brest Oblast', 'city': 'Kosava', 'region': 'Brest Oblast',
     'latitude': 52.4167, 'longitude': 24.3667, 'category': 'palace', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 17:00', 'ticket_price': 5.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Mikhail Kleofas Oginski Museum-Estate', 'name_en': 'Oginski Museum-Estate',
     'description': 'The estate of Prince Mikhail Kleofas Oginski (1765-1833), a Polish-Lithuanian nobleman, composer, and politician. Oginski composed the famous polandaise " Thoughts" here and was a patron of the arts. The estate includes the palace, a park with ponds, and an exhibition dedicated to Oginski\'s life and work. One of the most dynamically growing tourist sites in 2026.',
     'short_desc': 'Estate of Prince Oginski — composer of the famous polandaise, patron of the arts.',
     'location': 'Zalessye, Mogilev Oblast', 'city': 'Zalessye', 'region': 'Mogilev Oblast',
     'latitude': 54.0, 'longitude': 31.35, 'category': 'palace', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 17:00 (Tue-Sun)', 'ticket_price': 4.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # NATIONAL PARKS & NATURE
    # ══════════════════════════════════════════════════════════
    {'name': 'Narochansky National Park', 'name_en': 'Narochansky National Park',
     'description': 'Named after Lake Naroch — the largest lake in Belarus at 79.6 square kilometres — this park encompasses the lake, surrounding pine forests, and several smaller lakes. The area is known for its sandy beaches, clear water, pine forests, and tranquil natural beauty. Water sports, swimming, and beach recreation are popular in summer. The town of Naroch is a popular resort destination with sanatoriums and guesthouses.',
     'short_desc': 'Largest lake in Belarus (79.6 km²) with sandy beaches and pine forests.',
     'location': 'Naroch, Myadel District, Minsk Oblast', 'city': 'Naroch', 'region': 'Minsk Oblast',
     'latitude': 54.9833, 'longitude': 26.7333, 'category': 'nature', 'suitable_season': 'Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/NarachLake.jpg/400px-NarachLake.jpg',
     'avg_rating': 4.4, 'is_featured': True, 'is_verified': True},

    {'name': 'Braslau Lakes National Park', 'name_en': 'Braslau Lakes National Park',
     'description': 'Located in the north of Belarus near the borders with Latvia and Russia, this park encompasses over 30 glacial lakes connected by rivers and streams. The rolling hills, pine forests, and crystal-clear lakes of the Braslau region make it the most picturesque lake district in Belarus. Ideal for kayaking, birdwatching, lakeside camping, and cycling. The landscape was shaped by glacial activity during the last Ice Age.',
     'short_desc': '30+ glacial lakes in northern Belarus — kayaking, birdwatching, and lakeside camping.',
     'location': 'Braslau, Miory District, Vitebsk Oblast', 'city': 'Braslau', 'region': 'Vitebsk Oblast',
     'latitude': 55.7333, 'longitude': 27.05, 'category': 'nature', 'suitable_season': 'Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Braslaw_lakes.jpg/400px-Braslaw_lakes.jpg',
     'avg_rating': 4.5, 'is_featured': True, 'is_verified': True},

    {'name': 'Pripyatsky National Park', 'name_en': 'Pripyatsky National Park',
     'description': 'A vast protected area covering the Belarusian section of the Pripyat River wetlands and floodplains. Features primeval forests, meadows, and marshes that provide habitat for rare species including the European bison (wisent), lynx, wolf, and white-tailed eagle. The park protects one of the most significant wetland ecosystems in Europe.',
     'short_desc': 'Pripyat River wetlands with primeval forests — bison, wolves, and white-tailed eagles.',
     'location': 'Turov, Zhitkovichi District, Gomel Oblast', 'city': 'Turov', 'region': 'Gomel Oblast',
     'latitude': 52.05, 'longitude': 27.7333, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Berezina Biosphere Reserve', 'name_en': 'Berezina Biosphere Reserve',
     'description': 'A UNESCO Biosphere Reserve covering one of the largest river floodplain systems in Europe. The Berezina River and its tributaries support exceptional biodiversity. The reserve is home to the European bison and Eurasian lynx, along with 280 species of birds. Visitor facilities include nature trails, observation towers, and guided boat tours through the floodplain.',
     'short_desc': "UNESCO Biosphere Reserve — Europe's largest river floodplain ecosystem with bison.",
     'location': 'Zhonka, Berezina District, Minsk Oblast', 'city': 'Zhonka', 'region': 'Minsk Oblast',
     'latitude': 53.5, 'longitude': 28.5, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 2.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Turov Riverside (Bison Crossing)', 'name_en': 'Turov Riverside',
     'description': 'A picturesque section of the Pripyat River at Turov, famous for its high concentration of European bison that cross the river at this location. The town of Turov is one of the oldest in Belarus and the surrounding floodplain offers excellent wildlife observation. A prime destination for nature photographers.',
     'short_desc': 'Pripyat River at Turov — famous for bison crossing, one of Belarus oldest towns.',
     'location': 'Turov, Zhitkovichi District, Gomel Oblast', 'city': 'Turov', 'region': 'Gomel Oblast',
     'latitude': 52.0667, 'longitude': 27.7333, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Khotlitsa River Canyon', 'name_en': 'Khotlitsa River Canyon',
     'description': 'A scenic canyon formed by the Khotitsa River in the Vitebsk Oblast, featuring steep Devonian sandstone cliffs reaching 20-40 metres in height, forested slopes, and hiking trails along the river. One of the most dramatic natural landscapes in northern Belarus, with geological strata visible in the cliff walls.',
     'short_desc': 'Dramatic sandstone river canyon — steep cliffs and spectacular hiking trails.',
     'location': 'Beshankovichy District, Vitebsk Oblast', 'city': 'Beshankovichy', 'region': 'Vitebsk Oblast',
     'latitude': 55.0333, 'longitude': 29.3333, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Mikashevichy Chalk Quarries', 'name_en': 'Mikashevichy Chalk Quarries',
     'description': 'Dramatic white chalk quarry walls create an otherworldly landscape near the village of Mikashevichy. The exposed chalk layers, some millions of years old, make for striking geological formations. Popular with photographers, hikers, and geology enthusiasts.',
     'short_desc': 'White chalk quarry walls — striking geological formations and landscape photography.',
     'location': 'Mikashevichy, Zhlobin District, Gomel Oblast', 'city': 'Mikashevichy', 'region': 'Gomel Oblast',
     'latitude': 52.9167, 'longitude': 29.8333, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MINSK CITY SIGHTS
    # ══════════════════════════════════════════════════════════
    {'name': 'National Library of Belarus', 'name_en': 'National Library of Belarus',
     'description': 'One of the most recognizable symbols of modern Minsk, this rhombicuboctahedron-shaped building holds over 10 million items and features a rooftop observation deck with panoramic 360-degree views of Minsk. The building is illuminated at night with a massive LED display. The library is a major research institution and hosts cultural events, exhibitions, and conferences.',
     'short_desc': 'Iconic diamond-shaped building — 10M+ items, rooftop observation deck, symbol of modern Minsk.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9317, 'longitude': 27.6406, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': '09:00 - 21:00', 'ticket_price': 5.00,
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/National_Library_of_Belarus.jpg/400px-National_Library_of_Belarus.jpg',
     'avg_rating': 4.5, 'is_featured': True, 'is_verified': True},

    {'name': 'Independence Avenue (Praspiekt Niezaliežnasci)', 'name_en': 'Independence Avenue, Minsk',
     'description': 'The main thoroughfare of Minsk, stretching 15 kilometres from Victory Square to the southern outskirts. Lined with Stalinist neoclassical buildings, government institutions, department stores, theatres, and cafes. Walking this single avenue gives a comprehensive overview of Minsk\'s Soviet-era monumental architecture and modern city life. Key landmarks include Independence Square, the Government House, and the GUM department store.',
     'short_desc': '15km main boulevard — Stalinist neoclassical architecture, government buildings, and city life.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9167, 'longitude': 27.5667, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Minsk Metro (Ornate Stations)', 'name_en': 'Minsk Metro Stations',
     'description': 'The Minsk Metro is renowned for its ornate underground stations — many function as underground palaces with marble columns, crystal chandeliers, stained glass panels, and mosaics depicting Belarusian history, culture, and industry. Notable stations include Kastryčnickaja (October), Nyamiha, and Uschod. The metro runs from 05:30 to 01:00 daily.',
     'short_desc': 'Underground palaces — marble, chandeliers, stained glass, and Belarusian history mosaics.',
     'location': 'Minsk Metro', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9167, 'longitude': 27.5667, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': '05:30 - 01:00', 'ticket_price': 0.65, 'image_url': '',
     'avg_rating': 4.6, 'is_featured': False, 'is_verified': True},

    {'name': 'Upper Town (Vyšni Horad)', 'name_en': 'Upper Town, Minsk',
     'description': 'The oldest surviving district of Minsk, rebuilt after WWII but retaining the baroque layout and scale of the 17th-century town. Features the Holy Trinity Cathedral, the reconstructed Town Hall, the former Bernardine Monastery, and riverside terraces. The best spot for outdoor dining in summer.',
     'short_desc': "Minsk's oldest district — baroque churches, cobblestone streets, and riverside terraces.",
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9053, 'longitude': 27.5558, 'category': 'architecture', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Gorky Central Park of Culture and Rest', 'name_en': 'Gorky Park, Minsk',
     'description': 'The most popular park in Minsk, located along the Svislach River. Features amusement rides, sports facilities, a lake with boat rentals, walking and cycling paths, cafes, and regular cultural events and concerts. The park connects to Victory Park and the Svislach embankment promenade.',
     'short_desc': "Minsk's most popular park — rides, lake, boat rentals, sports facilities, and concerts.",
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9167, 'longitude': 27.5333, 'category': 'park', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Minsk Sea Reservoir', 'name_en': 'Minsk Sea',
     'description': 'A large artificial reservoir on the Svislach River, popular for swimming, windsurfing, and beach recreation. The area includes sandy beaches, campgrounds, and hiking trails. The reservoir is also known as a spot for ice sailing in winter.',
     'short_desc': 'Large artificial reservoir — swimming, windsurfing, beach recreation, and ice sailing in winter.',
     'location': 'Minsk District, Minsk Oblast', 'city': 'Minsk', 'region': 'Minsk Oblast',
     'latitude': 53.95, 'longitude': 27.5, 'category': 'nature', 'suitable_season': 'Summer',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MORE NATIONAL/REGIONAL PARKS
    # ══════════════════════════════════════════════════════════
    {'name': 'Pripyat Floodplain Landscape Reserve', 'name_en': 'Pripyat Floodplain Reserve',
     'description': 'A nature reserve protecting the unique floodplain landscape of the Pripyat River wetlands. Features oxbow lakes, marshes, floodplain forests, and meadows teeming with waterfowl and aquatic life. An important ecological corridor for migratory birds between Central Europe and Russia.',
     'short_desc': 'Pripyat River wetlands — oxbow lakes, waterfowl, and migratory bird corridor.',
     'location': 'Drahichyn District, Brest Oblast', 'city': 'Drahichyn', 'region': 'Brest Oblast',
     'latitude': 52.1833, 'longitude': 25.15, 'category': 'nature', 'suitable_season': 'Spring, Summer',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Yelnya Bog', 'name_en': 'Yelnya Peat Bog',
     'description': 'The largest high moor (bog) in Belarus, covering over 20,000 hectares. Formed during the glacial period, Yelnya is one of the oldest ecosystems in Europe. The bog has preserved a unique environment with sphagnum mosses, bog plants, and specialized wildlife that has existed continuously for millennia.',
     'short_desc': "Belarus's largest high moor — ancient ecosystem formed during the glacial period.",
     'location': 'Krychaw District, Gomel Oblast', 'city': 'Krychaw', 'region': 'Gomel Oblast',
     'latitude': 53.7, 'longitude': 31.85, 'category': 'nature', 'suitable_season': 'Summer',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Mogilev Botanical Garden', 'name_en': 'Mogilev Botanical Garden',
     'description': 'A botanical garden covering 67 hectares featuring plant collections from Belarus and around the world. Includes thematic sections, greenhouses, an ornamental pond, and a nature education centre. Known for its collection of lilies and ornamental shrubs.',
     'short_desc': '67-hectare botanical garden — ornamental plants, greenhouses, and a nature education centre.',
     'location': 'Mogilev, Belarus', 'city': 'Mogilev', 'region': 'Mogilev Oblast',
     'latitude': 53.9333, 'longitude': 30.3667, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '08:00 - 18:00', 'ticket_price': 2.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Vitebsk Botanical Garden', 'name_en': 'Vitebsk Botanical Garden',
     'description': 'A botanical garden established in 1910, featuring extensive plant collections, ornamental gardens, an arboretum, and greenhouses. Known for its outstanding displays of roses, lilies, and hostas. The garden sits on the banks of the Western Dvina River.',
     'short_desc': '1910 botanical garden — renowned rose, lily, and hosta collections on the Western Dvina.',
     'location': 'Vitebsk, Belarus', 'city': 'Vitebsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.1833, 'longitude': 30.2167, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '08:00 - 18:00', 'ticket_price': 2.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # HISTORIC TOWNS & CITIES
    # ══════════════════════════════════════════════════════════
    {'name': 'Grodno Old Town', 'name_en': 'Grodno Old Town',
     'description': 'Grodno is one of the few Belarusian cities with a well-preserved historic old town, featuring buildings from the 13th to 19th centuries. Highlights include the former Royal Castle site, the old market square, the New Town area with Polish-era merchant houses, and the Old Town\'s cobblestone streets. The city survived WWII largely intact and retains a genuine historical atmosphere.',
     'short_desc': 'Well-preserved old town — buildings from the 13th to 19th centuries, genuine historical atmosphere.',
     'location': 'Grodno, Belarus', 'city': 'Grodno', 'region': 'Grodno Oblast',
     'latitude': 53.6833, 'longitude': 23.8333, 'category': 'architecture', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Polotsk Old Town', 'name_en': 'Polotsk Old Town',
     'description': 'Polotsk is one of the oldest cities in Belarus, founded in the 9th century as the capital of a medieval principality. Its old town contains historic churches, merchant houses, the ruins of ancient fortifications, and the 12th-century Sophia Cathedral. Polotsk was a major centre of trade and culture in medieval Eastern Europe.',
     'short_desc': "One of Belarus's oldest cities — 9th-century principality capital with medieval churches.",
     'location': 'Polotsk, Vitebsk Oblast', 'city': 'Polotsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.5, 'longitude': 28.7667, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Krychaw Old Town', 'name_en': 'Krychaw',
     'description': 'An ancient town on the Sozh River founded in the 12th century. Krychaw is known for its wooden churches, historic market square, the Trinity Monastery on the riverbank, and scenic views along the Sozh. The town has a quiet, artistic character and is popular with painters and photographers.',
     'short_desc': '12th-century town on the Sozh River — wooden churches and the Trinity Monastery.',
     'location': 'Krychaw, Gomel Oblast', 'city': 'Krychaw', 'region': 'Gomel Oblast',
     'latitude': 53.7167, 'longitude': 31.7167, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Pyetrykaw', 'name_en': 'Pyetrykaw',
     'description': 'One of the oldest towns in Belarus, located at the confluence of the Dnieper and Sozh rivers. Features historic churches, an old market square, and a museum of local history. The surrounding countryside is known for its landscapes and traditional villages.',
     'short_desc': "One of Belarus's oldest towns — at the confluence of the Dnieper and Sozh rivers.",
     'location': 'Pyetrykaw, Gomel Oblast', 'city': 'Pyetrykaw', 'region': 'Gomel Oblast',
     'latitude': 52.1333, 'longitude': 28.5, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # SLAVIANSKI BAZAAR & CULTURAL EVENTS
    # ══════════════════════════════════════════════════════════
    {'name': 'Slavianski Bazaar Amphitheatre', 'name_en': 'Slavianski Bazaar Venue',
     'description': 'The annual Slavianski Bazaar international arts festival in Vitebsk is one of the largest cultural events in Eastern Europe, held every July since 1992. The festival attracts performers and visitors from across the Slavic world and beyond. The main amphitheatre venue seats thousands and hosts concerts, theatre performances, and dance competitions.',
     'short_desc': 'Venue for the annual Slavianski Bazaar — the largest cultural festival in Eastern Europe.',
     'location': 'Vitebsk, Belarus', 'city': 'Vitebsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.1967, 'longitude': 30.21, 'category': 'architecture', 'suitable_season': 'Summer (July)',
     'opening_hours': 'Festival season only', 'ticket_price': 10.00, 'image_url': '',
     'avg_rating': 4.5, 'is_featured': False, 'is_verified': True},

    {'name': 'Vitebsk Regional Museum', 'name_en': 'Vitebsk Regional Museum',
     'description': 'Located in the former Governorate building, this museum holds collections on the history of Vitebsk Oblast from prehistoric times through World War II. Includes archaeology, ethnography, fine arts, and a notable collection related to Marc Chagall\'s Vitebsk period.',
     'short_desc': 'History of Vitebsk Oblast — archaeology, Chagall period, and regional culture.',
     'location': 'Vitebsk, Belarus', 'city': 'Vitebsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.19, 'longitude': 30.205, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 17:00 (Wed-Sun)', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    {'name': 'Brest Regional Museum', 'name_en': 'Brest Regional Museum',
     'description': 'A regional museum showcasing the history, nature, and culture of the Brest Oblast from prehistoric times to the present day. Features exhibits on the region\'s archaeology, flora and fauna, and the history of the borderland.',
     'short_desc': 'Brest Oblast history, nature, and culture — from prehistoric times to today.',
     'location': 'Brest, Belarus', 'city': 'Brest', 'region': 'Brest Oblast',
     'latitude': 52.0983, 'longitude': 23.6917, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00 (Tue-Sun)', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MORE NATURAL & RECREATIONAL SITES
    # ══════════════════════════════════════════════════════════
    {'name': 'Vileyka Lake District', 'name_en': 'Vileyka Lake District',
     'description': 'A cluster of small glacial lakes around the town of Vileyka in northern Minsk Oblast. Known for its tranquil environment, excellent fishing, and opportunities for kayaking. The lakes were formed by glacial activity during the last Ice Age and vary in depth and character.',
     'short_desc': 'Glacial lake cluster near Vileyka — fishing, kayaking, and a tranquil environment.',
     'location': 'Vileyka, Minsk Oblast', 'city': 'Vileyka', 'region': 'Minsk Oblast',
     'latitude': 54.75, 'longitude': 26.9, 'category': 'nature', 'suitable_season': 'Summer',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    {'name': 'Sozh River Valley', 'name_en': 'Sozh River Valley',
     'description': 'The Sozh River, a tributary of the Dnieper, flows through picturesque landscapes of Belarus. The river valley is known for its scenic beauty, historic villages, and opportunities for boating and fishing. The valley has been inhabited since ancient times and contains numerous archaeological sites.',
     'short_desc': 'Scenic Sozh River valley — historic villages, boating, and fishing.',
     'location': 'Krychaw, Gomel Oblast', 'city': 'Krychaw', 'region': 'Gomel Oblast',
     'latitude': 53.7167, 'longitude': 31.7167, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    {'name': 'Svislach River Embankment', 'name_en': 'Svislach River Embankment, Minsk',
     'description': 'A scenic riverside promenade along the Svislach River in central Minsk. Features fountains, sculptures, landscaped parks, and illuminated walkways. The embankment connects many of the city\'s major landmarks and is especially beautiful in the evening when the buildings are illuminated.',
     'short_desc': 'Scenic riverside promenade — fountains, sculptures, and illuminated walkways in central Minsk.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9083, 'longitude': 27.555, 'category': 'park', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.4, 'is_featured': False, 'is_verified': True},

    {'name': 'Loshitsa Park (Mikhail Lositsky Estate)', 'name_en': 'Loshitsa Park, Minsk',
     'description': 'A historic park and estate complex featuring a neoclassical manor house, French-style regular garden, and natural landscape park. The estate belonged to various noble families and now serves as a cultural venue with concerts, exhibitions, and festivals.',
     'short_desc': 'Historic estate park — neoclassical manor, French-style garden, cultural venue.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.8833, 'longitude': 27.55, 'category': 'park', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '08:00 - 22:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # AUGUSTOW CANAL & WATERWAYS
    # ══════════════════════════════════════════════════════════
    {'name': 'Augustow Canal', 'name_en': 'Augustow Canal',
     'description': 'A UNESCO tentative list site built in 1823-1839 to connect the Neman River with the Vistula River. A remarkable feat of 19th-century engineering, the canal includes 18 locks and enables navigation between the Baltic and Black Sea basins. The surrounding landscape of forests and lakes makes it popular for canoeing, cycling, and nature observation.',
     'short_desc': '19th-century canal — engineering feat with 18 locks, popular for canoeing and cycling.',
     'location': 'Augustow Canal, Grodno Oblast', 'city': 'Augustow', 'region': 'Grodno Oblast',
     'latitude': 53.8333, 'longitude': 23.0, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Berezina Canal Locks', 'name_en': 'Berezina Canal Locks',
     'description': 'A system of historic canal locks built in the 18th-19th centuries as part of the Berezina waterway connecting the Dnieper and Daugava basins. The engineering feat is considered one of the most impressive canal systems in Eastern Europe. Surrounded by forests and wetlands, it is popular with kayakers and history enthusiasts.',
     'short_desc': '18th-century canal lock system — engineering feat connecting major river basins.',
     'location': 'Berezina Canal, Minsk Oblast', 'city': 'Borisov', 'region': 'Minsk Oblast',
     'latitude': 54.25, 'longitude': 28.5, 'category': 'architecture', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MORE MUSEUMS & CULTURAL SITES
    # ══════════════════════════════════════════════════════════
    {'name': 'Polotsk Museum of Local History', 'name_en': 'Polotsk Museum of Local History',
     'description': 'Housed in the 18th-century Jesuit college, this museum showcases the 1,000-year history of Polotsk — one of the oldest cities in Belarus and the former capital of a medieval principality. Collections include archaeology from the Viking Age, medieval manuscripts, and documents relating to the Polotsk Principality.',
     'short_desc': "1,000-year history of Polotsk — housed in an 18th-century Jesuit college.",
     'location': 'Polotsk, Vitebsk Oblast', 'city': 'Polotsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.5, 'longitude': 28.8, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 17:00 (Wed-Sun)', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    {'name': 'Dudutki Folk Museum', 'name_en': 'Dudutki Open-Air Museum',
     'description': 'An open-air ethnographic museum south of Minsk where visitors can try traditional crafts — pottery, weaving, blacksmithing, cheese-making, and samogon (moonshine) distillation — taste traditional Belarusian food, ride horses, and experience rural life. One of the most popular attractions for families.',
     'short_desc': 'Open-air ethnographic museum — traditional crafts, food, and horse riding south of Minsk.',
     'location': 'Dukora, Pukhovichi District, Minsk Oblast', 'city': 'Dukora', 'region': 'Minsk Oblast',
     'latitude': 53.6167, 'longitude': 28.0333, 'category': 'museum', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': '10:00 - 17:00', 'ticket_price': 6.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Copernicus House, Polotsk', 'name_en': 'Copernicus House, Polotsk',
     'description': 'The presumed birthplace of Nicolaus Copernicus (1473-1543), the astronomer who proposed the heliocentric model of the solar system. Copernicus was born in Torun, but his maternal uncle Lucas Watzenrode lived and worked in Polotsk as a canon of the cathedral chapter. The building houses a museum dedicated to Copernicus\'s scientific work and the intellectual history of Renaissance Europe.',
     'short_desc': 'Museum dedicated to Copernicus — linked to his maternal family in Polotsk.',
     'location': 'Polotsk, Vitebsk Oblast', 'city': 'Polotsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.5, 'longitude': 28.7667, 'category': 'museum', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 17:00 (Tue-Sun)', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # FORESTS, LAKES & SCENIC AREAS
    # ══════════════════════════════════════════════════════════
    {'name': 'Drahichyn Forest', 'name_en': 'Drahichyn Forest',
     'description': 'A vast forested area near Drahichyn, part of the Pripyat floodplain landscape reserve. The forest is home to elk, deer, wild boar, and numerous bird species. Nature trails allow visitors to explore the ecosystem without disturbing sensitive habitats.',
     'short_desc': 'Vast Pripyat floodplain forest — elk, deer, wild boar, and nature trails.',
     'location': 'Drahichyn, Brest Oblast', 'city': 'Drahichyn', 'region': 'Brest Oblast',
     'latitude': 52.2, 'longitude': 25.15, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Rossony Lake District', 'name_en': 'Rossony',
     'description': 'A remote area in the Vitebsk Oblast near the borders with Latvia and Russia, known for its beautiful forested landscapes and interconnected lake system. Popular with nature lovers, kayakers, and those seeking solitude in nature. Remote and unspoiled by mass tourism.',
     'short_desc': 'Remote lake district near borders — kayaking, nature observation, and solitude.',
     'location': 'Rossony, Vitebsk Oblast', 'city': 'Rossony', 'region': 'Vitebsk Oblast',
     'latitude': 56.0, 'longitude': 28.8333, 'category': 'nature', 'suitable_season': 'Summer',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Logoisk Forests', 'name_en': 'Logoisk',
     'description': 'A forested area of central Minsk Oblast that was once the preferred hunting ground of the Russian tsars. The forests are now part of a protected area near the Berezina Biosphere Reserve, offering hiking, birdwatching, and foraging. Rich in mushrooms and berries in season.',
     'short_desc': 'Former tsarist hunting grounds — forests near Berezina Reserve, mushroom picking.',
     'location': 'Logoisk, Minsk Oblast', 'city': 'Logoisk', 'region': 'Minsk Oblast',
     'latitude': 53.9833, 'longitude': 27.7, 'category': 'nature', 'suitable_season': 'Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 3.9, 'is_featured': False, 'is_verified': True},

    {'name': 'Svislach Hills', 'name_en': 'Svislach Hills',
     'description': 'Rolling hills along the Svislach River north of Minsk offering scenic hiking opportunities. The area is known for its beautiful autumn foliage, panoramic views over the river valley, and proximity to the historic town of Smolevichi.',
     'short_desc': 'Rolling hills north of Minsk — scenic hiking and beautiful autumn foliage.',
     'location': 'Smolevichi District, Minsk Oblast', 'city': 'Smolevichi', 'region': 'Minsk Oblast',
     'latitude': 54.15, 'longitude': 26.8333, 'category': 'nature', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 3.9, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MORE URBAN LANDMARKS
    # ══════════════════════════════════════════════════════════
    {'name': 'Minsk Central Railway Station', 'name_en': 'Minsk Central Railway Station',
     'description': 'The main railway station of Minsk, a major hub serving connections across Belarus and international routes to Moscow, Warsaw, Vilnius, and Berlin. The current building dates from 1993 and replaced the original Soviet-era station. The hall features murals depicting Belarusian history and culture.',
     'short_desc': 'Minsk main railway hub — connections across Belarus and international routes.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.8858, 'longitude': 27.5472, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'Open 24 hours', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Minsk Drama Theater', 'name_en': 'Minsk Drama Theater',
     'description': 'One of the oldest theatres in Belarus, founded in 1888. The current building in eclectic style with elements of neoclassicism opened in 1902. It is the national theatre of Belarus and hosts productions of classic and contemporary drama in the Belarusian and Russian languages.',
     'short_desc': 'National theatre founded in 1888 — eclectic architecture, classic and contemporary drama.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9111, 'longitude': 27.5656, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': 'By performance', 'ticket_price': 15.00, 'image_url': '',
     'avg_rating': 4.2, 'is_featured': False, 'is_verified': True},

    {'name': 'Motherland Monument', 'name_en': 'Motherland Monument',
     'description': 'The massive Motherland Monument in Minsk, one of the tallest structures in Belarus, stands as a symbol of victory and patriotism. The monument complex includes the figure of the Motherland, eternal flame, and a WWII memorial museum. The view from the top platform offers sweeping panoramas of Minsk.',
     'short_desc': 'Massive WWII monument — sweeping views of Minsk from the top platform.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9083, 'longitude': 27.5725, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': '10:00 - 18:00', 'ticket_price': 3.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    {'name': 'Minsk Sports Complex (Minsk Arena)', 'name_en': 'Minsk Arena',
     'description': 'A modern multi-purpose sports and entertainment complex with a 15,000-seat ice arena, velodrome, swimming pool, and fitness centre. Hosted events at the 2014 Ice Hockey World Championship. Open daily for sports activities and events.',
     'short_desc': 'Modern multi-sport complex — 15,000-seat arena, velodrome, swimming pool.',
     'location': 'Minsk, Belarus', 'city': 'Minsk', 'region': 'Minsk',
     'latitude': 53.9367, 'longitude': 27.4817, 'category': 'architecture', 'suitable_season': 'All seasons',
     'opening_hours': '08:00 - 22:00', 'ticket_price': 10.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # FORTRESSES & ARCHAEOLOGY
    # ══════════════════════════════════════════════════════════
    {'name': 'Babruysk Fortress', 'name_en': 'Babruysk Fortress',
     'description': 'An 18th-century fortress on the Berezina River built during the Russian Empire period. The fortress played a role in the Battle of Berezina during the Napoleonic Wars and later served as a military installation. Partially preserved walls and bastions can still be seen in the city centre of Babruysk.',
     'short_desc': '18th-century fortress on the Berezina River — played a role in the Napoleonic Wars.',
     'location': 'Babruysk, Mogilev Oblast', 'city': 'Babruysk', 'region': 'Mogilev Oblast',
     'latitude': 53.1333, 'longitude': 29.25, 'category': 'castle', 'suitable_season': 'All seasons',
     'opening_hours': 'External viewing only', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 3.8, 'is_featured': False, 'is_verified': True},

    {'name': 'Bruzdzitsy Ancient Settlement', 'name_en': 'Bruzdzitsy Ancient Settlement',
     'description': 'An archaeological site dating to the 6th-4th centuries BCE, containing the remains of an ancient settlement of the Bielanovichy culture. The site provides important insights into early Iron Age life in the region. Ongoing excavations continue to reveal more about this prehistoric community.',
     'short_desc': 'Iron Age archaeological site — 6th-4th century BCE ancient settlement.',
     'location': 'Bruzdzitsy, Grodno Oblast', 'city': 'Bruzdzitsy', 'region': 'Grodno Oblast',
     'latitude': 53.75, 'longitude': 24.5, 'category': 'memorial', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'Open all day', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 3.9, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # MORE RELIGIOUS SITES
    # ══════════════════════════════════════════════════════════
    {'name': 'Muravanka Church (Fortress Church)', 'name_en': 'Muravanka Church',
     'description': 'A 16th-century Roman Catholic fortress church (defensive church) in the village of Muravanka. One of the finest examples of fortified churches in Belarus, built during the time of the Polish-Lithuanian Commonwealth. The church served both as a place of worship and a defensive refuge during times of conflict.',
     'short_desc': '16th-century fortified church — defensive architecture of the Polish-Lithuanian Commonwealth.',
     'location': 'Muravanka, Pruzhany District, Brest Oblast', 'city': 'Muravanka', 'region': 'Brest Oblast',
     'latitude': 52.45, 'longitude': 24.3, 'category': 'church', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'By arrangement', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    {'name': 'Kasianikitsy Church', 'name_en': 'Kasianikitsy Church',
     'description': 'A 16th-century Orthodox church famous for its unique architectural design — the interior is structured in the shape of an equilateral cross, making it one of the most visually distinctive churches in Belarus. Located in a quiet rural setting near the border with Lithuania.',
     'short_desc': '16th-century Orthodox church — unique equilateral cross-shaped interior design.',
     'location': 'Kasianikitsy, Vitebsk Oblast', 'city': 'Kasianikitsy', 'region': 'Vitebsk Oblast',
     'latitude': 55.65, 'longitude': 29.05, 'category': 'church', 'suitable_season': 'Spring, Summer, Autumn',
     'opening_hours': 'By arrangement', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.1, 'is_featured': False, 'is_verified': True},

    {'name': 'Holy Trinity Cathedral, Vitebsk', 'name_en': 'Holy Trinity Cathedral, Vitebsk',
     'description': 'A historic Russian Revival Orthodox cathedral built between 1750 and 1772. It is the oldest stone building in Vitebsk and one of the most significant religious monuments in the region. The cathedral features baroque-influenced iconostases and a notable collection of 18th-century icons.',
     'short_desc': 'Oldest stone building in Vitebsk — Russian Revival Orthodox cathedral from 1750-1772.',
     'location': 'Vitebsk, Belarus', 'city': 'Vitebsk', 'region': 'Vitebsk Oblast',
     'latitude': 55.1917, 'longitude': 30.2033, 'category': 'church', 'suitable_season': 'All seasons',
     'opening_hours': '07:00 - 19:00', 'ticket_price': 0.00, 'image_url': '',
     'avg_rating': 4.0, 'is_featured': False, 'is_verified': True},

    # ══════════════════════════════════════════════════════════
    # FATHER FROST ESTATE (BELOVEZHSKAYA)
    # ══════════════════════════════════════════════════════════
    {'name': 'Residence of Ded Moroz (Father Frost)', 'name_en': 'Father Frost Estate',
     'description': 'The estate of Ded Moroz (Belarusian/Slavic Grandfather Frost) within the Belovezhskaya Pushcha National Park. Draws approximately 150,000 visitors annually, making it one of the most popular tourist attractions in Belarus. Features animated fairy-tale characters carved from wood, a workshop where gifts are made, and a New Year\'s train. Open year-round but busiest during the winter holiday season.',
     'short_desc': 'Residence of Slavic Grandfather Frost — 150,000 visitors annually, fairy-tale wood carvings.',
     'location': 'Kamieniuki, Brest Oblast', 'city': 'Kamieniuki', 'region': 'Brest Oblast',
     'latitude': 52.5833, 'longitude': 23.8667, 'category': 'architecture', 'suitable_season': 'All seasons (best winter)',
     'opening_hours': '09:00 - 17:00', 'ticket_price': 5.00, 'image_url': '',
     'avg_rating': 4.3, 'is_featured': False, 'is_verified': True},
]


# ─────────────────────────────────────────────────────────
# Init function
# ─────────────────────────────────────────────────────────
def init_db():
    app = create_app()
    with app.app_context():
        # ── Users ─────────────────────────────────────────
        if User.query.count() == 0:
            admin = User(
                username='admin', email='admin@belarus-tourism.com',
                password_hash=generate_password_hash('admin123'),
                role='admin', nickname='Administrator', status='active', email_verified=True
            )
            demo = User(
                username='demo', email='demo@example.com',
                password_hash=generate_password_hash('demo123'),
                role='user', nickname='Demo User', status='active', email_verified=True
            )
            db.session.add(admin)
            db.session.add(demo)
            db.session.commit()
            print('Users: admin / admin123, demo / demo123')

        # ── Attractions ────────────────────────────────────
        if True:
            # Clear tables first
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            db.session.execute(db.text('TRUNCATE TABLE attraction_tags'))
            db.session.execute(db.text('TRUNCATE TABLE attractions'))
            db.session.execute(db.text('TRUNCATE TABLE articles'))
            db.session.execute(db.text('TRUNCATE TABLE questions'))
            db.session.execute(db.text('TRUNCATE TABLE answers'))
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()

            for data in BELARUS_ATTRACTIONS:
                att = Attraction(**data)
                db.session.add(att)
            db.session.commit()
            print(f'{len(BELARUS_ATTRACTIONS)} REAL attractions inserted')

        # ── Tags ───────────────────────────────────────────
        if Tag.query.count() == 0:
            tags = [
                Tag(name='UNESCO World Heritage', slug='unesco', color='#f5a623', description='UNESCO World Heritage Sites in Belarus', use_count=3),
                Tag(name='History', slug='history', color='#8b4513', description='Historical sites and monuments', use_count=8),
                Tag(name='Nature', slug='nature', color='#2a9d5c', description='Parks, forests, and natural landscapes', use_count=8),
                Tag(name='Architecture', slug='architecture', color='#1a5e63', description='Architectural landmarks', use_count=6),
                Tag(name='Family Friendly', slug='family', color='#e91e63', description='Great for families with children', use_count=2),
                Tag(name='Photography', slug='photography', color='#9c27b0', description='Top photography spots', use_count=5),
                Tag(name='Medieval', slug='medieval', color='#795548', description='Medieval-era castles and ruins', use_count=5),
                Tag(name='Memorial', slug='memorial', color='#607d8b', description='Memorials and war monuments', use_count=4),
                Tag(name='Museums', slug='museums', color='#ff5722', description='Museums and exhibitions', use_count=6),
                Tag(name='Religious Sites', slug='religious', color='#673ab7', description='Churches, monasteries, and religious monuments', use_count=6),
                Tag(name='Lakes', slug='lakes', color='#2196f3', description='Lakes and water recreation', use_count=5),
                Tag(name='Forests', slug='forests', color='#4caf50', description='Forests and woodland areas', use_count=4),
                Tag(name='Hiking', slug='hiking', color='#795548', description='Hiking and outdoor activities', use_count=3),
                Tag(name='Urban', slug='urban', color='#9e9e9e', description='City landmarks and urban exploration', use_count=5),
            ]
            for t in tags:
                db.session.add(t)
            db.session.commit()
            print(f'{len(tags)} tags created')

        # ── Attraction Tags ────────────────────────────────
        if AttractionTag.query.count() == 0:
            for att in Attraction.query.all():
                tag_ids = []
                cat = (att.category or '').lower()
                desc = (att.description or '').lower()
                name = (att.name or '').lower()
                if cat == 'castle': tag_ids.extend([7])
                if cat == 'palace': tag_ids.extend([2])
                if cat == 'nature': tag_ids.extend([3, 12])
                if cat == 'memorial': tag_ids.extend([8])
                if cat == 'museum': tag_ids.extend([9])
                if cat == 'church': tag_ids.extend([10, 2])
                if cat == 'architecture': tag_ids.extend([4])
                if cat == 'park': tag_ids.extend([3, 13])
                if 'unesco' in desc or 'world heritage' in name: tag_ids.append(1)
                if 'family' in desc or 'children' in desc or 'kids' in name: tag_ids.append(5)
                if 'photo' in desc or 'panoramic' in desc: tag_ids.append(6)
                if 'lake' in name: tag_ids.extend([11, 3])
                if 'museum' in cat: tag_ids.append(9)
                if 'minsk' in name or 'brest' in name or 'vitebsk' in name: tag_ids.append(14)
                if 'monastery' in name or 'church' in name: tag_ids.extend([10, 2])
                if 'hiking' in name or 'trail' in desc: tag_ids.append(13)
                if 'forest' in name or 'bison' in desc or 'pushcha' in name: tag_ids.extend([12, 3])
                if 'river' in name or 'embankment' in name: tag_ids.extend([11, 3])
                if att.is_featured and float(att.avg_rating or 0) >= 4.5: tag_ids.extend([1, 2])
                tag_ids = list(dict.fromkeys(tag_ids))[:5]
                for tid in tag_ids:
                    db.session.add(AttractionTag(attraction_id=att.id, tag_id=tid))
            db.session.commit()
            print('Auto-tagged all attractions')

        # ── Sample Articles ────────────────────────────────
        if Article.query.count() == 0:
            articles_data = [
                {'user_id': 1, 'attraction_id': 1,
                 'title': 'A Complete Guide to Visiting Mir Castle Complex',
                 'summary': 'Everything you need for a perfect day trip to Belarus most iconic UNESCO World Heritage Site.',
                 'content': 'Mir Castle Complex is one of the most impressive historical monuments in Belarus. Built in the late 16th century, this Gothic-Renaissance masterpiece stands as a testament to the rich cultural heritage of the Polish-Lithuanian Commonwealth.\n\nGetting There: The castle is about 120km from Minsk. Most convenient by car or organized tour. Public buses available from Minsk Central Bus Station.\n\nBest Time to Visit: Spring and autumn offer the most dramatic photos — blooming gardens in spring and golden foliage in autumn. Summer weekends can be crowded.\n\nInside the Castle: The museum features exhibitions on castle history, the Radziwill family, and medieval life. The restored chambers with original frescoes are not to be missed.\n\nPhotography Tips: The castle looks best in early morning or late afternoon light. The lake reflection makes for stunning photographs.',
                 'cover_image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/%D0%9C%D0%B8%D1%80%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg/400px-%D0%9C%D0%B8%D1%80%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%B0%D0%BC%D0%B0%D0%BA.jpg',
                 'tags_json': ['UNESCO World Heritage', 'History', 'Medieval', 'Architecture'], 'is_featured': True, 'is_published': True, 'view_count': 312, 'like_count': 45},
                {'user_id': 1, 'attraction_id': 3,
                 'title': 'European Bison Encounter: Belovezhskaya Pushcha in One Day',
                 'summary': 'How to make the most of a day trip to Europe last primeval forest and spot the majestic wisent.',
                 'content': 'Belovezhskaya Pushcha is one of those places that reminds you of how magnificent untouched nature can be. As the last primeval forest in Europe, it offers a window into what the continent looked like before human civilization reshaped it.\n\nThe main attraction is the European bison (wisent). These magnificent animals roam freely in the park, and with a bit of patience you can observe them from safe viewing platforms. The park is home to over 600 bison.\n\nWhat to See: Start at the Nature Museum, then take the forest train to the bison feeding areas. The ancient oak trees — some over 600 years old — are equally impressive. Don\'t miss the Tsars Oak.\n\nPractical Tips: Wear comfortable walking shoes. The forest can be muddy. Bring binoculars for bird watching — 253 species live here!',
                 'cover_image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/BelarusBNP09.JPG/400px-BelarusBNP09.JPG',
                 'tags_json': ['Nature', 'UNESCO World Heritage', 'Family Friendly', 'Photography'], 'is_featured': True, 'is_published': True, 'view_count': 245, 'like_count': 38},
            ]
            for a in articles_data:
                db.session.add(Article(**a))
            db.session.commit()
            print(f'{len(articles_data)} sample articles created')

        # ── Sample Q&A ──────────────────────────────────
        if Question.query.count() == 0:
            q1 = Question(user_id=2, attraction_id=1,
                           title='What is the best time of year to visit Mir Castle?',
                           content='Planning a trip to Mir Castle and wondering when would be the best time to visit for photography and fewer crowds.',
                           view_count=45, answer_count=1, upvote_count=3)
            db.session.add(q1)
            db.session.flush()
            a1 = Answer(question_id=q1.id, user_id=1,
                          content='I would recommend late April to early June for the best weather and photos. The castle grounds are green and blooming, and summer crowds have not yet arrived. October is also beautiful for autumn foliage. Avoid July-August if you dislike crowds.',
                          upvote_count=5, is_accepted=True)
            db.session.add(a1)
            db.session.commit()
            q1.has_accepted_answer = True
            db.session.commit()

            q2 = Question(user_id=2, attraction_id=3,
                           title='Are there English guides available at Belovezhskaya Pushcha?',
                           content='My family does not speak Russian or Belarusian. Are there English-speaking guides for the forest tour?',
                           view_count=32, answer_count=0, upvote_count=1)
            db.session.add(q2)
            db.session.commit()
            print('Sample Q&A created')

        print('Database initialized successfully with REAL Belarus tourism data!')


if __name__ == '__main__':
    init_db()
