#!/bin/bash
docker-compose exec db mongo creepy --eval "db.tiles.drop()"

