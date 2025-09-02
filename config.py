from os import environ


debug = environ['DEBUG'] == 'TRUE'
db_url = environ['DB_URL']

db_pool_max_size = 5
