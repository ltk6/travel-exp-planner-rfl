"""
maps/tags.py
============

Controlled travel ontology for Vietnam destination tagging.

Used by BOTH location profiles and user-intent signals. Both sides map
into this shared vocabulary; cosine similarity across the shared embedding
space produces the relevance score fed into N4 ranking.

─────────────────────────────────────────────────────────────
DESIGN PRINCIPLES
─────────────────────────────────────────────────────────────

Expansions are written to maximise BGE-M3 retrieval signal:
  • 4–10 tokens of semantically adjacent English travel vocabulary
  • No mere restatement of the key (e.g. "beach" → "beach coastal" is weak)
  • Prefer evocative, discriminative phrases over generic fillers
  • Each expansion must pull the vector toward a distinct cluster in the
    embedding space so that user ↔ location cosine distances are meaningful
  • No proper nouns (place names, brand names, ethnic-group names) in any
    expansion — tags describe attributes of "big locations", not specific
    sites, so a single named place should never anchor a tag's vector
  • Tag keys must stay broad enough to match multiple destinations; a key
    that realistically applies to only one site belongs merged into a
    broader neighbour, not as its own entry

─────────────────────────────────────────────────────────────
SECTION INDEX
─────────────────────────────────────────────────────────────

  A. TERRAIN & LANDSCAPE   — physical geography, natural features
  B. WATER & COAST         — ocean, rivers, lakes, marine ecosystems
  C. FLORA & ECOSYSTEMS    — vegetation, protected areas
  D. CLIMATE & SEASON      — weather windows, temperature zones
  E. CULTURE & HERITAGE    — history, religion, ethnicity, arts
  F. URBAN & SETTLEMENT    — city types, neighbourhoods, markets
  G. ACTIVITIES — LAND     — trekking, cycling, aerial, overland adventure
  H. ACTIVITIES — WATER    — diving, paddling, boat experiences
  I. ACTIVITIES — LEISURE  — wellness, classes, soft experiences
  J. FOOD & DRINK          — cuisine types, dining styles, specialties
  K. VIBE & MOOD           — atmosphere, aesthetic, emotional tone
  L. TRIP PROFILE          — duration, pace, group composition
  M. BUDGET & STYLE        — spend level, accommodation style
  N. SPECIAL INTEREST      — niche travel segments
"""

# ──────────────────────────────────────────────────────────────────────────────
# A. TERRAIN & LANDSCAPE
# ──────────────────────────────────────────────────────────────────────────────

TERRAIN = {
    # Relief
    "mountain"          : "high mountain summit alpine trekking elevation",
    "hill"              : "gentle rolling hills countryside walking",
    "karst"             : "limestone karst tower pinnacle dramatic geology",
    "valley"            : "valley basin lowland surrounded by peaks",
    "plateau"           : "highland plateau open sky grassland tableland",
    "cliff"             : "sea cliff coastal rock face dramatic drop",
    "cave"              : "cave cavern underground stalactite hidden world",
    "sand dune"         : "sand dune arid golden landscape shifting coastal desert",

    # Lowland & delta
    "delta"             : "river delta flat wetland sediment fertile plain",
    "plain"             : "open flatland rural paddy countryside horizon",

    # Agricultural landscape
    "rice terrace"      : "terraced rice field hillside cultivation harvest scenic",
    "farm"              : "agricultural farm orchard countryside agro-tourism",
    "flower field"      : "flower meadow blossom field colourful seasonal bloom",
    "tea plantation"    : "tea plantation terraced hills green highland harvest",
}

# ──────────────────────────────────────────────────────────────────────────────
# B. WATER & COAST
# ──────────────────────────────────────────────────────────────────────────────

