How to run project:

Download and install Docker desktop.
https://www.docker.com/products/docker-desktop

Clone project from github.

Create branch from Main.  

git clone -b <branch_name> https://github.com/jasontaylor0891/CSC535_project.git

Change to the project directoty and run. (this is the folder where docker-compose.yml is located)

To run the application in production mode run:

  docker-compose up --build

To run the application in development mode run:

  docker-compose -f docker-compose-dev.yml up --build

To run the application in testing mode run:

  docker-compose -f docker-compose-test.yml up --build

Verify the database created on your computer is the same as in the docker compose file.

Run:
  docker ps 

Review the name for the database container.  If you need to change the database name in the application stop the application in docker desktop or from the command window hit Control-C a few times.  You may need to delete the application in docker.

You should see something similar to CSC535_project_db_1.  If you have something different you will need to update the database host in the docker compose for the selcted configuration. Line 12.

Production:
  MYSQL_HOST: 'CHANGE_TO_YOUR_DB_NAME_db_1'

Development:
  DEV_MYSQL_HOST: 'CHANGE_TO_YOUR_DB_NAME_db_1'

Testing:
  TEST_MYSQL_HOST: 'CHANGE_TO_YOUR_DB_NAME_db_1'

To access the mssql on the mysql docker use:

docker exec -it CHANGE_TO_YOUR_DB_NAME_db_1 mysql -ucsc535 -p

This will provide command line access to the MYSQL database.

Access the web application use the url: http://localhost:8000/
