# SideQuest API
I am not great at writing. I will need someone else to rewrite it better

## How to run
This is *unix setup only (at least for now). It works Windows to, but you will have to find the ways to set it up by yourself.

* First make sure you have Python 3.9 and PostgreSQL installed on your machine
* Make sure PostgreSQL is running
* clone the project
* go to the directory where `init.sh` is
* run the following command `sudo chmod +x init.sh` -> pretty much give execution persmission, so you can run it
* run the following command `./init.sh` -> this script will setup up everything (it should work; i couldn't test it because the project was already set it up on my machine manually)
* if everything went well `python manage.py runserver` will run the project

## Also I included flake8 as a hook in .git/hooks, so code can't be commited if it doesn't follow flake8. good luck 😈


### Have fun!!!!