WATER = {
    # Coastal & marine
    "beach"             : "sandy beach sun sea swimming tropical coast",
    "bay"               : "sheltered bay calm turquoise water anchorage",
    "island"            : "island remote tropical escape surrounded by sea",
    "archipelago"       : "island chain multiple islands hopping boat sea",
    "lagoon"            : "enclosed coastal lagoon calm shallow water",

    # Freshwater
    "lake"              : "scenic inland lake calm reflection mountain",
    "river"             : "river cruise floating winding waterway landscape",
    "stream"            : "freshwater stream forest babbling brook cool",
    "waterfall"         : "waterfall cascade vertical drop mist jungle",
    "hot spring"        : "thermal hot spring mineral soaking natural spa",
    "wetland"           : "wetland mangrove biodiversity bird sanctuary",

    # Marine ecosystems
    "coral reef"        : "coral reef marine biodiversity underwater colour",
    "mangrove"          : "mangrove forest coastal ecosystem kayak wildlife",
}

# ──────────────────────────────────────────────────────────────────────────────
# C. FLORA & ECOSYSTEMS
# ──────────────────────────────────────────────────────────────────────────────

ECOSYSTEM = {
    "national park"     : "protected national park wildlife forest reserve",
    "forest"            : "dense jungle rainforest canopy trekking shade",
    "pine forest"       : "pine forest cool misty highland atmospheric",
    "bamboo forest"     : "bamboo grove green tranquil walk shade",
    "biosphere reserve" : "UNESCO biosphere reserve pristine ecology conservation",
    "nature reserve"    : "wildlife nature reserve conservation endangered species",
    "birdwatching"      : "birdwatching rare species wetland binoculars nature",
    "wildlife"          : "wildlife safari animal encounter jungle biodiversity",
}

# ──────────────────────────────────────────────────────────────────────────────
# D. CLIMATE & SEASON
# ──────────────────────────────────────────────────────────────────────────────

SEASON = {
    # Temperature zones
    "cool climate"      : "cool highland climate fresh air escape heat",
    "tropical"          : "tropical warm sunny year round humid lush",
    "cold"              : "cold winter frost crisp mountain air sweater",

    # Travel windows
    "dry season"        : "dry season clear skies sunny ideal travel weather",
    "rainy season"      : "rainy season lush green rivers full dramatic",
    "summer trip"       : "summer school holiday hot beach sea swimming",
    "winter trip"       : "winter cold season frost highland unique",
    "spring trip"       : "spring blossom mild weather comfortable outdoor",
    "autumn trip"       : "autumn harvest golden rice cool comfortable trekking",

    # Specific phenomena
    "snow"              : "snowfall frost winter rare cold highland mountain",
    "cloud sea"         : "cloud sea fog inversion highland sunrise mystical",
    "flower season"     : "flower blooming season colourful landscape photography",
    "harvest season"    : "harvest season golden rice terrace autumn rural beauty",
}

# ──────────────────────────────────────────────────────────────────────────────
# E. CULTURE & HERITAGE
# ──────────────────────────────────────────────────────────────────────────────

CULTURE = {
    # Historical eras & sites
    "history"           : "historical heritage site war ancient dynasty cultural depth",
    "war history"       : "war battlefield bunker tunnel military history memorial",
    "colonial heritage" : "colonial architecture villa mansion old quarter",
    "imperial"          : "imperial citadel royal palace dynastic forbidden city",
    "prehistoric"       : "prehistoric archaeological ancient cave painting site",

    # Religion & spiritual
    "temple"            : "temple worship incense spiritual ritual devotion",
    "pagoda"            : "Buddhist pagoda lotus pond bell tower monk",
    "church"            : "colonial church cathedral religious architecture",
    "meditation"        : "meditation retreat mindfulness silent practice inner peace",

    # Ethnic & indigenous
    "ethnic minority"   : "highland ethnic minority tribe indigenous culture village",
    "ethnic village"    : "traditional ethnic minority village homestay customs dress",
    "craft village"     : "traditional craft village artisan pottery lacquer silk weaving",

    # Arts & performance
    "traditional music" : "traditional music water puppet folk performance",
    "water puppet"      : "water puppet show traditional theatre folk art performance",
    "festival"          : "local festival celebration lantern fire flower crowd ceremony",
    "art"               : "contemporary art gallery creative district exhibition",

    # UNESCO
    "UNESCO heritage"   : "UNESCO world heritage site globally significant protected",
}

# ──────────────────────────────────────────────────────────────────────────────
# F. URBAN & SETTLEMENT
# ──────────────────────────────────────────────────────────────────────────────

