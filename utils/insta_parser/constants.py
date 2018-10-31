from os import path


BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
ARCHIVES_DIR = path.join(BASE_DIR, 'archives')
INSTAGRAM_URL = "https://www.instagram.com"
NEXT_PAGE_URL = '/graphql/query/?query_hash={query_hash}&variables={variables}'
QUERY_PARAMETERS = '{{"id":"{user_id}","first":12,"after":"{end_cursor}"}}'
QUERY_HASH = 'a5164aed103f24b03e7b7747a2d94e3c'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/65.0.3325.181 Safari/537.36"
