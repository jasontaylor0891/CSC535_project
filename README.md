How to run project:

Download and install Docker desktop.
https://www.docker.com/products/docker-desktop

Clone project from github.

git clone -b <branch_name> https://github.com/jasontaylor0891/CSC535_project.git

Change to the project directoty and run. (this is the folder where docker-compose.yml is located)

docker-compose up --build

Verify the database created on your computer is the same as in app.py

Run:
  docker ps 

Review the name for the database container.  If you need to change the database name in the application stop the application in docker desktop or from the command window hit Control-C a few times.  You may need to delete the application in docker.

You should see something similar to CSC535_project_db_1.  If you have something different you will need to update the database host in app/app.py (Line 22).

app.config['MYSQL_HOST'] = 'CHANGE_TO_YOUR_DB_NAME_db_1'

To access the mssql on the mysql docker use:

docker exec -it CHANGE_TO_YOUR_DB_NAME_db_1 mysql -ucsc535 -p

This will provide command line access to the MYSQL database.

Access the web application use the url: http://localhost:8000/
