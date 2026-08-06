"""
maps/activity_tags.py (Trimmed-down version of tags.py)
=====================

Controlled travel ontology for Vietnam activity tagging and constraints.
Designed to focus on highly specific, evocative, and action-oriented activities.

Generic activities (such as swimming, shopping, photography, or dining) are omitted
here because they are already inferred directly from location type or tag attributes,
ensuring clean semantic vector spaces without redundant matching.

─────────────────────────────────────────────────────────────
DESIGN PRINCIPLES
─────────────────────────────────────────────────────────────

Expansions are written to maximise BGE-M3 retrieval signal:
  • 4–10 tokens of semantically adjacent English travel vocabulary
  • Prefer evocative, discriminative phrases over generic fillers
  • Activity tags are trimmed of highly generic/redundant entries
  • Tag keys must stay broad enough to match multiple destinations
"""

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
    **ACTIVITIES_LAND,
    **ACTIVITIES_WATER,
    **ACTIVITIES_LEISURE,
    **FOOD,
    **VIBE,
    **TRIP_PROFILE,
    **BUDGET,
    **SPECIAL_INTEREST,
}