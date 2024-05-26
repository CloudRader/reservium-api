# Buk Reservation System


## Description of web application

This is a reservation system that allows you to reserve a club room from the **Buben Student Club**. It automates the reservation process and simplifies the process for both the manager and the reservationist. The application communicates with the student information system IS, which takes the data needed for booking about users and adds the created event to Google calendar.

The basic framework I used is FastAPI for building APIs with Python based on standard Python type hints. My app is only backend, the fronend which is also used on our server is written by my colleague from the club. His repository can be found at this [link](https://github.com/daniilk11/react-reservation-system).

All the dependencies I use are in the environment-dev.yml file.

## Documentation on my app can be found on this link https://rezervace.buk.cvut.cz:8000/docs#


## How to run the application 🛫


### Run using our **server**
A container with the actual application code is running on the club's server.
Other ways to run it are problematic because you need to authorize your specific IP so you can run the code on your localhost, keep in mind, you must be logged in to IS to use our reservation app.

> 1) go to https://rezervace.buk.cvut.cz:80
> 2) enjoy the app ✨ 


### Run using **docker**
Unfortunately it is possible only if you are registered on IS, also your IP address is added to the authorized applications there and you you're inside our network.

> 1) run `$ docker compose up`
> 2) after docker compose finishes and runs up containers, go to https://{your IP address}:8000/
> 3) enjoy the app ✨ 
> 4) run `$ docker compose exec backend bash`
> 5) run `$ source /venv/bin/activate` to activate virtual environment
> 6) run `$ cd app/`
> 7) run `$ ./scripts/run_tests.sh` to run tests.
> 8) run `$ ./scripts/pylint.sh` to run pylinter.
> 9) run `$ ./scripts/mypy.sh` to run mypy.


### Run using **conda** 🐍:
Unfortunately it is possible only if you are registered on IS, also your IP address is added to the authorized applications there and you you're inside our network.

Installing conda:

> 1) Follow official installation guide  https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
> 2) It is recommended to install Miniconda, because it will take less disk space.

Running using conda:

> 1) using conda install conda-lock package, running `$ conda install conda-lock` 
> 2) in the project root run `$ ./scripts/create_or_update_env.sh` to create buk-reservation environment to run the
     application
> 3) run `$ conda activate buk-reservation` to activate new installed environment
> 4) run `$ docker compose up db` to run postgresql database
> 5) run `$ cd app/app/` and then `$ python -m main` to start application
> 6) go to https://{your IP address}:8000/ and enjoy the app ✨
> 7) run `$ cd ../` and then `$ ./scripts/run_tests.sh -c` to run tests with coverage.
> 8) run `$ ./scripts/pylint.sh` to run pylinter.
> 9) run `$ ./scripts/mypy.sh` to run mypy.


## Pylint

I use pylint to check quality of my code. There is a script to run pylint on the whole codebase.
To run it just run the script:

```shell
 $ cd app/
 $ ./scripts/pylint.sh
```

## Mypy

I use mypy as static type checker for Python. There is a script to run mypy on the whole codebase.
To run it just run the script:

```shell
 $ cd app/
 $ ./scripts/mypy.sh
```

## Pytest

I use pytest as testing framework. There is a script to run pytest on the whole codebase.
To run it just run the script:

```shell
 $ cd app/
 $ ./scripts/run_tests.sh
```
