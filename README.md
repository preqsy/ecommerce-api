# E-commerce API

This project is an e-commerce API designed to manage user carts, including adding products, viewing cart items, and calculating the total cart amount. It integrates product management, user authentication, and cart operations to provide a seamless shopping experience.

## Features

- **Cart Management**: Add products to the cart, view cart items, and calculate the total cart amount.
- **User Authentication**: JWT-based user authentication and authorization.
- **Product Management**: CRUD operations for products.
- **Data Validation**: Pydantic models for robust data validation.
- **Database Interaction**: SQLAlchemy for ORM and PostgreSQL as the database.
- **Payment Integration**: Paystack for handling payments.
- **Caching**: Redis for caching and background tasks.

## Technologies Used

- **FastAPI**: For building RESTful API endpoints.
- **Pydantic**: For data validation and settings management.
- **SQLAlchemy**: ORM for database modeling and interaction.
- **PostgreSQL**: Database management.
- **Docker**: For containerizing the application.
- **JWT**: For user authentication and authorization.
- **pytest**: For automated testing.
- **Poetry**: For dependency management.
- **Git**: For version control.
- **Asynchronous Programming**: For enhancing API performance with FastAPI.
- **Redis**: For caching and background tasks.
- **Paystack**: For payment processing.

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker (optional, for containerization)
- Paystack account for payment processing

## API Documentation

For detailed API endpoints and how to use them, you can download the Postman collection:

[Download Postman Collection](https://github.com/preqsy/ecommerce-api/raw/main/ecommerce.postman_collections.json)

### Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/preqsy/ecommerce-api.git
   cd ecommerce-api
   ```

2. **Install Poetry**:
   Follow the instructions at [Poetry's official documentation](https://python-poetry.org/docs/#installation) to install Poetry.

3. **Install dependencies**:

   ```sh
   poetry install
   ```

4. **Set up the database**:
   Create a PostgreSQL database and configure the connection in the `.env` file.

   ```
    SQLALCHEMY_DATABASE_URL=your_database_url
   ```

5. **Configure Paystack**:
   Add your Paystack public and secret keys to the `.env` file:

   ```
   PAYSTACK_PUBLIC_KEY=your_public_key
   PAYSTACK_SECRET_KEY=your_secret_key
   ```

6. **Run database migrations**:

   ```sh
   poetry run alembic upgrade head
   ```

7. **Start the application**:
   ```sh
   uvicorn main:app --reload
   ```

### Running Tests

To ensure the API functions correctly, we have implemented tests using `pytest`.

1. **Install `pytest`**:

   ```sh
   poetry add pytest --dev
   ```

2. **Run the tests**:
   ```sh
   poetry run pytest tests/
   ```

### Running with Docker

1. **Build the Docker image**:

   ```sh
   docker build -t ecommerce-api .
   ```

2. **Run the Docker container**:

   ```sh
   docker run --name ecommerce-api -p 8000:8000 --env-file .env ecommerce-api
   ```

3. **Access the application**:
   The application will be available at `http://localhost:8000`.

## Project Structure

```
ecommerce-api/
├── alembic/                # Database migrations
├── core/                   # Core functionalities and settings
├── crud/                   # CRUD functionalities
├── endpoints/              # API endpoints
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── tests/                  # Test cases
├── task_queue/             # Background Services Functionality
├── .env                    # Environment variables
├── main.py                 # Entry point of the application
├── pyproject.toml          # Poetry configuration file
├── Dockerfile              # Docker configuration
└── README.md               # Project documentation
```

## Contribution

Contributions are welcome! Please create a pull request or raise an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License.

## Contact

For more information, please contact [obbyprecious24@gmail.com](mailto:obbyprecious24@gmail.com).
