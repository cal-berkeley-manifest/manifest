.ONESHELL:
setup:
	virtualenv -p python3.9 env
	. env/bin/activate
	which pip3
	#pip install -r requirements.txt

run:
	uvicorn main:app --reload

clean:
	rm -rf env






