# ona-download

### Setup steps
* python setup.py sdist
* python setup.py install
* python setup.py sdist bdist_wheel
* pip install -r requirements.txt
* python -m PyInstaller main.py
* python -m PyInstaller .\main.py --onefile