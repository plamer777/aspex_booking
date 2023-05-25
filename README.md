# The Aspex-Booking
This application was created as test task for Aspex company.

The app provides functionality as follows:
 - A new user registration by email and password
 - User login and logout
 - Getting a list of all tables available for booking
 - Getting all tables booked by current user
 - Booking chosen table if conditions such as time and persons amount are appropriate
 - Changing booking parameters (time and persons amount)
 - Canceling booking if current time is more than an hour before booking time
 
---

**Technologies used in the project:**
 
 - Fastapi
 - SQLAlchemy 
 - Uvicorn
 - Bcrypt
 - PyJwt
 - Docker
 - Docker-compose

---

**How to start the project:**
To start the app just follow the next steps:
 - Clone the repository
 - Install docker and docker-compose packages by the command `sudo apt install docker.io docker-compose`
 - Create .env file using an example provided below
 - Prepare docker-compose.yaml file (change database name and db username)
 - Start the app by using `sudo docker-compose up -d` command
 - The main page with swagger will be available by the url http://localhost/ (if started locally) or http://yourdomain/ (if started on the server)
 - After that application is ready to process requests

---
Example of .env file:

    POSTGRES_DB=booking - your db name
    POSTGRES_PASSWORD=plamer0805 - db username's password
    POSTGRES_USER=plamer - db username
    POSTGRES_PORT=5432 - db port
    POSTGRES_HOST=db - database host (the name of docker container)
    JWT_SECRET=testing_jwt_secret - secret to generate JWT tokens (should be very strong)
    JWT_ALGO=HS256 - JWT algorithm to generate JWT tokens (can be used by default - SHA256)
    JWT_EXP_HOURS=1 - JWT token expiration (by default an hour)
    TZ_SHIFT=3 - your timezone relative to UTC
    API_TITLE=Aspex-Booking - Fast API title shown in swagger
    API_DESCRIPTION=The test application for Aspex vacancy - description of the application
    API_VERSION=1.0.0 - Version of the application


The project was created by Alexey Mavrin in 25 May 2023