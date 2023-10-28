## Step 4
The directory `DBDefinitions` has been added. 
This directory contains code related to persistence models.
As the ORM sqlalchemy is used.

In this step all code is in files 
- `DBDefinitions.__init__.py`
- `DBDefinitions.uuid.py`
- `DBDefinitions.baseDBModel.py`
- `DBDefinitions.eventDBModel.py`

also `main.py` has been changed.

It must solve this problems:

### uuid

It is quite common to use uuid as a primary key for newly created databases. 
It has many advantages in comparison to int primary keys.
To cover usgae of uuid in this code there is `uuid.py` file with few self explaining lines.
It also serves as a layer for future changes.

### database structure definition

SQLAlchemy needs a parent class for all models. 
This has been fullfilled by declaration of `BaseModel` class in file `baseDBModel.py`.
This class is imported in file `eventDBModel.py`. 
There is also defined class `EventModel` which is inherited from `BaseModel`.

Attribute `EventModel.__tablename__` contains table name used (and created) in database.
Other class attributes (`EventModel.id` and `EventModel.name`) repesents attributes of table records.

Structure is prepared for large databases. 
It is expected that all tables and its appropriate models are defined in separate files.

### database connection

Database connection is defined by connection string. 
This is very common for most programming languages.
Connection string contains type od connection (driver), hostname, port, username, password and database name.
You should look at `ComposeConnectionString` function in `__init__.py`.
This function tries to get connection string parts from environment variables.
If environment variables are not defined, there are default values.

In `__init__.py` is defined function `startEngine` which returns asynchronous session maker.
This should be used for sending statements to database server.

For experiments postgres database is recommended (and connection string is designed for this).
Postgres can be instaled as docker image see https://hub.docker.com/_/postgres .
**Be sure that instalation has appropriate database installed (created).**
For postgres management pgadmin can works well, see https://hub.docker.com/r/dpage/pgadmin4 .
Do not forget map ports so they will be available for localhost (postgres has 5432).

### application init

`main.py` inits FastAPI in way where `initEngine` is executed at application start.
It has been made to recreate related database structure (database table `events`).
This database table is dropped and created on each application start.
This leads to always empty `events` table.

### conclusion
After run of application throught pgadmin state of database can be checked.

The GraphQL endpoint is still available at
http://localhost:8000/gql


but the endpoint does not offer new functionality.