URBAN = {
    "city"              : "urban city modern amenities transport nightlife dining",
    "old town"          : "preserved old town walking heritage narrow alley merchant",
    "village"           : "rural village slow life community genuine local",
    "fishing village"   : "fishing village boat dock morning catch coastal life",
    "market"            : "local market fresh produce commerce noise colour",
    "night market"      : "night market street food stalls lantern bargain buzz",
    "floating market"   : "floating market river boat vendor dawn delta",
    "walking street"    : "pedestrian walking street evening crowd souvenir cafe",
    "rooftop bar"       : "rooftop bar skyline city view cocktail sunset panorama",
}

# ──────────────────────────────────────────────────────────────────────────────
# G. ACTIVITIES — LAND
# ──────────────────────────────────────────────────────────────────────────────

ACTIVITIES_LAND = {
    # Overland & trail
    "trekking"          : "multi-day trekking mountain trail jungle endurance rewarding",
    "hiking"            : "day hike trail nature walk scenic viewpoint fitness",
    "motorbiking"       : "motorbike road trip winding pass freedom open road",
    "motorbike loop"    : "multi-day motorbike loop winding mountain pass adventure road trip",
    "cycling"           : "cycling bike countryside rural road slow discovery",
    "rock climbing"     : "rock climbing bouldering vertical sport outdoor challenge",
    "caving"            : "caving spelunking underground giant cavern dark adventure",
    "canyoning"         : "canyoning waterfall rappel water jump adrenaline gorge",
    "zip lining"        : "zip lining canopy aerial forest fly speed thrill",
    "camping"           : "camping tent outdoor overnight stargazing nature immersion",
    "jeep tour"         : "off-road jeep 4WD rugged terrain highland adventure",
    "train journey"     : "scenic train slow travel railway mountain coastal pass",
    "night train"       : "overnight sleeper train cabin slow journey",
    "cyclo"             : "cyclo pedicab city tour slow old quarter colonial streets",
    "photography"       : "landscape photography golden hour composition travel art",
    "shopping"          : "shopping souvenir retail handicraft boutique market",
    "golf"              : "golf resort course green sport premium leisure",
    "trail running"     : "trail running mountain race endurance sport outdoor fitness",
    "scooter tour"      : "scooter tour motorbike passenger city sight exploration",

    # Aerial
    "paragliding"       : "paragliding tandem aerial rice terrace mountain valley glide",
    "hot air balloon"   : "hot air balloon sunrise aerial float landscape photography",
    "cable car"         : "cable car gondola mountain record aerial scenic",
}

# ──────────────────────────────────────────────────────────────────────────────
# H. ACTIVITIES — WATER
# ──────────────────────────────────────────────────────────────────────────────

ACTIVITIES_WATER = {
    "scuba diving"      : "scuba diving underwater coral fish reef certification depth",
    "snorkeling"        : "snorkeling reef fish mask fins shallow clear water",
    "kayaking"          : "kayaking paddle sea cave lagoon mangrove self-propelled",
    "stand up paddle"   : "stand up paddleboard SUP flat water balance sunrise",
    "surfing"           : "surfing ocean swell wave board sport adrenaline beach",
    "kitesurfing"       : "kitesurfing wind kite board speed coastal sport",
    "boat cruise"       : "boat cruise scenic waterway overnight luxury sunset",
    "junk boat"         : "traditional wooden boat overnight bay cruise heritage",
    "speed boat"        : "speed boat fast island transfer coastal excursion",
    "fishing"           : "fishing boat local catch rod sea night lamp experience",
    "river cruise"      : "river cruise delta slow boat floating village",
    "rafting"           : "river rafting white water rapids adrenaline jungle",
    "swimming"          : "swimming beach ocean pool refreshing resort leisure",
    "bamboo rafting"    : "bamboo rafting slow river scenic traditional float",
    "waterfall jumping" : "waterfall jump cliff diving deep pool adventure",
}

# ──────────────────────────────────────────────────────────────────────────────
# I. ACTIVITIES — LEISURE, WELLNESS & LEARNING
# ──────────────────────────────────────────────────────────────────────────────

