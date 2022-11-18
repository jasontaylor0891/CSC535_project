# Class Project for CSC535 - Reminder Application

Class project for Advanced Software Engineering CSC535 - Section 01 


## Authors

- [@jasontaylor0891](https://www.github.com/jasontaylor0891)
- [@KunaK10](https://www.github.com/KunaK10)
- [@romibarde](https://www.github.com/romibarde)
- [@vinaydeep26](https://www.github.com/vinaydeep26)



## Installation

Install project

```bash
  git clone -b <branch_name> https://github.com/jasontaylor0891/CSC535_project.git
  cd CSC535_project
```
    
## Deployment

To deploy this project in production mode run:

```bash
  docker-compose up --build
```

To deploy this project in development mode run:

```bash
  docker-compose -f docker-compose-dev.yml up --build
```

To deploy this project in testing mode run:

```bash
  docker-compose -f docker-compose-test.yml up --build
```


## Local Database Access

```bash
  docker exec -it csc535_project_db_1 mysql -ucsc535 -p
```
## Website Access

http://localhost:8000/
