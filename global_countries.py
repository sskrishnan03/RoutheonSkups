"""Global travel data for 40 countries with administrative hierarchies, currencies, timezones, and metadata."""

COUNTRIES = {
    "Italy": {
        "code": "IT", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Rome",
        "tts_voice": "it-IT-ElsaNeural", "tts_fallback_lang": "it",
        "region_label": "Region", "regions": {
            "Tuscany": ["Florence", "Siena", "Pisa", "Lucca", "Arezzo", "Livorno", "Grosseto", "San Gimignano", "Cortona", "Montepulciano"],
            "Lombardy": ["Milan", "Bergamo", "Brescia", "Como", "Mantua", "Cremona", "Pavia"],
            "Lazio": ["Rome", "Fiumicino", "Tivoli", "Ostia", "Civitavecchia", "Viterbo"],
            "Veneto": ["Venice", "Verona", "Padua", "Vicenza", "Treviso", "Belluno", "Rovigo"],
            "Campania": ["Naples", "Amalfi", "Positano", "Sorrento", "Salerno", "Capri", "Ischia", "Caserta"],
            "Sicily": ["Palermo", "Catania", "Taormina", "Syracuse", "Trapani", "Agrigento"],
            "Sardinia": ["Cagliari", "Alghero", "Costa Smeralda", "Olbia", "Nuoro"],
            "Emilia-Romagna": ["Bologna", "Modena", "Parma", "Ravenna", "Ferrara", "Rimini", "Reggio Emilia"],
            "Piedmont": ["Turin", "Asti", "Alba", "Novara", "Cuneo"],
            "Liguria": ["Genoa", "Cinque Terre", "Portofino", "Sanremo", "La Spezia"],
            "Umbria": ["Perugia", "Assisi", "Spoleto", "Orvieto", "Gubbio"],
            "Abruzzo": ["L'Aquila", "Pescara", "Teramo", "Chieti"],
            "Marche": ["Ancona", "Urbino", "Pesaro", "Macerata"],
            "Trentino-Alto Adige": ["Trento", "Bolzano", "Merano"],
            "Friuli Venezia Giulia": ["Trieste", "Udine", "Gorizia", "Pordenone"],
            "Puglia": ["Bari", "Lecce", "Alberobello", "Ostuni", "Brindisi", "Taranto", "Polignano a Mare"],
            "Basilicata": ["Matera", "Potenza"],
            "Calabria": ["Reggio Calabria", "Tropea", "Cosenza", "Catanzaro"],
            "Molise": ["Campobasso", "Isernia"],
            "Valle d'Aosta": ["Aosta", "Courmayeur"],
        },
        "popular_destinations": ["Rome", "Venice", "Florence", "Milan", "Amalfi Coast", "Naples", "Cinque Terre", "Tuscany", "Lake Como", "Capri", "Taormina", "Positano", "Pisa", "Siena", "Bologna", "Verona", "Santorini", "Trieste", "Palermo", "Matera"],
    },
    "Japan": {
        "code": "JP", "continent": "Asia",
        "currency": "JPY", "currency_symbol": "\u00a5",
        "timezone": "Asia/Tokyo",
        "tts_voice": "ja-JP-NanamiNeural", "tts_fallback_lang": "ja",
        "region_label": "Prefecture", "regions": {
            "Tokyo": ["Shibuya", "Shinjuku", "Asakusa", "Harajuku", "Akihabara", "Ginza", "Roppongi", "Odaiba", "Ikebukuro", "Sumida"],
            "Kyoto": ["Higashiyama", "Arashiyama", "Fushimi", "Kinkaku-ji", "Gion", "Nishiki"],
            "Osaka": ["Dotonbori", "Shinsaibashi", "Osaka Castle", "Namba", "Umeda", "Shinsekai"],
            "Hokkaido": ["Sapporo", "Otaru", "Niseko", "Furano", "Hakodate", "Asahikawa", "Kushiro"],
            "Okinawa": ["Naha", "Nago", "Ishigaki", "Miyako", "Chatan"],
            "Hiroshima": ["Hiroshima City", "Miyajima Island", "Onomichi"],
            "Nara": ["Nara City", "Yoshino"],
            "Nagano": ["Nagano City", "Matsumoto", "Hakuba", "Zao"],
            "Kanagawa": ["Yokohama", "Kamakura", "Hakone", "Enoshima"],
            "Aichi": ["Nagoya", "Inuyama", "Takayama"],
            "Mie": ["Ise", "Toba", "Shima"],
            "Shizuoka": ["Mt. Fuji Area", "Atami", "Izu Peninsula"],
            "Fukuoka": ["Fukuoka City", "Dazaifu", "Itoshima"],
            "Nagasaki": ["Nagasaki City", "Gunkanjima"],
            "Miyagi": ["Sendai"],
            "Ibaraki": ["Mito"],
            "Tochigi": ["Nikko"],
            "Gunma": ["Kusatsu"],
            "Niigata": ["Niigata City", "Echigo-Yuzawa"],
            "Ishikawa": ["Kanazawa", "Noto Peninsula"],
            "Fukui": ["Fukui City", "Eiheiji"],
            "Yamanashi": ["Kofu", "Lake Kawaguchi"],
        },
        "popular_destinations": ["Tokyo", "Kyoto", "Osaka", "Hokkaido", "Okinawa", "Hiroshima", "Nara", "Nagano", "Kamakura", "Hakone", "Takayama", "Nikko", "Kanazawa", "Sendai", "Fukuoka", "Mount Fuji", "Nagasaki", "Ise", "Matsumoto", "Atami"],
    },
    "France": {
        "code": "FR", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Paris",
        "tts_voice": "fr-FR-DeniseNeural", "tts_fallback_lang": "fr",
        "region_label": "Region", "regions": {
            "Ile-de-France": ["Paris", "Versailles", "Disneyland Paris", "Fontainebleau", "Saint-Denis"],
            "Provence-Alpes-Cote d'Azur": ["Nice", "Marseille", "Cannes", "Antibes", "Aix-en-Provence", "Monaco", "Saint-Tropez", "Avignon", "Arles", "Gordes"],
            "Normandy": ["Mont Saint-Michel", "Honfleur", "Caen", "Rouen", "Deauville", "Etretat"],
            "Brittany": ["Saint-Malo", "Brest", "Rennes", "Quimper", "Concarneau"],
            "Burgundy": ["Dijon", "Beaune", "Lyon"],
            "Alsace": ["Strasbourg", "Colmar", "Riquewihr"],
            "Loire Valley": ["Amboise", "Chambord", "Tours", "Angers", "Blois"],
            "Occitanie": ["Carcassonne", "Toulouse", "Montpellier", "Nimes", "Albi"],
            "Nouvelle-Aquitaine": ["Bordeaux", "Biarritz", "La Rochelle", "Dordogne", "Arcachon"],
            "Auvergne-Rhone-Alpes": ["Lyon", "Annecy", "Chamonix", "Grenoble", "Clermont-Ferrand"],
            "Hauts-de-France": ["Lille", "Amiens", "Reims"],
            "Grand Est": ["Strasbourg", "Metz", "Nancy"],
            "Pays de la Loire": ["Nantes", "Angers", "Le Mans"],
            "Centre-Val de Loire": ["Orleans", "Chartres", "Le Mans"],
            "Corsica": ["Ajaccio", "Bastia", "Bonifacio", "Calvi"],
            "PACA": ["Toulon", "Gap", "Digne-les-Bains"],
        },
        "popular_destinations": ["Paris", "Nice", "Lyon", "Bordeaux", "Marseille", "Mont Saint-Michel", "Strasbourg", "Cannes", "Chamonix", "Versailles", "Honfleur", "Annecy", "Colmar", "Toulouse", "Dijon", "Biarriz", "Avignon", "Corsica", "Dordogne", "La Rochelle"],
    },
    "Spain": {
        "code": "ES", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Madrid",
        "tts_voice": "es-ES-ElviraNeural", "tts_fallback_lang": "es",
        "region_label": "Autonomous Community", "regions": {
            "Catalonia": ["Barcelona", "Girona", "Tarragona", "Sitges", "Costa Brava", "Montserrat", "Figueres"],
            "Andalusia": ["Seville", "Granada", "Malaga", "Cordoba", "Cadiz", "Ronda", "Nerja", "Marbella", "Jerez"],
            "Madrid": ["Madrid", "Toledo", "Segovia", "Avila", "El Escorial"],
            "Valencia": ["Valencia", "Alicante", "Benidorm", "Castellon", "Peñiscola"],
            "Basque Country": ["San Sebastian", "Bilbao", "Vitoria-Gasteiz"],
            "Galicia": ["Santiago de Compostela", "A Coruña", "Vigo", "Pontevedra"],
            "Balearic Islands": ["Palma de Mallorca", "Ibiza", "Menorca", "Formentera"],
            "Canary Islands": ["Tenerife", "Gran Canaria", "Lanzarote", "Fuerteventura", "La Palma"],
            "Castilla y Leon": ["Salamanca", "Burgos", "Leon", "Valladolid", "Segovia"],
            "Castilla-La Mancha": ["Toledo", "Cuenca", "Albacete"],
            "Aragon": ["Zaragoza", "Teruel", "Huesca"],
            "Extremadura": ["Caceres", "Badajoz", "Merida"],
            "Murcia": ["Cartagena", "Murcia City"],
            "Cantabria": ["Santander", "Santillana del Mar"],
            "Asturias": ["Oviedo", "Gijon", "Covadonga"],
            "La Rioja": ["Logrono", "Haro"],
            "Navarre": ["Pamplona", "San Sebastian de Garabandal"],
        },
        "popular_destinations": ["Barcelona", "Madrid", "Seville", "Granada", "Valencia", "San Sebastian", "Bilbao", "Ibiza", "Mallorca", "Tenerife", "Cordoba", "Toledo", "Malaga", "Ronda", "Santiago de Compostela", "Pamplona", "Cadiz", "Menorca", "Marbella", "Girona"],
    },
    "United States": {
        "code": "US", "continent": "North America",
        "currency": "USD", "currency_symbol": "$",
        "timezone": "America/New_York",
        "tts_voice": "en-US-JennyNeural", "tts_fallback_lang": "en",
        "region_label": "State", "regions": {
            "New York": ["New York City", "Buffalo", "Niagara Falls", "Hudson Valley", "The Hamptons", "Lake George"],
            "California": ["Los Angeles", "San Francisco", "San Diego", "Yosemite", "Napa Valley", "Lake Tahoe", "Santa Barbara", "Big Sur", "Malibu", "Joshua Tree"],
            "Florida": ["Miami", "Orlando", "Key West", "Tampa", "Fort Lauderdale", "Clearwater", "St. Augustine", "Everglades"],
            "Hawaii": ["Honolulu", "Maui", "Big Island", "Kauai", "Lanai", "Molokai"],
            "Nevada": ["Las Vegas", "Reno", "Lake Tahoe"],
            "Illinois": ["Chicago", "Springfield"],
            "Texas": ["Austin", "San Antonio", "Houston", "Dallas", "Big Bend", "Marfa"],
            "Massachusetts": ["Boston", "Cambridge", "Salem", "Cape Cod", "Martha's Vineyard"],
            "Arizona": ["Grand Canyon", "Sedona", "Phoenix", "Tucson", "Antelope Canyon", "Monument Valley"],
            "Colorado": ["Denver", "Aspen", "Vail", "Boulder", "Colorado Springs", "Telluride"],
            "Washington": ["Seattle", "Olympic National Park", "Mount Rainier", "San Juan Islands"],
            "Oregon": ["Portland", "Cannon Beach", "Crater Lake", "Bend", "Columbia River Gorge"],
            "Montana": ["Glacier National Park", "Bozeman", "Missoula", "Whitefish"],
            "Wyoming": ["Yellowstone", "Grand Teton", "Jackson Hole", "Cody"],
            "Utah": ["Salt Lake City", "Zion National Park", "Arches", "Bryce Canyon", "Moab", "Park City"],
            "South Carolina": ["Charleston", "Myrtle Beach", "Hilton Head", "Savannah"],
            "North Carolina": ["Asheville", "Outer Banks", "Charlotte", "Wilmington"],
            "Georgia": ["Savannah", "Atlanta", "St. Simons Island", "Blue Ridge"],
            "Tennessee": ["Nashville", "Memphis", "Gatlinburg", "Pigeon Forge", "Chattanooga"],
            "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Denali", "Kenai Fjords"],
            "Pennsylvania": ["Philadelphia", "Pittsburgh", "Gettysburg", "Poconos"],
            "Maine": ["Portland", "Acadia National Park", "Bar Harbor", "Kennebunkport"],
            "Virginia": ["Williamsburg", "Shenandoah", "Virginia Beach", "Alexandria"],
            "Michigan": ["Detroit", "Traverse City", "Mackinac Island", "Sleeping Bear Dunes"],
            "Ohio": ["Cleveland", "Columbus", "Cincinnati"],
            "Louisiana": ["New Orleans", "Baton Rouge", "Lafayette"],
            "Maryland": ["Baltimore", "Annapolis"],
            "Connecticut": ["Hartford", "Mystic", "Greenwich"],
            "New Jersey": ["Atlantic City", "Cape May", "Princeton"],
        },
        "popular_destinations": ["New York City", "Los Angeles", "San Francisco", "Las Vegas", "Miami", "Hawaii", "Grand Canyon", "Chicago", "Orlando", "Seattle", "Nashville", "Yosemite", "New Orleans", "Boston", "Portland", "Sedona", "Yellowstone", "Denver", "Austin", "Aspen"],
    },
    "New Zealand": {
        "code": "NZ", "continent": "Oceania",
        "currency": "NZD", "currency_symbol": "NZ$",
        "timezone": "Pacific/Auckland",
        "tts_voice": "en-NZ-MollyNeural", "tts_fallback_lang": "en",
        "region_label": "Region", "regions": {
            "Auckland Region": ["Auckland", "Waiheke Island", "Piha", "Rangitoto"],
            "Wellington Region": ["Wellington", "Martinborough", "Wairarapa"],
            "Canterbury": ["Christchurch", "Akaroa", "Kaikoura", "Mt Hutt"],
            "Otago": ["Queenstown", "Wanaka", "Dunedin", "Milford Sound", "Central Otago", "Arrowtown"],
            "Bay of Plenty": ["Tauranga", "Mount Maunganui", "Rotorua"],
            "Waikato": ["Hamilton", "Hobbiton", "Waitomo Caves", "Coromandel"],
            "Nelson/Tasman": ["Nelson", "Abel Tasman", "Golden Bay", "Motueka"],
            "West Coast": ["Franz Josef", "Fox Glacier", "Punakaiki", "Hokitika"],
            "Hawke's Bay": ["Napier", "Hastings"],
            "Northland": ["Bay of Islands", "Whangarei", "Cape Reinga", "Russell"],
            "Gisborne": ["Gisborne", "East Cape"],
            "Taranaki": ["New Plymouth", "Mount Taranaki"],
            "Manawatu-Whanganui": ["Palmerston North", "Whanganui"],
            "Marlborough": ["Blenheim", "Picton", "Marlborough Sounds"],
            "Southland": ["Invercargill", "Stewart Island", "The Catlins"],
            "Chatham Islands": ["Chatham Islands"],
        },
        "popular_destinations": ["Queenstown", "Milford Sound", "Auckland", "Rotorua", "Hobbiton", "Wellington", "Christchurch", "Wanaka", "Franz Josef", "Bay of Islands", "Abel Tasman", "Dunedin", "Mount Maunganui", "Napier", "Coromandel", "Waitomo Caves", "Kaikoura", "Punakaiki", "Arrowtown", "Picton"],
    },
    "Greece": {
        "code": "GR", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Athens",
        "tts_voice": "el-GR-AthinaNeural", "tts_fallback_lang": "el",
        "region_label": "Region", "regions": {
            "Attica": ["Athens", "Piraeus", "Cape Sounion", "Hydra"],
            "South Aegean": ["Santorini", "Mykonos", "Rhodes", "Naxos", "Paros", "Milos", "Corfu", "Kos"],
            "Crete": ["Heraklion", "Chania", "Elafonisi", "Rethymno", "Agios Nikolaos", "Lassithi"],
            "Ionian Islands": ["Corfu", "Zakynthos", "Kefalonia", "Lefkada", "Paxos"],
            "Central Macedonia": ["Thessaloniki", "Halkidiki", "Vergina"],
            "Peloponnese": ["Nafplio", "Monemvasia", "Olympia", "Sparta", "Gytheio", "Elonida"],
            "Thessaly": ["Meteora", "Volos", "Skiathos", "Skopelos", "Alonissos"],
            "Epirus": ["Ioannina", "Zagori", "Parga"],
            "Western Greece": ["Patras", "Nafpaktos"],
            "Eastern Macedonia and Thrace": ["Kavala", "Alexandroupolis"],
            "Central Greece": ["Delphi", "Karpenisi"],
            "North Aegean": ["Lesbos", "Chios", "Samos"],
            "Mount Athos": ["Mount Athos"],
            "Dodecanese": ["Rhodes", "Kos", "Lindos", "Karpathos"],
        },
        "popular_destinations": ["Santorini", "Mykonos", "Athens", "Crete", "Rhodes", "Corfu", "Meteora", "Zakynthos", "Paros", "Naxos", "Milos", "Thessaloniki", "Nafplio", "Halkidiki", "Kefalonia", "Skiathos", "Elafonisi", "Delphi", "Lefkada", "Parga"],
    },
    "Switzerland": {
        "code": "CH", "continent": "Europe",
        "currency": "CHF", "currency_symbol": "CHF",
        "timezone": "Europe/Zurich",
        "tts_voice": "de-CH-ConradNeural", "tts_fallback_lang": "de",
        "region_label": "Canton", "regions": {
            "Bern": ["Interlaken", "Jungfraujoch", "Grindelwald", "Thun", "Bern"],
            "Zurich": ["Zurich", "Rapperswil", "Uetliberg"],
            "Valais": ["Zermatt", "Verbier", "Sion", "Leukerbad", "Crans-Montana"],
            "Lucerne": ["Lucerne", "Mount Pilatus", "Engelberg"],
            "Graubunden": ["St. Moritz", "Davos", "Arosa", "Chur", "Fluela Pass"],
            "Vaud": ["Montreux", "Lausanne", "Vevey", "Lavaux"],
            "Geneva": ["Geneva"],
            "Ticino": ["Lugano", "Locarno", "Bellinzona", "Ascona"],
            "Basel-Landschaft": ["Basel"],
            "Schwyz": ["Schwyz", "Einsiedeln"],
            "Obwalden": ["Brunnen"],
            "Nidwalden": ["Stans"],
            "Appenzell Ausserrhoden": ["Appenzell"],
            "Glarus": ["Glarus"],
            "Fribourg": ["Fribourg", "Gruyeres"],
            "Solothurn": ["Solothurn"],
            "Neuchatel": ["Neuchatel"],
            "Jura": ["Porrentruy"],
            "Schaffhausen": ["Schaffhausen", "Rhine Falls"],
        },
        "popular_destinations": ["Interlaken", "Zermatt", "Lucerne", "Jungfraujoch", "Grindelwald", "Zurich", "Geneva", "Montreux", "St. Moritz", "Verbier", "Bern", "Lake Geneva", "Lauterbrunnen", "Davos", "Lausanne", "Lugano", "Basel", "Engelberg", "Thun", "Leukerbad"],
    },
    "Australia": {
        "code": "AU", "continent": "Oceania",
        "currency": "AUD", "currency_symbol": "A$",
        "timezone": "Australia/Sydney",
        "tts_voice": "en-AU-NatashaNeural", "tts_fallback_lang": "en",
        "region_label": "State", "regions": {
            "New South Wales": ["Sydney", "Blue Mountains", "Byron Bay", "Hunter Valley", "Port Stephens"],
            "Victoria": ["Melbourne", "Great Ocean Road", "Phillip Island", "Yarra Valley", "Ballarat"],
            "Queensland": ["Gold Coast", "Cairns", "Great Barrier Reef", "Brisbane", "Whitsundays", "Port Douglas", "Fraser Island"],
            "Western Australia": ["Perth", "Broome", "Margaret River", "Ningaloo Reef", "Karijini"],
            "South Australia": ["Adelaide", "Kangaroo Island", "Barossa Valley", "Flinders Ranges"],
            "Tasmania": ["Hobart", "Launceston", "Cradle Mountain", "Freycinet", "MONA"],
            "Northern Territory": ["Darwin", "Uluru", "Kakadu", "Alice Springs", "Litchfield"],
            "ACT": ["Canberra"],
        },
        "popular_destinations": ["Sydney", "Melbourne", "Great Barrier Reef", "Uluru", "Gold Coast", "Cairns", "Blue Mountains", "Great Ocean Road", "Perth", "Hobart", "Broome", "Brisbane", "Kangaroo Island", "Whitsundays", "Byron Bay", "Fraser Island", "Kakadu", "Adelaide", "Margaret River", "Tasmania"],
    },
    "Thailand": {
        "code": "TH", "continent": "Asia",
        "currency": "THB", "currency_symbol": "\u0e3f",
        "timezone": "Asia/Bangkok",
        "tts_voice": "th-TH-PremwadeeNeural", "tts_fallback_lang": "th",
        "region_label": "Region", "regions": {
            "Bangkok": ["Bangkok", "Ayutthaya", "Damnoen Saduak", "Kanchanaburi"],
            "Chiang Mai": ["Chiang Mai", "Chiang Rai", "Pai", "Mae Hong Son"],
            "Phuket": ["Phuket", "Patong", "Kata", "Phi Phi Islands", "Phang Nga"],
            "Krabi": ["Krabi", "Ao Nang", "Railay Beach", "Koh Lanta"],
            "Surat Thani": ["Koh Samui", "Koh Phangan", "Koh Tao"],
            "Pattaya": ["Pattaya", "Bang Saen", "Rayong"],
            "Hua Hin": ["Hua Hin", "Prachuap Khiri Khan"],
            "Koh Chang": ["Koh Chang", "Trat"],
            "Isan": ["Khon Kaen", "Nakhon Ratchasima", "Udon Thani", "Phimai"],
            "Tak": ["Sangkhla Buri"],
            "Kanchanaburi": ["Kanchanaburi", "Erawan National Park", "Sai Yok"],
            "Trang": ["Trang", "Koh Lipe", "Koh Mook"],
            "Lampang": ["Lampang"],
            "Nakhon Pathom": ["Nakhon Pathom"],
            "Prachuap Khiri Khan": ["Hua Hin"],
        },
        "popular_destinations": ["Bangkok", "Chiang Mai", "Phuket", "Krabi", "Koh Samui", "Pattaya", "Phi Phi Islands", "Koh Lanta", "Ayutthaya", "Pai", "Koh Phangan", "Chiang Rai", "Hua Hin", "Railay Beach", "Kanchanaburi", "Koh Tao", "Koh Chang", "Phang Nga", "Sukhothai", "Lampang"],
    },
    "United Kingdom": {
        "code": "GB", "continent": "Europe",
        "currency": "GBP", "currency_symbol": "\u00a3",
        "timezone": "Europe/London",
        "tts_voice": "en-GB-SoniaNeural", "tts_fallback_lang": "en",
        "region_label": "Country/County", "regions": {
            "England": ["London", "Oxford", "Cambridge", "Bath", "York", "Cornwall", "Lake District", "Brighton", "Manchester", "Liverpool", "Bristol", "Salisbury", "Canterbury", "Stonehenge", "Windsor"],
            "Scotland": ["Edinburgh", "Glasgow", "Inverness", "Isle of Skye", "Highlands", "Loch Lomond", "St Andrews", "Orkney Islands", "Aberdeen"],
            "Wales": ["Cardiff", "Snowdonia", "Brecon Beacons", "Pembrokeshire", "Conwy", "Swansea"],
            "Northern Ireland": ["Belfast", "Giant's Causeway", "Derry", "Causeway Coast"],
        },
        "popular_destinations": ["London", "Edinburgh", "Bath", "York", "Lake District", "Oxford", "Cambridge", "Cornwall", "Brighton", "Isle of Skye", "Manchester", "Liverpool", "Bristol", "Snowdonia", "Belfast", "Glasgow", "Giant's Causeway", "Stonehenge", "Windsor", "Wales"],
    },
    "Canada": {
        "code": "CA", "continent": "North America",
        "currency": "CAD", "currency_symbol": "CA$",
        "timezone": "America/Toronto",
        "tts_voice": "en-CA-ClaireNeural", "tts_fallback_lang": "en",
        "region_label": "Province", "regions": {
            "Ontario": ["Toronto", "Niagara Falls", "Ottawa", "Algonquin Park", "Prince Edward County"],
            "British Columbia": ["Vancouver", "Victoria", "Whistler", "Banff", "Okanagan", "Tofino", "Jasper"],
            "Alberta": ["Calgary", "Banff National Park", "Jasper National Park", "Lake Louise", "Edmonton"],
            "Quebec": ["Montreal", "Quebec City", "Mont-Tremblant", "Gaspe Peninsula"],
            "Nova Scotia": ["Halifax", "Lunenburg", "Cape Breton", "Peggy's Cove"],
            "New Brunswick": ["Bay of Fundy", "Fredericton", "St Andrews"],
            "Manitoba": ["Winnipeg", "Churchill"],
            "Saskatchewan": ["Saskatoon", "Prince Albert"],
            "Newfoundland and Labrador": ["St. John's", "Gros Morne", "Iceberg Alley"],
            "Prince Edward Island": ["Charlottetown", "Cavendish"],
            "Yukon": ["Whitehorse", "Dawson City", "Kluane"],
            "Northwest Territories": ["Yellowknife"],
            "Nunavut": ["Iqaluit"],
        },
        "popular_destinations": ["Banff", "Vancouver", "Toronto", "Niagara Falls", "Jasper", "Whistler", "Montreal", "Quebec City", "Ottawa", "Lake Louise", "Victoria", "Tofino", "Halifax", "Prince Edward Island", "Okanagan", "Cape Breton", "Whitehorse", "Churchill", "Mont-Tremblant", "Gros Morne"],
    },
    "Maldives": {
        "code": "MV", "continent": "Asia",
        "currency": "MVR", "currency_symbol": "Rf",
        "timezone": "Indian/Maldives",
        "tts_voice": "en-US-JennyNeural", "tts_fallback_lang": "en",
        "region_label": "Atoll", "regions": {
            "North Male Atoll": ["Malé", "Hulhumalé", "Baa Atoll", "Vaadhoo"],
            "South Male Atoll": ["Embudhdhoo", "Dhigufahuraa"],
            "Ari Atoll": ["South Ari Atoll", "North Ari Atoll", "Rasdhoo"],
            "Baa Atoll": ["Hanifaru Bay", "Dharavandhoo", "Eydhafushi"],
            "Lhaviyani Atoll": ["Komandoo", "Kuredu"],
            "Noonu Atoll": ["Kurumba", "Velaa"],
            "Raa Atoll": ["Ifuru", "Meedhoo"],
            "Shaviyani Atoll": ["Foakaidhoo"],
            "Thaa Atoll": ["Thaa Atoll"],
            "Laamu Atoll": ["Laamu Atoll"],
            "Gaafu Alif Atoll": ["Kooddoo"],
            "Gaafu Dhaalu Atoll": ["Fuvahmulah"],
            "Seenu Atoll": ["Addu City"],
            "Addu Atoll": ["Addu City"],
        },
        "popular_destinations": ["Malé", "Baa Atoll", "Ari Atoll", "South Male Atoll", "Vaadhoo", "Hanifaru Bay", "Rasdhoo", "North Male Atoll", "Kuredu", "Komandoo", "Addu Atoll", "Laamu Atoll", "Fuvahmulah"],
    },
    "Portugal": {
        "code": "PT", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Lisbon",
        "tts_voice": "pt-PT-FernandaNeural", "tts_fallback_lang": "pt",
        "region_label": "Region", "regions": {
            "Lisbon": ["Lisbon", "Sintra", "Cascais", "Belem", "Arrabida"],
            "Porto": ["Porto", "Braga", "Guimaraes", "Vila Nova de Gaia"],
            "Algarve": ["Lagos", "Faro", "Tavira", "Albufeira", "Portimao", "Sagres", "Carvoeiro", "Monchique"],
            "Azores": ["Ponta Delgada", "Sete Cidades", "Faial", "Sao Miguel", "Flores"],
            "Madeira": ["Funchal", "Madeira", "Porto Santo"],
            "Alentejo": ["Evora", "Monsaraz", "Comporta", "Vila Nova de Milfontes"],
            "Centro": ["Coimbra", "Tomar", "Batalha", "Obidos", "Aveiro"],
            "Minho": ["Viana do Castelo", "Peneda-Geres"],
            "Douro Valley": ["Pinhao", "Lamego"],
            "Leiria": ["Nazaré", "Fatima", "Peniche"],
        },
        "popular_destinations": ["Lisbon", "Porto", "Sintra", "Algarve", "Lagos", "Madeira", "Azores", "Evora", "Braga", "Cascais", "Coimbra", "Fatima", "Nazare", "Tavira", "Obidos", "Douro Valley", "Faro", "Comporta", "Sagres", "Monsaraz"],
    },
    "Iceland": {
        "code": "IS", "continent": "Europe",
        "currency": "ISK", "currency_symbol": "kr",
        "timezone": "Atlantic/Reykjavik",
        "tts_voice": "en-US-JennyNeural", "tts_fallback_lang": "en",
        "region_label": "Region", "regions": {
            "Capital Region": ["Reykjavik", "Keflavik", "Blue Lagoon", "Hafnarfjordur"],
            "South Iceland": ["Vik", "Seljalandsfoss", "Skogafoss", "Reynisfjara", "Landmannalaugar", "Thorsmork"],
            "North Iceland": ["Akureyri", "Husavik", "Lake Myvatn", "Godafoss", "Dalvik"],
            "East Iceland": ["Egilsstadir", "Seydisfjordur", "Hengifoss"],
            "West Iceland": ["Borgarnes", "Snæfellsnes", "Kirkjufell", "Budir"],
            "Westfjords": ["Isafjordur", "Dynjandi", "Latrabjarg"],
            "Southwest Iceland": ["Golden Circle", "Thingvellir", "Geysir", "Gullfoss"],
        },
        "popular_destinations": ["Reykjavik", "Golden Circle", "Blue Lagoon", "Akureyri", "Jokulsarlon", "Seljalandsfoss", "Landmannalaugar", "Vik", "Snaefellsnes", "Myvatn", "Husavik", "Westfjords", "Skogafoss", "Diamond Beach", "Kirkjufell", "Dettifoss", "Eastfjords", "Godafoss", "Reynisfjara", "Thorsmork"],
    },
    "Brazil": {
        "code": "BR", "continent": "South America",
        "currency": "BRL", "currency_symbol": "R$",
        "timezone": "America/Sao_Paulo",
        "tts_voice": "pt-BR-FranciscaNeural", "tts_fallback_lang": "pt",
        "region_label": "State", "regions": {
            "Rio de Janeiro": ["Rio de Janeiro", "Cristo Redentor", "Copacabana", "Ipanema", "Niteroi", "Buzios"],
            "Sao Paulo": ["Sao Paulo City", "Campos do Jordao", "Santos"],
            "Bahia": ["Salvador", "Morro de Sao Paulo", "Itacare", "Chapada Diamantina"],
            "Amazonas": ["Manaus", "Meeting of Waters", "Amazon Rainforest"],
            "Minas Gerais": ["Belo Horizonte", "Ouro Preto", "Tiradentes", "Divinopolis"],
            "Ceara": ["Fortaleza", "Jericoacoara", "Canoa Quebrada"],
            "Para": ["Belem", "Marajo Island"],
            "Espirito Santo": ["Vitoria", "Vila Velha"],
            "Parana": ["Curitiba", "Foz do Iguacu", "Paranagua"],
            "Santa Catarina": ["Florianopolis", "Balneario Camboriu", "Blumenau"],
            "Rio Grande do Sul": ["Porto Alegre", "Gramado", "Canela", "Bento Goncalves"],
            "Goias": ["Goiania", "Caldas Novas"],
            "Pernambuco": ["Recife", "Fernando de Noronha", "Porto de Galinhas"],
            "Mato Grosso": ["Cuiaba", "Pantanal", "Chapada dos Guimaraes"],
        },
        "popular_destinations": ["Rio de Janeiro", "Salvador", "Sao Paulo", "Fortaleza", "Manaus", "Iguazu Falls", "Florianopolis", "Gramado", "Buzios", "Ouro Preto", "Pantanal", "Fernando de Noronha", "Amazon Rainforest", "Jericoacoara", "Paraty", "Chapada Diamantina", "Natal", "Recife", "Tiradentes", "Marajo Island"],
    },
    "Costa Rica": {
        "code": "CR", "continent": "North America",
        "currency": "CRC", "currency_symbol": "\u20a1",
        "timezone": "America/Costa_Rica",
        "tts_voice": "es-CR-JuanNeural", "tts_fallback_lang": "es",
        "region_label": "Province", "regions": {
            "Guanacaste": ["Tamarindo", "Playa Conchal", "Liberia", "Nosara", "Playa Flamingo"],
            "Puntarenas": ["Monteverde", "Manuel Antonio", "Jacó", "Corcovado", "Quepos"],
            "San José": ["San José", "Poas Volcano", "Irazu", "Cartago"],
            "Alajuela": ["La Fortuna", "Arenal", "Sarchi", "San Carlos"],
            "Limón": ["Puerto Viejo", "Cahuita", "Tortuguero"],
            "Heredia": ["Sarapiqui", "Braulio Carrillo"],
            "Cartago": ["Turrialba"],
        },
        "popular_destinations": ["San José", "Manuel Antonio", "Monteverde", "La Fortuna", "Tamarindo", "Puerto Viejo", "Arenal Volcano", "Tortuguero", "Jacó", "Nosara", "Corcovado", "Liberia", "Cahuita", "Montezuma", "Playa Conchal", "Turrialba", "Osa Peninsula", "Sarchi", "Poas", "Irazu"],
    },
    "Mexico": {
        "code": "MX", "continent": "North America",
        "currency": "MXN", "currency_symbol": "MX$",
        "timezone": "America/Mexico_City",
        "tts_voice": "es-MX-DaliaNeural", "tts_fallback_lang": "es",
        "region_label": "State", "regions": {
            "Mexico City": ["Mexico City", "Xochimilco", "Coyoacan", "Polanco"],
            "Quintana Roo": ["Cancun", "Tulum", "Playa del Carmen", "Cozumel", "Bacalar", "Isla Holbox"],
            "Jalisco": ["Puerto Vallarta", "Guadalajara", "Sayulita", "Tequila"],
            "Oaxaca": ["Oaxaca City", "Monte Alban", "Hierve el Agua", "Huatulco"],
            "Baja California Sur": ["Los Cabos", "Cabo San Lucas", "Todos Santos", "La Paz"],
            "Yucatan": ["Merida", "Chichen Itza", "Valladolid", "Uxmal"],
            "Guerrero": ["Acapulco", "Zihuatanejo", "Taxco"],
            "Nayarit": ["Riviera Nayarit", "San Pancho", "Mexcaltitan"],
            "Michoacan": ["Morelia", "Patzcuaro", "Monarch Butterfly Reserve"],
            "Colima": ["Manzanillo"],
            "Chiapas": ["San Cristobal de las Casas", "Palenque", "Tuxtla Gutierrez"],
            "Baja California": ["Ensenada", "Valle de Guadalupe"],
            "Sonora": ["Hermosillo", "Guaymas"],
            "Sinaloa": ["Mazatlan"],
            "Tabasco": ["Villahermosa"],
        },
        "popular_destinations": ["Cancun", "Mexico City", "Tulum", "Playa del Carmen", "Puerto Vallarta", "Oaxaca", "Los Cabos", "Merida", "Chichen Itza", "Acapulco", "Cozumel", "Sayulita", "Taxco", "San Cristobal", "Palenque", "Valle de Guadalupe", "Isla Holbox", "Bacalar", "Mazatlan", "Morelia"],
    },
    "Vietnam": {
        "code": "VN", "continent": "Asia",
        "currency": "VND", "currency_symbol": "\u20ab",
        "timezone": "Asia/Ho_Chi_Minh",
        "tts_voice": "vi-VN-HoaiMyNeural", "tts_fallback_lang": "vi",
        "region_label": "Region", "regions": {
            "South": ["Ho Chi Minh City", "Phu Quoc", "Mui Ne", "Dalat", "Vung Tau", "Con Dao"],
            "Central": ["Da Nang", "Hoi An", "Hue", "Nha Trang", "Quy Nhon", "Phong Nha"],
            "North": ["Hanoi", "Ha Long Bay", "Sapa", "Ninh Binh", "Cat Ba", "Ha Giang"],
            "Mekong Delta": ["Can Tho", "Ben Tre", "Chau Doc"],
            "Central Highlands": ["Buon Ma Thuot", "Kontum"],
        },
        "popular_destinations": ["Hanoi", "Ha Long Bay", "Ho Chi Minh City", "Da Nang", "Hoi An", "Phu Quoc", "Hue", "Sapa", "Nha Trang", "Dalat", "Ninh Binh", "Ha Giang", "Mui Ne", "Phong Nha", "Cat Ba", "Con Dao", "Hue", "Quy Nhon", "Can Tho", "Ben Tre"],
    },
    "Austria": {
        "code": "AT", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Vienna",
        "tts_voice": "de-AT-JonasNeural", "tts_fallback_lang": "de",
        "region_label": "State", "regions": {
            "Vienna": ["Vienna"],
            "Salzburg": ["Salzburg", "Zell am See", "Saalfelden", "Werfen"],
            "Tyrol": ["Innsbruck", "St Anton", "Kitzbuhel", "Hallstatt", "Achensee"],
            "Upper Austria": ["Linz", "Hallstatt", "Wachau Valley"],
            "Carinthia": ["Klagenfurt", "Villach", "Millstatter See", "Faaker See"],
            "Styria": ["Graz", "Schladming", "Admont"],
            "Lower Austria": ["Wachau", "Melk"],
            "Vorarlberg": ["Bregenz", "Lech", "Vorarlberg"],
        },
        "popular_destinations": ["Vienna", "Salzburg", "Hallstatt", "Innsbruck", "Graz", "Kitzbuhel", "St Anton", "Wachau Valley", "Melk", "Linz", "Zell am See", "Werfen", "Lech", "Bregenz", "Admont", "Schladming", "Achensee", "Villach", "Faaker See", "Saalfelden"],
    },
    "Egypt": {
        "code": "EG", "continent": "Africa",
        "currency": "EGP", "currency_symbol": "E£",
        "timezone": "Africa/Cairo",
        "tts_voice": "ar-EG-SalmaNeural", "tts_fallback_lang": "ar",
        "region_label": "Governorate", "regions": {
            "Cairo": ["Cairo", "Giza", "Pyramids of Giza", "Khan El Khalili"],
            "Luxor": ["Luxor", "Valley of the Kings", "Karnak Temple"],
            "Aswan": ["Aswan", "Philae Temple", "Abu Simbel"],
            "Red Sea": ["Hurghada", "Marsa Alam", "El Gouna", "Sharm El Sheikh", "Dahab"],
            "Alexandria": ["Alexandria"],
            "Sinai": ["Sharm El Sheikh", "Dahab", "Nuweiba"],
            "Fayoum": ["Fayoum", "Wadi El Rayan"],
            "Matrouh": ["Matrouh"],
        },
        "popular_destinations": ["Cairo", "Luxor", "Aswan", "Giza Pyramids", "Hurghada", "Sharm El Sheikh", "Alexandria", "Abu Simbel", "Dahab", "Nile Cruise", "Karnak Temple", "Valley of the Kings", "Philae Temple", "Khan El Khalili", "El Gouna", "Fayoum", "Marsa Alam", "Mount Sinai", "Siwa Oasis", "White Desert"],
    },
    "South Africa": {
        "code": "ZA", "continent": "Africa",
        "currency": "ZAR", "currency_symbol": "R",
        "timezone": "Africa/Johannesburg",
        "tts_voice": "en-ZA-LeahNeural", "tts_fallback_lang": "en",
        "region_label": "Province", "regions": {
            "Western Cape": ["Cape Town", "Stellenbosch", "Franschhoek", "Garden Route", "Hermanus", "Cape Winelands"],
            "Gauteng": ["Johannesburg", "Pretoria", "Soweto"],
            "KwaZulu-Natal": ["Durban", "Drakensberg", "Hluhluwe", "St Lucia"],
            "Eastern Cape": ["Port Elizabeth", "Addo Elephant Park", "Hogsback"],
            "Limpopo": ["Kruger National Park (South)"],
            "Mpumalanga": ["Kruger National Park", "Panorama Route", "Blyde River Canyon"],
            "North West": ["Sun City", "Pilanesberg"],
            "Free State": ["Golden Gate", "Clarens"],
            "Northern Cape": ["Kalahari", "Kimberley", "Namaqualand"],
        },
        "popular_destinations": ["Cape Town", "Kruger National Park", "Johannesburg", "Garden Route", "Stellenbosch", "Durban", "Franschhoek", "Hermanus", "Drakensberg", "St Lucia", "Pretoria", "Addo Elephant Park", "Sun City", "Panorama Route", "Blyde River Canyon", "Pilanesberg", "Hogsback", "Clarens", "Kalahari", "Cape Winelands"],
    },
    "Norway": {
        "code": "NO", "continent": "Europe",
        "currency": "NOK", "currency_symbol": "kr",
        "timezone": "Europe/Oslo",
        "tts_voice": "nb-NO-PernilleNeural", "tts_fallback_lang": "nb",
        "region_label": "Region", "regions": {
            "Oslo": ["Oslo", "Vigeland Park", "Bygdoy Peninsula"],
            "Bergen": ["Bergen", "Fløyen", "Bryggen"],
            "Troms": ["Tromsø", "Northern Lights", "Arctic Cathedral"],
            "Nordland": ["Lofoten Islands", "Bodø", "Helgeland"],
            "Rogaland": ["Stavanger", "Preikestolen", "Kjerag"],
            "Vestland": ["Sognefjord", "Geirangerfjord", "Flåm"],
            "More og Romsdal": ["Geiranger", "Trollstigen", "Ålesund"],
            "Trøndelag": ["Trondheim"],
            "Finnmark": ["North Cape", "Alta", "Hammerfest"],
            "Oppland": ["Jotunheimen", "Lillehammer"],
            "Hedmark": ["Hamar", "Røros"],
            "Buskerud": ["Drammen"],
            "Vestfold": ["Tønsberg", "Sandefjord"],
            "Telemark": ["Rjukan", "Notodden"],
        },
        "popular_destinations": ["Tromsø", "Lofoten Islands", "Bergen", "Oslo", "Geirangerfjord", "Preikestolen", "Stavanger", "Sognefjord", "Flåm", "North Cape", "Trollstigen", "Northern Lights", "Ålesund", "Jotunheimen", "Røros", "Bodø", "Trondheim", "Kjerag", "Alta", "Helgeland"],
    },
    "Turkey": {
        "code": "TR", "continent": "Europe/Asia",
        "currency": "TRY", "currency_symbol": "\u20ba",
        "timezone": "Europe/Istanbul",
        "tts_voice": "tr-TR-EmelNeural", "tts_fallback_lang": "tr",
        "region_label": "Region", "regions": {
            "Istanbul": ["Istanbul", "Sultanahmet", "Beyoglu", "Kadikoy", "Bosphorus"],
            "Cappadocia": ["Goreme", "Urgup", "Avanos", "Kaymakli"],
            "Antalya": ["Antalya", "Kas", "Kalkan", "Olympos", "Patara", "Side", "Belek"],
            "Aegean": ["Izmir", "Bodrum", "Alacati", "Ephesus", "Pamukkale"],
            "Mediterranean": ["Fethiye", "Oludeniz", "Dalyan", "Marmaris", "Anamur"],
            "Black Sea": ["Trabzon", "Uzungol", "Rize"],
            "Ankara": ["Ankara"],
            "Southeastern Anatolia": ["Gaziantep", "Sanliurfa", "Mardin"],
            "Central Anatolia": ["Konya", "Cappadocia"],
            "Marmara": ["Bursa", "Canakkale", "Troya"],
            "Eastern Anatolia": ["Mount Ararat", "Van"],
        },
        "popular_destinations": ["Istanbul", "Cappadocia", "Antalya", "Bodrum", "Pamukkale", "Ephesus", "Fethiye", "Alacati", "Goreme", "Kas", "Oludeniz", "Trabzon", "Konya", "Troya", "Bursa", "Mardin", "Ankara", "Dalyan", "Belek", "Uzungol"],
    },
    "Peru": {
        "code": "PE", "continent": "South America",
        "currency": "PEN", "currency_symbol": "S/",
        "timezone": "America/Lima",
        "tts_voice": "es-PE-AlexNeural", "tts_fallback_lang": "es",
        "region_label": "Region", "regions": {
            "Cusco": ["Cusco", "Machu Picchu", "Sacred Valley", "Ollantaytambo", "Rainbow Mountain"],
            "Lima": ["Lima", "Miraflores", "Barranco"],
            "Arequipa": ["Arequipa", "Colca Canyon"],
            "Puno": ["Puno", "Lake Titicaca"],
            "Ica": ["Huacachina", "Paracas", "Ballestas Islands"],
            "Amazonas": ["Chachapoyas", "Gocta Waterfall"],
            "Moquegua": ["Colca"],
            "Tacna": ["Tacna"],
            "La Libertad": ["Chan Chan", "Huanchaco"],
            "Piura": ["Mancora"],
            "Madre de Dios": ["Tambopata", "Puerto Maldonado"],
            "Junin": ["Cerro Pasco"],
        },
        "popular_destinations": ["Machu Picchu", "Cusco", "Sacred Valley", "Lima", "Rainbow Mountain", "Lake Titicaca", "Arequipa", "Colca Canyon", "Huacachina", "Paracas", "Nazca Lines", "Chachapoyas", "Chan Chan", "Manu National Park", "Tambopata", "Mancora", "Ballestas Islands", "Gocta Waterfall", "Ollantaytambo", "Trujillo"],
    },
    "Indonesia": {
        "code": "ID", "continent": "Asia",
        "currency": "IDR", "currency_symbol": "Rp",
        "timezone": "Asia/Jakarta",
        "tts_voice": "id-ID-GadisNeural", "tts_fallback_lang": "id",
        "region_label": "Island/Province", "regions": {
            "Bali": ["Ubud", "Seminyak", "Canggu", "Kuta", "Uluwatu", "Nusa Penida", "Sanur", "Lovina"],
            "Java": ["Jakarta", "Yogyakarta", "Borobudur", "Prambanan", "Bandung", "Mount Bromo"],
            "Nusa Tenggara": ["Lombok", "Komodo Island", "Flores", "Sumba"],
            "Sumatra": ["Lake Toba", "Bukit Lawang", "Padang", "Medan"],
            "Sulawesi": ["Makassar", "Toraja", "Bunaken", "Raja Ampat"],
            "Kalimantan": ["Borneo", "Orangutan sanctuaries"],
            "Maluku": ["Ambon", "Banda Islands"],
            "Papua": ["Raja Ampat", "Manokwari"],
        },
        "popular_destinations": ["Bali", "Ubud", "Komodo Island", "Lombok", "Borobudur", "Yogyakarta", "Raja Ampat", "Nusa Penida", "Mount Bromo", "Lake Toba", "Seminyak", "Canggu", "Flores", "Uluwatu", "Bukit Lawang", "Makassar", "Toraja", "Prambanan", "Bandung", "Sumba"],
    },
    "United Arab Emirates": {
        "code": "AE", "continent": "Asia",
        "currency": "AED", "currency_symbol": "AED",
        "timezone": "Asia/Dubai",
        "tts_voice": "ar-AE-FatimaNeural", "tts_fallback_lang": "ar",
        "region_label": "Emirate", "regions": {
            "Dubai": ["Dubai", "Palm Jumeirah", "Burj Khalifa", "Dubai Marina", "Old Dubai", "Deira", "JBR"],
            "Abu Dhabi": ["Abu Dhabi", "Yas Island", "Saadiyat Island", "Al Ain"],
            "Sharjah": ["Sharjah"],
            "Ras Al Khaimah": ["Ras Al Khaimah", "Jebel Jais"],
            "Fujairah": ["Fujairah"],
            "Ajman": ["Ajman"],
            "Umm Al Quwain": ["Umm Al Quwain"],
        },
        "popular_destinations": ["Dubai", "Abu Dhabi", "Palm Jumeirah", "Burj Khalifa", "Dubai Marina", "Sharjah", "Desert Safari", "Yas Island", "Al Ain", "Ras Al Khaimah", "Old Dubai", "JBR", "Saadiyat Island", "Jebel Jais", "Fujairah", "Louvre Abu Dhabi", "Dubai Creek", "Miracle Garden", "Global Village", "Deira"],
    },
    "Germany": {
        "code": "DE", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Berlin",
        "tts_voice": "de-DE-KatjaNeural", "tts_fallback_lang": "de",
        "region_label": "State", "regions": {
            "Bavaria": ["Munich", "Neuschwanstein", "Rothenburg", "Nuremberg", "Garmisch-Partenkirchen", "Berchtesgaden"],
            "Berlin": ["Berlin", "Brandenburg Gate", "Museum Island"],
            "Hamburg": ["Hamburg"],
            "Saxony": ["Dresden", "Leipzig", "Saxon Switzerland"],
            "Hesse": ["Frankfurt", "Rhine Valley", "Heidelberg"],
            "North Rhine-Westphalia": ["Cologne", "Dusseldorf", "Bonn", "Aachen"],
            "Baden-Württemberg": ["Stuttgart", "Black Forest", "Heidelberg", "Freiburg", "Lake Constance"],
            "Lower Saxony": ["Hanover", "Bremen"],
            "Thuringia": ["Erfurt", "Weimar"],
            "Schleswig-Holstein": ["Hamburg area", "Lübeck", "Sylt"],
            "Mecklenburg-Vorpommern": ["Rügen", "Stralsund"],
            "Brandenburg": ["Potsdam", "Spreewald"],
        },
        "popular_destinations": ["Berlin", "Munich", "Neuschwanstein", "Hamburg", "Dresden", "Cologne", "Frankfurt", "Heidelberg", "Black Forest", "Rothenburg", "Leipzig", "Dusseldorf", "Nuremberg", "Stuttgart", "Rhine Valley", "Saxon Switzerland", "Freiburg", "Berchtesgaden", "Bremen", "Lake Constance"],
    },
    "South Korea": {
        "code": "KR", "continent": "Asia",
        "currency": "KRW", "currency_symbol": "\u20a9",
        "timezone": "Asia/Seoul",
        "tts_voice": "ko-KR-SunHiNeural", "tts_fallback_lang": "ko",
        "region_label": "Province/City", "regions": {
            "Seoul": ["Seoul", "Gangnam", "Myeongdong", "Bukchon", "Insadong", "Hongdae", "Itaewon", "Namsan", "Dongdaemun"],
            "Busan": ["Busan", "Haeundae Beach", "Jagalchi Market", "Gamcheon Village"],
            "Gyeongju": ["Gyeongju", "Bulguksa", "Anapji", "Tumuli Park"],
            "Jeju Island": ["Jeju City", "Seogwipo", "Hallasan", "Seongsan Ilchulbong"],
            "Gangwon Province": ["Sokcho", "Seoraksan", "Pyongyang", "Chuncheon"],
            "Gyeonggi Province": ["Suwon", "Everland", "Lotte World"],
            "Incheon": ["Incheon", "Songdo"],
            "Daegu": ["Daegu"],
            "Daejeon": ["Daejeon"],
            "Jeolla Province": ["Gwangju", "Suncheon", "Yeosu"],
        },
        "popular_destinations": ["Seoul", "Busan", "Gyeongju", "Jeju Island", "Seoraksan", "Incheon", "Daegu", "Gangnam", "Bukchon", "Haeundae Beach", "Insadong", "Hongdae", "Namsan", "Chuncheon", "Gamcheon Village", "Gwangju", "Suncheon", "Everland", "Lotte World", "Jeonju"],
    },
    "Netherlands": {
        "code": "NL", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Amsterdam",
        "tts_voice": "nl-NL-ColetteNeural", "tts_fallback_lang": "nl",
        "region_label": "Province", "regions": {
            "North Holland": ["Amsterdam", "Haarlem", "Zaanse Schans", "Alkmaar"],
            "South Holland": ["Rotterdam", "The Hague", "Delft", "Leiden"],
            "Utrecht": ["Utrecht", "Amersfoort"],
            "North Brabant": ["Eindhoven", "Tilburg", "'s-Hertogenbosch"],
            "Groningen": ["Groningen"],
            "Friesland": ["Leeuwarden", "Friesland lakes"],
            "Zeeland": ["Middelburg", "Vlissingen", "Zeeuws-Vlaanderen"],
            "Limburg": ["Maastricht", "Valkenburg", "Venlo"],
            "Gelderland": ["Arnhem", "Nijmegen", "Veluwe"],
            "Overijssel": ["Zwolle", "Deventer"],
            "Drenthe": ["Assen", "Drenthe"],
            "Flevoland": ["Lelystad"],
        },
        "popular_destinations": ["Amsterdam", "Rotterdam", "The Hague", "Delft", "Zaanse Schans", "Utrecht", "Giethoorn", "Maastricht", "Haarlem", "Leiden", "Eindhoven", "Groningen", "Keukenhof", "Veluwe", "Texel", "Middelburg", "Zwolle", "Arnhem", "Valkenburg", "Nijmegen"],
    },
    "India": {
        "code": "IN", "continent": "Asia",
        "currency": "INR", "currency_symbol": "\u20b9",
        "timezone": "Asia/Kolkata",
        "tts_voice": "en-IN-NeerjaNeural", "tts_fallback_lang": "en",
        "region_label": "State", "regions": {
            "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati", "Araku Valley", "Lepakshi", "Amaravati", "Rajahmundry", "Kakinada", "Guntur"],
            "Arunachal Pradesh": ["Tawang", "Itanagar", "Ziro Valley", "Bomdila", "Pasighat"],
            "Assam": ["Guwahati", "Kaziranga", "Majuli", "Sibsagar", "Dibrugarh", "Jorhat", "Tezpur"],
            "Bihar": ["Patna", "Bodh Gaya", "Nalanda", "Rajgir", "Vaishali"],
            "Chhattisgarh": ["Raipur", "Chitrakote Falls", "Barnawapara", "Sirpur", "Dantewada"],
            "Goa": ["Panaji", "Margao", "Anjuna", "Palolem", "Arambol", "Calangute", "Colva", "Vagator", "Old Goa"],
            "Gujarat": ["Ahmedabad", "Gandhinagar", "Kutch", "Rann of Kutch", "Somnath", "Dwarka", "Junagadh", "Rajkot", "Surat", "Vadodara"],
            "Haryana": ["Gurugram", "Faridabad", "Kurukshetra", "Sultanpur National Park", "Pinjore Gardens"],
            "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "McLeod Ganj", "Spiti Valley", "Kasol", "Kullu", "Dalhousie", "Chamba", "Bir Billing", "Khadapathar"],
            "Jammu and Kashmir": ["Srinagar", "Gulmarg", "Pahalgam", "Sonamarg", "Leh", "Nubra Valley", "Pangong Lake", "Jammu"],
            "Jharkhand": ["Ranchi", "Netarhat", "Hundru Falls", "Dalma Wildlife Sanctuary", "Jamshedpur"],
            "Karnataka": ["Bengaluru", "Mysuru", "Coorg", "Hampi", "Gokarna", "Udupi", "Mangalore", "Badami", "Hampi", "Jog Falls"],
            "Kerala": ["Kochi", "Munnar", "Alleppey", "Thekkady", "Wayanad", "Kovalam", "Varkala", "Kumarakom", "Fort Kochi", "Athirapally Falls"],
            "Madhya Pradesh": ["Bhopal", "Khajuraho", "Orchha", "Ujjain", "Sanchi", "Pachmarhi", "Bandhavgarh", "Kanha", "Gwalior", "Indore"],
            "Maharashtra": ["Mumbai", "Pune", "Lonavala", "Mahabaleshwar", "Ajanta and Ellora Caves", "Nashik", "Alibaug", "Lavasa", "Matheran", "Shirdi"],
            "Manipur": ["Imphal", "Loktak Lake", "Kohima", "Ukhrul", "Churachandpur"],
            "Meghalaya": ["Shillong", "Cherrapunji", "Mawlynnong", "Dawki", "Tura", "Jowai", "Nongkhnum Island"],
            "Mizoram": ["Aizawl", "Champhai", "Reiek", "Hmuifang"],
            "Nagaland": ["Kohima", "Dimapur", "Dzukou Valley", "Kisama", "Mokokchung"],
            "Odisha": ["Bhubaneswar", "Puri", "Konark", "Chilika Lake", "Simlipal", "Rourkela", "Cuttack"],
            "Punjab": ["Amritsar", "Chandigarh", "Jalandhar", "Ludhiana", "Patiala", "Wagah Border"],
            "Rajasthan": ["Jaipur", "Udaipur", "Jaisalmer", "Jodhpur", "Mount Abu", "Pushkar", "Ranthambore", "Bundi", "Chittorgarh", "Bikaner"],
            "Sikkim": ["Gangtok", "Pelling", "Lachung", "Yumthang Valley", "Nathula Pass", "Ravangla"],
            "Tamil Nadu": ["Chennai", "Ooty", "Kodaikanal", "Madurai", "Mahabalipuram", "Coimbatore", "Rameswaram", "Thanjavur", "Pondicherry"],
            "Telangana": ["Hyderabad", "Warangal", "Nagarjuna Sagar", "Hampi", "Adilabad"],
            "Tripura": ["Agartala", "Unakoti", "Neermahal", "Sepahijala"],
            "Uttar Pradesh": ["Agra", "Varanasi", "Lucknow", "Mathura", "Vrindavan", "Allahabad", "Ayodhya", "Jhansi", "Chitrakoot"],
            "Uttarakhand": ["Rishikesh", "Haridwar", "Nainital", "Mussoorie", "Auli", "Valley of Flowers", "Kedarnath", "Badrinath", "Jim Corbett", "Chopta"],
            "West Bengal": ["Kolkata", "Darjeeling", "Sundarbans", "Digha", "Shantiniketan", "Siliguri", "Kalimpong"],
            "Andaman and Nicobar Islands": ["Port Blair", "Havelock Island", "Neil Island", "Ross Island", "Baratang Island", "Diglipur"],
            "Chandigarh": ["Chandigarh", "Rock Garden", "Sukhna Lake", "Elante Mall"],
            "Delhi": ["New Delhi", "Old Delhi", "Qutub Minar", "Red Fort", "India Gate", "Humayun's Tomb", "Chandni Chowk", "Connaught Place"],
            "Jammu and Kashmir (UT)": ["Leh", "Ladakh", "Pangong Lake", "Nubra Valley", "Zanskar"],
            "Ladakh": ["Leh", "Pangong Lake", "Nubra Valley", "Zanskar", "Kargil", "Hemis"],
            "Lakshadweep": ["Agatti", "Bangaram", "Minicoy", "Kavaratti"],
            "Puducherry": ["Pondicherry", "Auroville", "Karaikal", "Mahe", "Yanam"],
        },
        "popular_destinations": ["Goa", "Jaipur", "Udaipur", "Jaisalmer", "Rishikesh", "Manali", "Shimla", "Dharamshala", "Leh", "Srinagar", "Amritsar", "Varanasi", "Agra", "Delhi", "Mumbai", "Pune", "Bengaluru", "Mysuru", "Coorg", "Ooty", "Kodaikanal", "Chennai", "Pondicherry", "Hyderabad", "Hampi", "Kochi", "Munnar", "Alleppey", "Thekkady", "Madurai", "Kolkata", "Darjeeling", "Gangtok", "Shillong", "Kaziranga", "Andaman", "Spiti Valley", "Auli", "Nainital", "Mussoorie"],
    },
    "Croatia": {
        "code": "HR", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Zagreb",
        "tts_voice": "hr-HR-GabrijelaNeural", "tts_fallback_lang": "hr",
        "region_label": "County", "regions": {
            "Istria": ["Pula", "Rovinj", "Opatija", "Porec", "Motovun", "Umag"],
            "Dalmatia": ["Dubrovnik", "Split", "Zadar", "Trogir", "Sibenik", "Makarska", "Hvar", "Korcula", "Vis"],
            "Kvarner": ["Rijeka", "Opatija", "Cres", "Losinj", "Krk"],
            "Slavonia": ["Osijek", "Vukovar", "Ilok"],
            "Central Croatia": ["Zagreb", "Karlovac", "Samobor", "Varazdin", "Trakoscan"],
            "Plitvice Region": ["Plitvice Lakes", "Slunj", "Rastoke"],
        },
        "popular_destinations": ["Dubrovnik", "Split", "Plitvice Lakes", "Hvar", "Zadar", "Pula", "Rovinj", "Trogir", "Korcula", "Makarska", "Opatija", "Krka", "Dubrovnik Old Town", "Diocletian's Palace", "Brela Beach", "Sibenik", "Vis Island", "Motovun", "Osijek", "Cres"],
    },
    "Ireland": {
        "code": "IE", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Dublin",
        "tts_voice": "en-IE-EmilyNeural", "tts_fallback_lang": "en",
        "region_label": "Province", "regions": {
            "Leinster": ["Dublin", "Wicklow", "Kilkenny", "Waterford", "Wexford", "Kildare"],
            "Munster": ["Cork", "Galway", "Limerick", "Killarney", "Dingle", "Kenmare", "Cliffs of Moher"],
            "Connacht": ["Galway", "Westport", "Clare Island", "Aran Islands"],
            "Ulster (ROI)": ["Donegal", "Sligo", "Derry", "Belfast"],
        },
        "popular_destinations": ["Dublin", "Galway", "Cork", "Killarney", "Cliffs of Moher", "Dingle", "Ring of Kerry", "Belfast", "Kilkenny", "Donegal", "Connemara", "Sligo", "Wicklow", "Aran Islands", "Blarney Castle", "Glendalough", "Kenmare", "Westport", "Waterford", "Newgrange"],
    },
    "Singapore": {
        "code": "SG", "continent": "Asia",
        "currency": "SGD", "currency_symbol": "S$",
        "timezone": "Asia/Singapore",
        "tts_voice": "en-SG-LunaNeural", "tts_fallback_lang": "en",
        "region_label": "Region", "regions": {
            "Central Region": ["Marina Bay", "Sentosa", "Orchard Road", "Chinatown", "Kampong Glam", "Little India", "Raffles Place"],
            "East Region": ["Changi", "Tampines", "Katong", "East Coast Park"],
            "North Region": ["Woodlands", "Yishun", "Singapore Zoo"],
            "West Region": ["Jurong", "Sentosa", "Labrador Park"],
            "North-East Region": ["Hougang", "Serangoon", "Punggol"],
        },
        "popular_destinations": ["Marina Bay Sands", "Sentosa Island", "Gardens by the Bay", "Orchard Road", "Chinatown", "Little India", "Kampong Glam", "Singapore Zoo", "Changi Airport", "Raffles Hotel", "Clarke Quay", "Bukit Timah", "Haw Par Villa", "Sungei Buloh", "East Coast Park", "Jurong Bird Park", "Pulau Ubin", "Botanic Gardens", "Night Safari", "Jewel Changi"],
    },
    "Czech Republic": {
        "code": "CZ", "continent": "Europe",
        "currency": "CZK", "currency_symbol": "Kč",
        "timezone": "Europe/Prague",
        "tts_voice": "cs-CZ-VlastaNeural", "tts_fallback_lang": "cs",
        "region_label": "Region", "regions": {
            "Bohemia": ["Prague", "Karlovy Vary", "Cesky Krumlov", "Plzen", "Kutna Hora", "Brno"],
            "Moravia": ["Brno", "Olomouc", "Znojmo", "Telc", "Lednice"],
            "Silesia": ["Ostrava", "Beskydy"],
            "Bohemian Switzerland": ["Decin", "Hrensko", "Pravcicka Brana"],
        },
        "popular_destinations": ["Prague", "Cesky Krumlov", "Karlovy Vary", "Brno", "Kutna Hora", "Plzen", "Olomouc", "Telc", "Lednice", "Decin", "Krumlov", "Charles Bridge", "Prague Castle", "Old Town Square", "Wenceslas Square", "Znojmo", "Ostrava", "Beskydy", "Ceske Budejovice", "Tabor"],
    },
    "Sri Lanka": {
        "code": "LK", "continent": "Asia",
        "currency": "LKR", "currency_symbol": "Rs",
        "timezone": "Asia/Colombo",
        "tts_voice": "si-SL-ThiliniNeural", "tts_fallback_lang": "si",
        "region_label": "Province", "regions": {
            "Western Province": ["Colombo", "Negombo", "Bentota"],
            "Central Province": ["Kandy", "Nuwara Eliya", "Ella", "Sigiriya", "Dambulla"],
            "Southern Province": ["Galle", "Unawatuna", "Mirissa", "Yala", "Tangalle", "Hikkaduwa"],
            "Eastern Province": ["Trincomalee", "Arugam Bay", "Passikudah"],
            "North Central Province": ["Polonnaruwa", "Anuradhapura"],
            "Sabaragamuwa Province": ["Ratnapura", "Kitulgala"],
            "Uva Province": ["Bandarawela", "Haputale"],
        },
        "popular_destinations": ["Sigiriya", "Kandy", "Galle", "Ella", "Nuwara Eliya", "Yala National Park", "Mirissa", "Unawatuna", "Polonnaruwa", "Anuradhapura", "Dambulla", "Colombo", "Trincomalee", "Arugam Bay", "Hikkaduwa", "Tangalle", "Kitulgala", "Negombo", "Bentota", "Bandarawela"],
    },
    "Morocco": {
        "code": "MA", "continent": "Africa",
        "currency": "MAD", "currency_symbol": "MAD",
        "timezone": "Africa/Casablanca",
        "tts_voice": "ar-MA-AmiraNeural", "tts_fallback_lang": "ar",
        "region_label": "Region", "regions": {
            "Marrakech-Safi": ["Marrakech", "Essaouira", "Ouarzazate", "Ait Benhaddou"],
            "Casablanca-Setat": ["Casablanca", "Rabat", "Chefchaouen"],
            "Tangier-Tetouan-Al Hoceima": ["Tangier", "Tetouan", "Chefchaouen"],
            "Fes-Meknes": ["Fez", "Meknes", "Ifrane", "Volubilis"],
            "Souss-Massa": ["Agadir", "Taroudant", "Tiznit"],
            "Draa-Tafilalet": ["Merzouga", "Erfoud", "Todra Gorge", "Zagora"],
        },
        "popular_destinations": ["Marrakech", "Fez", "Chefchaouen", "Casablanca", "Essaouira", "Merzouga", "Tangier", "Agadir", "Ouarzazate", "Ait Benhaddou", "Rabat", "Todra Gorge", "Zagora", "Meknes", "Volubilis", "Tiznit", "Tetouan", "Ifrane", "Taroudant", "Erfoud"],
    },
    "Argentina": {
        "code": "AR", "continent": "South America",
        "currency": "ARS", "currency_symbol": "AR$",
        "timezone": "America/Argentina/Buenos_Aires",
        "tts_voice": "es-AR-TomasNeural", "tts_fallback_lang": "es",
        "region_label": "Province", "regions": {
            "Buenos Aires": ["Buenos Aires", "La Plata", "Mar del Plata"],
            "Patagonia": ["Bariloche", "El Calafate", "Ushuaia", "Puerto Madryn", "Perito Moreno Glacier", "El Chalten"],
            "Mendoza": ["Mendoza", "Villas Godel", "Aconcagua"],
            "Cordoba": ["Cordoba", "Villa Carlos Paz", "La Cumbrecita"],
            "Salta & Jujuy": ["Salta", "Jujuy", "Purmamarca", "Tilcara", "Humahuaca"],
            "Iguazu": ["Puerto Iguazu", "Iguazu Falls"],
        },
        "popular_destinations": ["Buenos Aires", "Bariloche", "El Calafate", "Ushuaia", "Mendoza", "Iguazu Falls", "Salta", "Cordoba", "Puerto Madryn", "Mar del Plata", "Perito Moreno Glacier", "El Chalten", "La Plata", "Purmamarca", "Villa Carlos Paz", "Jujuy", "Tilcara", "Humahuaca", "Aconcagua", "La Cumbrecita"],
    },
    "Finland": {
        "code": "FI", "continent": "Europe",
        "currency": "EUR", "currency_symbol": "\u20ac",
        "timezone": "Europe/Helsinki",
        "tts_voice": "fi-FI-HarriNeural", "tts_fallback_lang": "fi",
        "region_label": "Region", "regions": {
            "Uusimaa": ["Helsinki", "Espoo", "Vantaa", "Porvoo"],
            "Lapland": ["Rovaniemi", "Levi", "Saariselka", "Inari", "Kilpisjarvi"],
            "Southwest Finland": ["Turku", "Naantali", "Rauma"],
            "Ostrobothnia": ["Oulu", "Raahe", "Kalajoki"],
            "Kainuu": ["Kajaani", "Kuhmo"],
            "Tavastia": ["Hameenlinna", "Lahti"],
            "Finnish Lakeland": ["Savonlinna", "Lappeenranta", "Kuopio", "Joensuu"],
        },
        "popular_destinations": ["Helsinki", "Rovaniemi", "Levi", "Lapland", "Turku", "Porvoo", "Saariselka", "Inari", "Oulu", "Naantali", "Rauma", "Savonlinna", "Lappeenranta", "Kuopio", "Hameenlinna", "Lahti", "Kalajoki", "Kilpisjarvi", "Espoo", "Kajaani"],
    },
    "China": {
        "code": "CN", "continent": "Asia",
        "currency": "CNY", "currency_symbol": "¥",
        "timezone": "Asia/Shanghai",
        "tts_voice": "zh-CN-XiaoxiaoNeural", "tts_fallback_lang": "zh",
        "region_label": "Province", "regions": {
            "Beijing": ["Beijing", "Great Wall", "Forbidden City", "Temple of Heaven", "Summer Palace"],
            "Shanghai": ["Shanghai", "The Bund", "Yu Garden", "Nanjing Road"],
            "Guangdong": ["Guangzhou", "Shenzhen", "Zhuhai"],
            "Sichuan": ["Chengdu", "Leshan", "Jiuzhaigou", "Mount Emei"],
            "Yunnan": ["Kunming", "Dali", "Lijiang", "Shangri-La", "Tiger Leaping Gorge"],
            "Shaanxi": ["Xi'an", "Terracotta Army", "Huashan"],
            "Guilin & Guangxi": ["Guilin", "Yangshuo", "Longji Rice Terraces"],
            "Zhejiang": ["Hangzhou", "West Lake", "Ningbo"],
            "Jiangsu": ["Nanjing", "Suzhou", "Wuxi"],
            "Hainan": ["Sanya", "Haikou"],
        },
        "popular_destinations": ["Beijing", "Shanghai", "Xi'an", "Guilin", "Chengdu", "Hangzhou", "Lijiang", "Suzhou", "Shenzhen", "Great Wall", "Forbidden City", "Terracotta Army", "Yangshuo", "Dali", "Shangri-La", "Kunming", "Leshan", "Jiuzhaigou", "Sanya", "Nanjing"],
    },
}