ACTIVITIES_LEISURE = {
    # Wellness
    "spa"               : "luxury spa massage body treatment relaxation resort pampering",
    "yoga retreat"      : "yoga retreat morning practice wellness mindful beach mountain",
    "wellness retreat"  : "wellness retreat holistic healing detox rejuvenate resort",
    "hot spring bath"   : "natural hot spring thermal soak mineral outdoor relaxation",

    # Cultural learning
    "cooking class"     : "cooking class recipe local market ingredient hands-on",
    "farm tour"         : "agro farm tour pick fruit vegetable rural sustainable food",
    "tea tasting"       : "tea tasting highland plantation ceremony ritual flavor",
    "coffee tour"       : "coffee plantation tour tasting highland local brew",
    "cultural show"     : "cultural performance folk dance ethnic show traditional costume",

    # Family & recreation
    "theme park"        : "amusement theme park rides family fun entertainment",
    "water park"        : "water park slides pool wave aquatic family leisure",
    "picnic"            : "picnic lakeside meadow relaxed outdoor leisure casual",
    "night tour"        : "night tour city illuminated ghost history lantern atmospheric",
    "volunteering"      : "volunteer community work social impact giving back",
}

# ──────────────────────────────────────────────────────────────────────────────
# J. FOOD & DRINK
# ──────────────────────────────────────────────────────────────────────────────

FOOD = {
    # Styles
    "street food"       : "street food stall vendor sidewalk authentic cheap local",
    "local cuisine"     : "regional local dish specialty home cooking traditional recipe",
    "fine dining"       : "fine dining upscale restaurant tasting menu elegant chef",
    "food tour"         : "guided food tour tasting multiple stops culinary discovery",
    "royal cuisine"     : "imperial court cuisine elaborate refined heritage",

    # Dietary
    "seafood"           : "fresh seafood grilled crab prawn squid coastal feast",
    "vegetarian"        : "vegetarian plant-based friendly menu temple food",
    "vegan"             : "vegan whole-food plant-based no animal product menu",
    "halal"             : "halal certified Muslim friendly food prayer facility",
    "organic"           : "organic farm-to-table clean food sustainable healthy",

    # Drinks
    "coffee"            : "coffee culture drip iced milk sidewalk cafe morning ritual",
    "craft beer"        : "craft beer local microbrewery social sidewalk",
    "bia hoi"           : "fresh draft beer corner street local gathering cheap",
    "tropical fruit"    : "exotic tropical fruit market taste fresh seasonal",
    "local wine"        : "local rice wine traditional fermented highland spirits",
    "tea"               : "highland tea plantation artisan green oolong ceremony taste",
}

# ──────────────────────────────────────────────────────────────────────────────
# K. VIBE & MOOD
# ──────────────────────────────────────────────────────────────────────────────

VIBE = {
    # Peace & energy
    "peaceful"          : "peaceful serene quiet undisturbed calm retreat nature",
    "vibrant"           : "vibrant energetic buzzing lively social dynamic city",
    "chill"             : "chill laid-back slow afternoon hammock no rush",

    # Emotional tone
    "romantic"          : "romantic intimate couple sunset candle private getaway",
    "mysterious"        : "mysterious misty atmospheric eerie ancient sacred unknown",
    "wild"              : "wild raw untamed rugged off-grid frontier nature",
    "cozy"              : "cozy warm fireplace cabin blanket intimate indoor comfort",
    "nostalgic"         : "nostalgic retro vintage old film timeworn heritage memory",
    "spiritual"         : "spiritual sacred pilgrimage devotion incense prayer meaning",

    # Aesthetic
    "rustic"            : "rustic simple bare honest wooden earthy primitive genuine",
    "picturesque"       : "picturesque postcard view stunning landscape photo worthy",
    "bohemian"          : "bohemian artistic creative independent eclectic traveller",
    "instagrammable"    : "photogenic iconic visual stunning selfie landmark",
    "modern"            : "modern sleek contemporary urban architecture design",

    # Discovery type
    "off the beaten path" : "hidden gem undiscovered crowd-free local secret untouched",
    "authentic"         : "authentic genuine unfiltered real local community no tourist trap",
    "immersive"         : "immersive deep culture live with locals hands-on full experience",
    "adventure"         : "adventure challenge push limits unknown thrill outdoor discovery",
}

