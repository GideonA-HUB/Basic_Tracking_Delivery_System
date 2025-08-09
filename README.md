# Meridian Asset Logistics - Delivery Tracking Platform

A comprehensive Django REST Framework-based delivery tracking system that allows businesses to generate and share secure live tracking links with customers without requiring registration or login.

## Features

### Backend (Django REST Framework)
- **Secure Tracking Links**: Generate unique, expirable tracking links for each delivery
- **Real-time Status Updates**: Live delivery status tracking with timestamps
- **RESTful API**: Complete API for delivery management and tracking
- **Admin Interface**: Django admin for managing deliveries and status updates
- **Database Support**: SQLite (default) or PostgreSQL support

### Frontend (Modern Web Interface)
- **Responsive Design**: Mobile-friendly interface using Tailwind CSS
- **Real-time Updates**: Auto-refresh tracking information every 30 seconds
- **Modern UI/UX**: Clean, professional interface with intuitive navigation
- **No Login Required**: Customers can track deliveries using only the tracking link

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Tracking_Platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Dashboard: http://localhost:8000/
   - Admin Interface: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/api/

## API Endpoints

### Delivery Management

#### Create Delivery
```http
POST /api/deliveries/
Content-Type: application/json

{
    "order_number": "ORD-2024-001",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1 (555) 123-4567",
    "pickup_address": "123 Warehouse St, City, State 12345",
    "delivery_address": "456 Customer Ave, City, State 12345",
    "package_description": "Electronics package",
    "package_weight": 2.5,
    "package_dimensions": "30x20x15 cm",
    "estimated_delivery": "2024-01-15T14:00:00Z"
}
```

#### Get All Deliveries
```http
GET /api/deliveries/
```

#### Get Delivery Details
```http
GET /api/deliveries/{id}/
```

#### Update Delivery Status
```http
POST /api/deliveries/{id}/update_status/
Content-Type: application/json

{
    "status": "in_transit",
    "location": "Distribution Center",
    "description": "Package picked up and in transit"
}
```

### Public Tracking

#### Track Delivery (Public)
```http
GET /api/track/{tracking_number}/{tracking_secret}/
```

### Search and Statistics

#### Search Deliveries
```http
GET /api/search/?q=search_term&status=pending
```

#### Get Statistics
```http
GET /api/stats/
```

## Frontend Usage

### Dashboard
- View all deliveries with status indicators
- Update delivery statuses in real-time
- Access delivery statistics

### Create Delivery
- Fill out delivery form with customer and package information
- Automatically generates tracking number and secure link
- Copy tracking link to share with customer

### Customer Tracking Page
- Access via tracking link: `/track/{tracking_number}/{tracking_secret}/`
- Real-time status updates with timeline
- Mobile-responsive design
- No login required

## Database Models

### Delivery
- `order_number`: Unique order identifier
- `tracking_number`: Auto-generated tracking number
- `tracking_secret`: Secure secret for tracking link
- `customer_name`, `customer_email`, `customer_phone`: Customer information
- `pickup_address`, `delivery_address`: Address information
- `package_description`, `package_weight`, `package_dimensions`: Package details
- `current_status`: Current delivery status
- `estimated_delivery`, `actual_delivery`: Delivery timestamps
- `tracking_link_expires`: Link expiration date

### DeliveryStatus
- `delivery`: Foreign key to Delivery
- `status`: Status update (pending, confirmed, in_transit, etc.)
- `location`: Optional location information
- `description`: Status description
- `timestamp`: When the status was updated

## Status Types

- `pending`: Order received and pending confirmation
- `confirmed`: Order confirmed and ready for shipping
- `in_transit`: Package is in transit
- `out_for_delivery`: Package is out for delivery
- `delivered`: Package successfully delivered
- `failed`: Delivery attempt failed
- `returned`: Package returned

## Security Features

- **Secure Tracking Links**: Each delivery gets a unique tracking number and secret
- **Expirable Links**: Tracking links expire after 30 days (configurable)
- **No Authentication Required**: Customers can track without accounts
- **CORS Enabled**: Cross-origin requests allowed for API access

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TRACKING_LINK_EXPIRY_DAYS=30
TRACKING_LINK_SECRET_LENGTH=32
```

### Database Configuration
The default configuration uses SQLite. For PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'delivery_tracker',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Set up static file serving
5. Configure HTTPS

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on the repository.
