.ONESHELL:
setup:
	virtualenv -p python3.9 manifest
	. manifest/bin/activate
	echo $(which pip3)
	#pip install -r requirements.txt

clean:
	rm -rf manifest

run:
	uvicorn app.main:app --reload





