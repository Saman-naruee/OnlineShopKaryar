# E Commerce Project

## Overview
E Commerce is a Django-based e-commerce platform with a RESTful API. It provides a robust backend for managing products, collections, carts, orders, and customer interactions.

## Key Features
- Product management with detailed information and image support
- Hierarchical product collections using MPTT
- Shopping cart functionality
- Order processing system
- Customer profiles and authentication
- Admin panel for easy management
- RESTful API for frontend integration

## Technical Stack
- Django
- Django REST Framework
- PostgreSQL
- JWT for authentication
- MPTT for hierarchical data

## Main Components
1. Products: Manage product details, pricing, and inventory
2. Collections: Organize products into categories
3. Carts: Handle shopping cart operations
4. Orders: Process and manage customer orders
5. Customers: User profiles and authentication
6. Reviews: Product review system
7. Notifications: User notification system

## API Endpoints
- `/products/`: Product management
- `/collections/`: Product collections
- `/carts/`: Shopping cart operations
- `/customers/`: Customer profile management
- `/orders/`: Order processing
- `/notifications/`: User notifications

## Getting Started

### Prerequisites
- Python 3.x
- pip
- PostgreSQL

### Clone the Repository
To get started with the E Commerce project, clone the repository to your local machine:

```bash
git clone https://github.com/Saman-naruee/OnlineShopKaryar.git
```
```bash
cd OnlineShopKaryar
```

### Settup a virtual environment
```bash
python -m venv venv
```
```bash
source venv/bin/activate
```

### Installl Dependencies
Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```
### Database Setup
Set up the PostgreSQL database and update the database settings in the settings.py file.

## Environment Variables:
Create a .env file in the root directory and add the following variables:
```PlainText
SECRET_KEY=your_secret_key
DATABASE=your_database_name
USER=your_database_user
PASSWORD=your_database_password
HOST=your_database_host
PORT=your_database_port
```

### Run  Migrations:
Apply the database migrations:
```bash
python manage.py makemigrations
```
```bash
python  manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run the Development Server
```bash
python manage.py runserver
```

### More info:
The application is now running at :
```url
http://localhost:8000.
```

Access the admin panel at :
```url
http://localhost:8000/admin.
```

### Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

Contributions to the E Commerce project are welcome! Please follow these steps:

    1.fork the repository.
    2.Create a new branch for your feature or bug fix.
    3.Make your changes and commit them with descriptive commit messages.
    4.Push your changes to your forked repository.
    5.Submit a pull request to the main repository.
    6.Provide a clear description of your changes and why they should be merged.
    7.Your pull request will be reviewed, and if everything looks good, it will be merged into the main project.

