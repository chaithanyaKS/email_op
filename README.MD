# Email Operations
Integrate with third party email providers and perform rule based operations on emails

### Prerequisites
1. Make sure [Poetry](https://python-poetry.org/) is installed in your system.
2. Create credentials [credentials](https://developers.google.com/gmail/api/quickstart/python) for interacting with the gmail api and place it in the root of the project with the filename as `credentials.json`.

### Installation

Steps to install the project locally.

1. Clone the repo
```bash
git clone https://github.com/chaithanyaKS/email_op.git
cd email_op
```
2. Install dependencies
```bash
poetry install
```
3. Set the environment variables, see .env-example for list of all the environment variables.

4. Run migrations
```bash
python manage.py migrate
```

5. Start development server
```bash
python manage.py runserver
```

### Loading the data to the database
1. Make sure the migrations are applied to the database.

2. Run the following command to load the data into the database. Due to certain limitations only 10 recent emails are queried and loaded into the database.
```bash
python manage.py load
```    

### Accessing the api
1. Send a POST request to http://localhost/api/email/process/ with the a json file constructed with the rules-example.json.