# Quick-access mappings
ALL_COUNTRY_NAMES = sorted(COUNTRIES.keys())
ALL_COUNTRIES_BY_CODE = {v["code"]: k for k, v in COUNTRIES.items()}

# Season maps per hemisphere
_NORTHERN_HEMISPHERE_SEASONS = {
    1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring", 6: "Summer",
    7: "Summer", 8: "Summer", 9: "Autumn", 10: "Autumn", 11: "Autumn", 12: "Winter",
}
_SOUTHERN_HEMISPHERE_SEASONS = {
    1: "Summer", 2: "Summer", 3: "Autumn", 4: "Autumn", 5: "Autumn", 6: "Winter",
    7: "Winter", 8: "Winter", 9: "Spring", 10: "Spring", 11: "Spring", 12: "Summer",
}
_SOUTHEAST_ASIA_SEASONS = {
    1: "Dry Season", 2: "Dry Season", 3: "Hot Season", 4: "Hot Season", 5: "Wet Season", 6: "Wet Season",
    7: "Wet Season", 8: "Wet Season", 9: "Wet Season", 10: "Wet Season", 11: "Cool Season", 12: "Cool Season",
}
_TROPICAL_SEASONS = {
    1: "Dry Season", 2: "Dry Season", 3: "Dry Season", 4: "Wet Season", 5: "Wet Season", 6: "Wet Season",
    7: "Wet Season", 8: "Wet Season", 9: "Wet Season", 10: "Wet Season", 11: "Wet Season", 12: "Dry Season",
}