# ──────────────────────────────────────────────────────────────────────────────
# L. TRIP PROFILE
# ──────────────────────────────────────────────────────────────────────────────

TRIP_PROFILE = {
    # Duration
    "day trip"          : "one day excursion nearby short easy return no overnight",
    "weekend trip"      : "2-3 day weekend short getaway close to city quick escape",
    "long stay"         : "extended stay week month slow travel deep immersion",
    "workcation"        : "remote work vacation long stay wifi cafe slow travel digital",

    # Companion type
    "solo"              : "solo travel independent safe walkable self-discovery freedom",
    "couple"            : "couple romantic private intimate honeymoon anniversary",
    "honeymoon"         : "honeymoon luxury romantic private resort couple sunset",
    "family"            : "family children friendly safe activities pool easy access",
    "group"             : "group travel social shared tour activities crowd fun",
    "friends trip"      : "friends group party social nightlife activities adventure",
    "corporate"         : "corporate team building incentive event meeting",

    # Pace
    "backpacking"       : "budget backpacker hostel flexible schedule low cost explore",
    "slow travel"       : "slow travel immersive long stay local rhythm community daily life",
}

# ──────────────────────────────────────────────────────────────────────────────
# M. BUDGET & ACCOMMODATION STYLE
# ──────────────────────────────────────────────────────────────────────────────

BUDGET = {
    "budget"            : "budget affordable cheap hostel local eatery backpacker",
    "mid range"         : "mid range comfortable hotel good value moderate spend",
    "luxury"            : "luxury five-star resort private pool butler premium",
    "boutique"          : "boutique hotel small intimate design character unique stay",
    "homestay"          : "homestay local family community warm cultural immersion",
    "eco lodge"         : "eco lodge sustainable forest nature immersive low impact",
    "resort"            : "beach resort pool spa all-inclusive leisure facility",
    "glamping"          : "glamping luxury tent outdoor comfort nature premium camping",
    "pet friendly"      : "pet friendly dog cat welcome accommodation travel",
    "wheelchair accessible" : "wheelchair accessible disabled friendly easy mobility",
}

# ──────────────────────────────────────────────────────────────────────────────
# N. SPECIAL INTEREST SEGMENTS
# ──────────────────────────────────────────────────────────────────────────────

SPECIAL_INTEREST = {
    "eco travel"        : "eco sustainable green low impact responsible conservation",
    "agro tourism"      : "agro farm village harvest fruit pick rice planting rural",
    "medical tourism"   : "medical tourism health check dental procedure hospital international",
    "wellness tourism"  : "wellness holistic spa yoga herbal healing rejuvenation retreat",
    "culinary tourism"  : "culinary food-focused trip market class tasting regional dish",
    "MICE"              : "meeting incentive conference exhibition business event venue",
    "digital nomad"     : "digital nomad remote worker long stay coworking wifi cafe coliving",
    "war tourism"       : "war memorial battlefield tunnel history veteran emotional heritage",
    "religious tourism" : "pilgrimage temple pagoda church sacred festival devotion",
    "sports tourism"    : "sports active marathon cycling golf surfing competition event",
    "photography tour"  : "photography tour golden hour guided landscape portrait composition",
    "nightlife"         : "nightlife bar club live music late night social entertainment",
    "luxury travel"     : "ultra luxury exclusive private yacht villa helicopter concierge",
}

# ──────────────────────────────────────────────────────────────────────────────
# MASTER REGISTRY
# ──────────────────────────────────────────────────────────────────────────────

ALL_TAGS: dict[str, str] = {
    **TERRAIN,
    **WATER,
    **ECOSYSTEM,
    **SEASON,
    **CULTURE,
    **URBAN,
    **ACTIVITIES_LAND,
    **ACTIVITIES_WATER,
    **ACTIVITIES_LEISURE,
    **FOOD,
    **VIBE,
    **TRIP_PROFILE,
    **BUDGET,
    **SPECIAL_INTEREST,
}