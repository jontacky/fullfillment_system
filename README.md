# Fulfillment System

## Overview
This Django-based fulfillment system manages inventory and processes orders for a logistics company. It allows you to initialize a product catalog, restock inventory, and handle incoming orders, ensuring that no shipment exceeds the maximum weight.

## Features
- Initialize product catalog via `init_catalog`
- Process restocking of inventory via `process_restock`
- Handle incoming orders via `process_order`
- Automatically handle partial fulfillment and deferred shipping due to insufficient inventory

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/jontacky/fulfillment_system.git
    cd fulfillment_system
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure your PostgreSQL database**:
    Edit `fulfillment_system/settings.py` with your database credentials.

4. **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

5. **Create Superuser for Admin**:
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the Server**:
    ```bash
    python manage.py runserver
    ```

7. **Access the Admin Panel**:
    Visit `http://127.0.0.1:8000/admin` to add products and manage inventory.

## Usage

### Endpoints:
1. **Initialize Catalog**:
    - **POST** `/inventory/init_catalog/`
    - **Body**: JSON Array of products with `mass_g` and `product_name`.

2. **Process Restock**:
    - **POST** `/inventory/process_restock/`
    - **Body**: JSON Array of `product_id` and `quantity`.

3. **Process Order**:
    - **POST** `/inventory/process_order/`
    - **Body**: JSON Object with `requested` items (array of `product_id` and `quantity`).

## Running Tests
Run unit tests to validate the system:
```bash
python manage.py test inventory
```


# Production Readiness Steps for Fulfillment System

## 1. Database Optimization
   - **Optimize Queries**: Use `select_related` and `prefetch_related` to reduce database hits, especially for related data in queries.
   - **Indexes**: Add indexes to frequently queried fields (e.g., `product_id` in the `Inventory` table) for faster lookups.
   - **Connection Pooling**: Implement connection pooling using tools like `pgbouncer` for PostgreSQL to efficiently manage database connections.

## 2. Caching
   - **Implement Redis or Memcached**: Cache frequently accessed data (e.g., product catalog, inventory counts) to reduce load on the database.
   - **Django Cache Framework**: Configure Django’s caching system to store and retrieve cached data from Redis or Memcached.

## 3. Asynchronous Processing
   - **Celery**: Use Celery with Redis or RabbitMQ as the message broker to handle background tasks like order processing and large restocks.
   - **Task Offloading**: Offload intensive tasks to Celery to reduce response times and improve scalability.

## 4. Error Monitoring and Logging
   - **Configure Logging**: Set up logging in Django for tracking errors, debug information, and general transaction data.
   - **Error Monitoring Tools**: Use tools like **Sentry** or **Rollbar** for real-time error tracking, notifications, and analytics.

## 5. Security Enhancements
   - **Environment Variables**: Store sensitive data (e.g., database credentials, secret keys) in a `.env` file and load them using `django-environ`.
   - **HTTPS and SSL**: Enable SSL for secure data transmission. Use services like **Let's Encrypt** or **AWS Certificate Manager** to manage certificates.
   - **CORS (Cross-Origin Resource Sharing)**: Limit CORS access to trusted domains using the `django-cors-headers` package.
   - **Security Headers**: Add headers such as `X-Content-Type-Options`, `X-Frame-Options`, and `Content-Security-Policy` for enhanced security.

## 6. Load Balancing and Auto-scaling
   - **Horizontal Scaling**: Use a load balancer (e.g., **Nginx**, **AWS ELB**) to distribute traffic across multiple instances.
   - **Containerization**: Dockerize the application for easy replication and scalability.
   - **Auto-scaling**: Set up auto-scaling on cloud providers like **AWS EC2** or through **Kubernetes** to automatically adjust resources based on traffic.

## 7. Use Gunicorn and Nginx
   - **Gunicorn**: Use Gunicorn as the WSGI server for handling concurrent requests.
   - **Nginx**: Set up Nginx as a reverse proxy to manage traffic, serve static files, and route requests to Gunicorn.

## 8. Health Checks and Observability
   - **Health Checks**: Add a health check endpoint (e.g., `/health`) to verify the status of the application and database.
   - **Monitoring and Metrics**: Use monitoring tools like **Prometheus** or **DataDog** to track system performance, response times, and error rates. Visualize metrics with **Grafana** for detailed insights.

## 9. Backup and Disaster Recovery
   - **Database Backups**: Schedule regular PostgreSQL database backups and store them securely, such as in **AWS S3**.
   - **Configuration Backups**: Use version control for code and automate backup processes for critical configurations and environment files.

## 10. Documentation and Maintainability
   - **API Documentation**: Use **Swagger** or **Django REST framework's built-in documentation** to generate API documentation for endpoints, parameters, and responses.
   - **Automated Testing and CI/CD**: Implement CI/CD pipelines (using **GitHub Actions**, **CircleCI**, or **Jenkins**) for automated testing, linting, and deployment.

