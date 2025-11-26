Test Account
- username: admin
- password: admin123

Take note: in the test account there is only 5 kinder student and there only data inputed is in the AP subject. So to test you can browse the AP subject or add additional data to it.

Requirments:
Python 3.12.1

to run this follow the following command:
> .venv\Scripts\activate
> flask run

If the .venv\Scripts\activate is not working try this:
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt

Error:
(.venv) PS C:\Users\HP\Desktop\My Projects\Final Project CS50x> flask run
 * Serving Flask app 'app'
 * Debug mode: on
An attempt was made to access a socket in a way forbidden by its access permissions

Fix: flask run --port=5001 [Just change the port that is available]


Nov 26 2025 Installation I did on mac:
> Make sure there is a Python installed to the system
> rm -rf venv
> python3 -m venv venv
> source venv/bin/activate
> pip install --upgrade pip
> pip install -r requirements.txt
> flask run