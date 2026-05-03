BOT_NAME = 'sneakerz'

SPIDER_MODULES = ['scraper']

# Respecter les règles
ROBOTSTXT_OBEY = False

# Délais pour éviter le ban
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1

# Headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,en;q=0.9',
}

# Output JSON
FEEDS = {
    'data/%(name)s_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
    }
}

# Pipelines
ITEM_PIPELINES = {
    'scraper.pipelines.SneakerzPipeline': 300,
}