_SOUTHERN_COUNTRIES = {"Australia", "New Zealand", "Brazil", "South Africa", "Argentina"}
_TROPICAL_COUNTRIES = {"Thailand", "Vietnam", "Indonesia", "Maldives", "Costa Rica", "Singapore", "Sri Lanka"}
_SOUTHEAST_ASIA_COUNTRIES = {"Thailand", "Vietnam", "Indonesia", "Singapore"}

# Countries with multiple timezone spans
_MULTI_TIMEZONE_COUNTRIES = {"United States", "Canada", "Australia", "Indonesia", "China"}


def get_country_info(country_name):
    return COUNTRIES.get(country_name)


def get_regions(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return []
    return list(country["regions"].keys())


def get_cities(country_name, region_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return []
    return country["regions"].get(region_name, [])


def get_region_label(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "Region"
    return country["region_label"]


def get_currency(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "USD"
    return country["currency"]


def get_currency_symbol(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "$"
    return country["currency_symbol"]


def get_timezone(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "UTC"
    return country["timezone"]


def get_tts_voice(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "en-US-JennyNeural"
    return country["tts_voice"]


def get_tts_fallback_lang(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "en"
    return country["tts_fallback_lang"]


def get_season(month, country_name=None):
    if country_name in _SOUTHERN_COUNTRIES:
        return _SOUTHERN_HEMISPHERE_SEASONS.get(month, "Season")
    if country_name in _SOUTHEAST_ASIA_COUNTRIES:
        return _SOUTHEAST_ASIA_SEASONS.get(month, "Season")
    if country_name in _TROPICAL_COUNTRIES:
        return _TROPICAL_SEASONS.get(month, "Season")
    return _NORTHERN_HEMISPHERE_SEASONS.get(month, "Season")


def get_popular_destinations(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return []
    return country.get("popular_destinations", [])


def get_all_popular_destinations(count=20):
    import random
    all_dests = []
    for cname, cdata in COUNTRIES.items():
        for dest in cdata.get("popular_destinations", [])[:5]:
            all_dests.append(dest)
    random.shuffle(all_dests)
    return all_dests[:count]


def get_continent(country_name):
    country = COUNTRIES.get(country_name)
    if not country:
        return "Unknown"
    return country["continent"]


def search_destinations(query):
    """Search across all countries, regions, and cities for a matching name."""
    query_lower = query.lower().strip()
    results = []
    for cname, cdata in COUNTRIES.items():
        if query_lower in cname.lower():
            results.append({"type": "country", "name": cname, "country": cname})
        for rname, cities in cdata["regions"].items():
            if query_lower in rname.lower():
                results.append({"type": "region", "name": rname, "country": cname})
            for city in cities:
                if query_lower in city.lower():
                    results.append({"type": "city", "name": city, "country": cname, "region": rname})
    return results


def get_serper_gl_code(country_name):
    """Return the Serper geo-locale code for a country."""
    country = COUNTRIES.get(country_name)
    if not country:
        return "us"
    code_map = {
        "IT": "it", "JP": "jp", "FR": "fr", "ES": "es", "US": "us",
        "NZ": "nz", "GR": "gr", "CH": "ch", "AU": "au", "TH": "th",
        "GB": "uk", "CA": "ca", "MV": "mv", "PT": "pt", "IS": "is",
        "BR": "br", "CR": "cr", "MX": "mx", "VN": "vn", "AT": "at",
        "EG": "eg", "ZA": "za", "NO": "no", "TR": "tr", "PE": "pe",
        "ID": "id", "AE": "ae", "DE": "de", "KR": "kr", "NL": "nl",
        "IN": "in", "HR": "hr", "IE": "ie", "SG": "sg", "CZ": "cz",
        "LK": "lk", "MA": "ma", "AR": "ar", "FI": "fi", "CN": "cn",
    }
    return code_map.get(country["code"], "us")


def get_country_center_coords(country_name):
    """Return approximate center coordinates for a country."""
    coords = {
        "Italy": {"lat": 41.8719, "lng": 12.5674},
        "Japan": {"lat": 36.2048, "lng": 138.2529},
        "France": {"lat": 46.2276, "lng": 2.2137},
        "Spain": {"lat": 40.4637, "lng": -3.7492},
        "United States": {"lat": 37.0902, "lng": -95.7129},
        "New Zealand": {"lat": -40.9006, "lng": 174.8860},
        "Greece": {"lat": 39.0742, "lng": 21.8243},
        "Switzerland": {"lat": 46.8182, "lng": 8.2275},
        "Australia": {"lat": -25.2744, "lng": 133.7751},
        "Thailand": {"lat": 15.8700, "lng": 100.9925},
        "United Kingdom": {"lat": 55.3781, "lng": -3.4360},
        "Canada": {"lat": 56.1304, "lng": -106.3468},
        "Maldives": {"lat": 3.2028, "lng": 73.2207},
        "Portugal": {"lat": 39.3999, "lng": -8.2245},
        "Iceland": {"lat": 64.9631, "lng": -19.0208},
        "Brazil": {"lat": -14.2350, "lng": -51.9253},
        "Costa Rica": {"lat": 9.7489, "lng": -83.7534},
        "Mexico": {"lat": 23.6345, "lng": -102.5528},
        "Vietnam": {"lat": 14.0583, "lng": 108.2772},
        "Austria": {"lat": 47.5162, "lng": 14.5501},
        "Egypt": {"lat": 26.8206, "lng": 30.8025},
        "South Africa": {"lat": -30.5595, "lng": 22.9375},
        "Norway": {"lat": 60.4720, "lng": 8.4689},
        "Turkey": {"lat": 38.9637, "lng": 35.2433},
        "Peru": {"lat": -9.1900, "lng": -75.0152},
        "Indonesia": {"lat": -0.7893, "lng": 113.9213},
        "United Arab Emirates": {"lat": 23.4241, "lng": 53.8478},
        "Germany": {"lat": 51.1657, "lng": 10.4515},
        "South Korea": {"lat": 35.9078, "lng": 127.7669},
        "Netherlands": {"lat": 52.1326, "lng": 5.2913},
        "India": {"lat": 20.5937, "lng": 78.9629},
        "Croatia": {"lat": 45.1000, "lng": 15.2000},
        "Ireland": {"lat": 53.1424, "lng": -7.6921},
        "Singapore": {"lat": 1.3521, "lng": 103.8198},
        "Czech Republic": {"lat": 49.8175, "lng": 15.4730},
        "Sri Lanka": {"lat": 7.8731, "lng": 80.7718},
        "Morocco": {"lat": 31.7917, "lng": -7.0926},
        "Argentina": {"lat": -38.4161, "lng": -63.6167},
        "Finland": {"lat": 61.9241, "lng": 25.7482},
        "China": {"lat": 35.8617, "lng": 104.1954},
    }
    return coords.get(country_name, {"lat": 20.0, "lng": 0.0})


def get_all_destination_names(count=60):
    """Return a flat list of popular destination names across all supported countries."""
    import random as _random
    all_names = []
    for cname, cdata in COUNTRIES.items():
        for dest in cdata.get("popular_destinations", []):
            all_names.append(dest)
    _random.shuffle(all_names)
    return all_names[:count]


def get_daily_destinations(count=20):
    """Get a rotating daily set of global destination names."""
    import random as _random
    from datetime import datetime as _datetime
    today = _datetime.utcnow().date()
    all_names = []
    for cname, cdata in COUNTRIES.items():
        for dest in cdata.get("popular_destinations", []):
            all_names.append(dest)
    day_num = today.toordinal()
    _random.Random(f"daily-global-{today.isoformat()}").shuffle(all_names)
    start = (day_num * 7) % max(len(all_names), 1)
    return [all_names[(start + i) % len(all_names)] for i in range(min(count, len(all_names)))]
