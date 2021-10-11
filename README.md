# Monochrome
Monochrome's API, implemented with a PostgreSQL backend and FS image storage.

## Usage
### Docker
This service is available on ghcr.io:
```shell
docker pull ghcr.io/monochromeCMS/monochrome-api-postgres:latest
```
A Makefile is included for the initial setup of the database:
```shell
make DB_URL=... install
```
Once done, the image can be launched with the required [env. vars](#environment-variables):
```shell
docker run -p 3000:3000                                             \
  -e DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres \
  -e JWT_SECRET_KEY=changeMe                                        \
  -v "$(pwd)/media:/media"                                          \
  ghcr.io/monochromeCMS/monochrome-api-postgres:latest
```
*The images will be saved in the media_path, so a volume is highly recommended.*
### Native
Even though Docker is the recommended method,
a virtual environment can also be used after cloning this repository:
```shell
pip install pipenv
pipenv shell
pipenv install

export DB_URL=...
export JWT_SECRET_KEY=...
export MEDIA_PATH=../media
export TEMP_PATH=../temp

make native-install

hypercorn api.main:app -b 0.0.0.0:3000
```

### Environment variables
```python
# URL to the Postgres database, ex: postgresql+asyncpg://username:password@db:5432/name
DB_URL
# Comma-separated list of origins to allow for CORS, namely the origin of your frontend
CORS_ORIGINS = ""

# Secret used to sign the JWT
JWT_SECRET_KEY
# Algorithm used to sign the JWT
JWT_ALGORITHM = "HS256"
# Amount of minutes a JWT will be valid for
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Path where the images will be stored
MEDIA_PATH = "/media"
# Path where temporary data will be stored
TEMP_PATH = "/temp"

# For pagination, the maximum of elements per request, has to be positive
MAX_PAGE_LIMIT = 50
```

## Testing
- `make test` Launches the tests

## Tools used
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic

## Progress
* Creation 🟢100% (new features can always be added)
* Documentation 🟡58%
* OpenAPI 🟡66%
* Cleaner code 🟡50%
* Testing 🟠40%
* Unit 🟢100%
* Integration 🔴10%
  
Credits:
* Base API template: https://github.com/grillazz/fastapi-sqlalchemy-asyncpg
