#!/usr/bin/env bash

# This script will undo the last migration and then run the migrations again
# while in development. This is useful when you want to reset the database
# without deleting the database file.
# Author: Maxwell Nana Forson <theLazyProgrammer>

# get redo option from the user as an argument
redo=false
if [[ $1 == "--redo" ]]; then
	redo=true
fi

if [[ -f '.env' ]]; then
	echo "Sourcing .env file..."
	# shellcheck disable=SC1091
	source .env
fi

rm -f db.sqlite3 2>/dev/null

# get all the apps
all_apps=$(./manage.py showmigrations | grep -o '^[a-z]*') || :

# now let's get I created
my_apps=$(
	find . \
		-type d \
		-not -path "./.venv/*" \
		-exec test -f '{}/__init__.py' \; \
		! -exec test -f '{}/settings.py' \; \
		-printf '%P\n' |
		cut -d '/' -f 1 | sort -u
) || :

remove_app_migrations() {
	# remove the migrations for my apps
	for app in ${my_apps}; do
		echo "Removing migrations for ${app}..."
		./manage.py migrate "${app}" zero 2>/dev/null
		rm -rf "${app}/migrations/" 2>/dev/null
	done

}

if [[ ${redo} == true ]]; then
	echo "Redoing migrations..."
	echo "Creating migrations..."
	remove_app_migrations
	# trunk-ignore(shellcheck/SC2250)
	# trunk-ignore(shellcheck/SC2086)
	./manage.py makemigrations $my_apps
	./manage.py migrate
else
	remove_app_migrations
fi

# get django apps only
django_apps=$(echo "${all_apps}" | grep -v -f <(echo "${my_apps[@]}")) || :

# undo migrations for all apps
for app in ${django_apps}; do
	echo "Undoing migrations for ${app}..."
	./manage.py migrate "${app}" zero 2>/dev/null

	rm -rf "${app}/migrations/" 2>/dev/null
done

if [[ ${redo} == true ]]; then
	./manage.py migrate
	# creating super superuser
	echo
	echo "Creating super superuser..."
	./create_superuser.py
	echo "Super User created..."
fi

rm error.log 2>/dev/null
echo "Finished execution successfully"
