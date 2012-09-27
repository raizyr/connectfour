# Connect Four Code Exercise
*Connect Four® is a trademark of Hasbro.*

An exercise in game solving algorithms using Django.

## Installation

1. Use virtualenv to create an isolated environment  
```
virtualenv --distribute conn4env
```
2. Active new virtualenv  
```
source conn4env/bin/active
```
3. Install Dependencies
  * django `pip install django`
  * numpy `pip install numpy`
  * django-dajaxice `pip install django-dajaxice`
  * django-dajax `pip install django-dajax`
4. Get your own copy of connectfour  
```
git clone https://github.com/raizyr/connectfour.git
```

## Usage
1. Initialize sqlite3 in-memory database (*used for sessions*)  
```
python manage.py syncdb
```
2. Run the development server  
```
python manage.py runserver
```
3. Point your browser to http://localhost:8000/

## Game Modes
Can be played with 0, 1, or 2 human players.  
Difficuty selections include 3 game solving algorithms: *minimax* search, *negamax* search, and *alphabeta* pruning.

The *Normal* difficulty of each algorithm only looks 1 move ahead for the best move, while the *Hard* difficulty looks further ahead.
The *alphabeta* algorithm is the fastest and thus can look further ahead
than the others. 



