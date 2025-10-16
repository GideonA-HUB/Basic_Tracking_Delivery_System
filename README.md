# Meridian Asset Logistics - VIP Dashboard System

A comprehensive Django-based web application for managing VIP customer accounts, financial services, and support ticket systems.

## 🚀 Features

### VIP Dashboard System
- **Dashboard Overview**: Complete financial overview with balance, income, outgoing, and transaction limits
- **User Profile Management**: VIP member profiles with KYC verification and member IDs
- **Real-time Data Display**: Live balance updates and transaction monitoring

### Financial Services
- **Transaction Management**: Complete transaction history and monitoring
- **Virtual Cards**: Card application, management, and balance tracking
- **Local Transfers**: Domestic money transfer functionality
- **International Wire Transfers**: Global money transfer with multiple payment methods
- **Deposit Services**: Multiple deposit methods including USDT, Bank Transfer, PayPal, Bitcoin
- **Loan Services**: Loan applications, history, and FAQ management
- **IRS Tax Refund**: Tax refund application and status tracking

### Support System
- **Support Ticket System**: Complete ticket management with priority levels and categories
- **Admin Management**: Full Django admin interface for ticket monitoring
- **Response Tracking**: 24-hour response time tracking and status updates

### Account Management
- **Account Settings**: Comprehensive profile and security settings
- **KYC Verification**: Identity verification system
- **Security Features**: Two-factor authentication, transaction PINs, and limits

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, Django 4.2+, Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, TailwindCSS, JavaScript
- **Deployment**: Railway.app (configured with Procfile and railway.json)
- **Admin Interface**: Django Admin with custom configurations

## 📁 Project Structure

```
Basic_Tracking_Delivery_System/
├── accounts/
│   ├── models.py          # User profiles, transactions, support tickets
│   ├── views.py           # VIP dashboard views and functionality
│   ├── forms.py           # Django forms for all features
│   ├── admin.py           # Custom admin configurations
│   ├── urls.py            # URL routing
│   └── migrations/        # Database migrations
├── templates/
│   └── accounts/
│       ├── vip_dashboard.html
│       ├── vip_transactions.html
│       ├── vip_cards.html
│       ├── vip_support_ticket.html
│       ├── vip_account_settings.html
│       └── [other VIP pages]
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── railway.json          # Railway app configuration
├── runtime.txt           # Python version specification
└── README.md            # This file
```

## 🗄️ Database Models

### Core Models
- **VIPProfile**: VIP member information and status
- **Transaction**: Financial transaction records
- **Card**: Virtual card management
- **SupportTicket**: Support ticket system with priority and status tracking

### Service Models
- **LocalTransfer**: Domestic transfer records
- **InternationalTransfer**: International transfer with multiple methods
- **Deposit**: Deposit transaction records
- **Loan**: Loan application and management
- **LoanApplication**: Detailed loan applications
- **IRSTaxRefund**: Tax refund applications

### Configuration Models
- **AccountSettings**: User preferences and security settings
- **RecentActivity**: Activity tracking and notifications

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Basic_Tracking_Delivery_System
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Create a `.env` file with the following variables:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## 🚀 Deployment (Railway.app)

The application is configured for deployment on Railway.app:

1. **Connect your GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically** - Railway will use the Procfile and railway.json

### Railway Configuration
- **Procfile**: `web: python manage.py runserver 0.0.0.0:$PORT`
- **runtime.txt**: Specifies Python version
- **railway.json**: App configuration and build settings

## 👥 User Management

### VIP Member Features
- **Dashboard Access**: Complete financial overview
- **Transaction History**: Detailed transaction records
- **Card Management**: Virtual card applications and management
- **Transfer Services**: Local and international transfers
- **Support System**: Ticket submission and tracking
- **Account Settings**: Profile and security management

### Admin Features
- **User Management**: Complete user profile administration
- **Transaction Monitoring**: Real-time transaction oversight
- **Support Ticket Management**: Priority-based ticket handling
- **Financial Services**: Loan and transfer approval workflows
- **System Configuration**: Settings and preferences management

## 📊 Support Ticket System

### Features
- **Priority Levels**: Low, Medium, High, Urgent
- **Categories**: General, Technical, Account, Billing, Transaction, Security, Feature Request, Other
- **Status Tracking**: Open, In Progress, Waiting for Customer, Resolved, Closed
- **Auto-numbering**: Unique ticket numbers (ST-XXXXXXXX format)
- **Response Tracking**: 24-hour response time commitment

### Admin Actions
- Mark tickets as resolved/closed
- Set priority levels
- Add internal notes
- Monitor response times

## 🔧 API Endpoints

### VIP Dashboard Routes
- `/accounts/vip/dashboard/` - Main VIP dashboard
- `/accounts/vip/transactions/` - Transaction history
- `/accounts/vip/cards/` - Virtual cards management
- `/accounts/vip/support-ticket/` - Support ticket system
- `/accounts/vip/account-settings/` - Account settings

### Financial Services
- `/accounts/vip/transfer/local/` - Local transfers
- `/accounts/vip/transfer/international/` - International transfers
- `/accounts/vip/deposit/` - Deposit services
- `/accounts/vip/loan-services/` - Loan applications

## 🎨 Frontend Features

### Design System
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **Dark/Light Themes**: Automatic theme detection and switching
- **Custom Components**: Reusable UI components
- **Independent Scrolling**: Sidebar and main content scroll independently

### User Interface
- **Dashboard Layout**: Fixed sidebar with scrollable main content
- **Form Validation**: Client-side and server-side validation
- **Loading States**: User feedback during operations
- **Error Handling**: Comprehensive error messages and recovery

## 🔐 Security Features

### Authentication & Authorization
- **VIP Member Verification**: Exclusive access control
- **Session Management**: Secure user sessions
- **CSRF Protection**: Cross-site request forgery protection

### Data Protection
- **Input Validation**: Comprehensive form validation
- **SQL Injection Prevention**: Django ORM protection
- **XSS Protection**: Content Security Policy implementation

## 📈 Performance Optimization

### Database Optimization
- **Query Optimization**: Efficient database queries
- **Indexing**: Strategic database indexing
- **Caching**: Django caching framework

### Frontend Optimization
- **Asset Minification**: Optimized CSS and JavaScript
- **Image Optimization**: Compressed images and icons
- **Lazy Loading**: On-demand content loading

## 🧪 Testing

### Test Coverage
- **Model Tests**: Database model validation
- **View Tests**: HTTP response testing
- **Form Tests**: Form validation testing
- **Integration Tests**: End-to-end functionality

### Running Tests
```bash
python manage.py test
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software owned by Meridian Asset Logistics.

## 🆘 Support

For technical support or questions:
- **Email**: support@meridianassetlogistics.com
- **Support Portal**: Use the built-in support ticket system
- **Documentation**: Refer to this README and inline code comments

## 🔄 Version History

### v1.0.0 (Current)
- Complete VIP dashboard system
- Support ticket management
- Financial services integration
- Account management features
- Django admin customization
- Railway.app deployment configuration

---

**Meridian Asset Logistics** - Empowering VIP financial services with cutting-edge technology.