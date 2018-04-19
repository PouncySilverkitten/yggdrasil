# yggdrasil
![Build Badge](https://travis-ci.org/PouncySilverkitten/yggdrasil.svg?branch=master)
![Coverage Badge](coverage.svg)

The Yggdrasil Project is a (now unmaintained) suite of bots for the chat platform Heim, located at euphoria.io. It is comprised of the below parts.

## Heimdall
![Pylint Badge](data/heimdall/heimdall.svg)
Heimdall is a message logging and statistics generation bot. It can be invoked using the following commands:
- !stats (@user)
- !rank (@user|number)
- !roomstats

## Hermothr
![Pylint Badge](data/hermothr/hermothr.svg)
Hermothr is a message-delivery bot. It's designed to facilitate async messages across a longer timescale. It is invoked with the following commands:
- !(herm|hermothr|nnotify|notify) (@user|\*group) message
There is a known bug which causes it to silently fail to save messages when being run using the Forseti database mediator.

## Forseti
![Pylint Badge](data/forseti/forseti.svg)
Forseti is a database mediation library. It's used by yggdrasil.py to facilitate writing to a single database by multiple processes. When yggdrasil.py spawns Heimdall and Hermothr in multiple rooms, each instance of the bot is given a Queue which Forseti listens to. Using WAL, this enables the use of a single database file.

## Loki
![Pylint Badge](data/loki/loki.svg)

## Setup
`git clone https://github.com/pouncysilverkitten/yggdrasil/`
`cd yggdrasil`
`pip install pipenv`
`pipenv install`
`pipenv run python yggdrasil.py & disown`
Heimdall will automatically create a database and collate messages to it if no database is found; while doing so it remains in 'stealth' mode; i.e. not visible on the nicklist. Once a full set of messages for the room has been downloaded and processed, it will automatically connect.
