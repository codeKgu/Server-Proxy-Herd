SERVER_IDS = ['Goloman', 'Hands', 'Holiday', 'Welsh', 'Wilkes']

# server id as key to a tuple of adjacent node servers and port number
SERVER_CONFIG = {}
SERVER_CONFIG['Goloman'] = (['Hands', 'Holiday', 'Wilkes'], 17735)
SERVER_CONFIG['Hands'] = (['Goloman', 'Wilkes'], 17736)
SERVER_CONFIG['Holiday'] = (['Goloman', 'Welsh', 'Wilkes'], 17737)
SERVER_CONFIG['Welsh'] = (['Holiday'], 17738)
SERVER_CONFIG['Wilkes'] = (['Goloman', 'Hands', 'Holiday'], 17739)


API_KEY = 'AIzaSyC-pALbeZ1iks-6xlsC4EQMa72kiOzf-No'
REQUEST_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
