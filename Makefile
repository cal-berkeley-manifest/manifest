.ONESHELL:

setup: check-env
	virtualenv -p python3.9 env
	. env/bin/activate
	which pip3
	#pip install -r requirements.txt

check-env:
ifndef MONGODB_URL
	$(warning Set the environmental variable MONGODB_URL with the following command:)
	$(warning export MONGODB_URL="mongodb+srv://<username>:<password>@<db_subdomain>.mongodb.net/?retryWrites=true&w=majority")
	$(error MONGODB_URL is not defined)
endif

run:
	uvicorn main:app --reload

clean:
	rm -rf env