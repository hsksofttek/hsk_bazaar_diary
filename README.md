# Business Management System - Web Application

A modern, mobile-friendly web application for business management with multi-user authentication, built with Flask and modern web technologies.

## 🌟 Features

### Core Features
- **Multi-User Authentication**: Secure login system with role-based access control
- **Party Management**: Complete customer and supplier management
- **Item Management**: Product catalog with detailed specifications
- **Purchase Management**: Track all purchase transactions
- **Sales Management**: Complete sales tracking and billing
- **Financial Management**: Cashbook and bankbook tracking
- **Reporting**: Comprehensive business reports and analytics
- **Mobile Responsive**: Optimized for all devices and screen sizes

### Technical Features
- **Modern UI/UX**: Beautiful, colorful interface with smooth animations
- **RESTful API**: Full API support for mobile app integration
- **Real-time Updates**: Live data updates and notifications
- **Data Export**: Export data to Excel and PDF formats
- **Search & Filter**: Advanced search and filtering capabilities
- **Pagination**: Efficient data loading with pagination
- **Security**: Secure authentication with password hashing
- **Database**: SQLite database with SQLAlchemy ORM

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd web_app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python app.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## 📱 Mobile Compatibility

The application is fully optimized for mobile devices:

- **Responsive Design**: Adapts to all screen sizes
- **Touch-Friendly**: Optimized for touch interactions
- **Mobile Navigation**: Collapsible sidebar for mobile
- **Fast Loading**: Optimized for mobile networks
- **PWA Ready**: Can be installed as a mobile app

## 🔐 User Management

### User Roles
- **Admin**: Full access to all features and user management
- **Manager**: Access to business operations and reports
- **User**: Basic access to data entry and viewing

### Authentication Features
- Secure password hashing with bcrypt
- Session management with Flask-Login
- Remember me functionality
- Password reset capabilities
- Account activation/deactivation

## 📊 Business Features

### Party Management
- Add, edit, and delete parties (customers/suppliers)
- Complete contact information
- GST and tax details
- Credit limits and balances
- Transaction history

### Item Management
- Product catalog with categories
- Pricing and tax information
- Stock tracking
- Barcode support
- HSN codes for GST

### Transaction Management
- Purchase orders and bills
- Sales invoices
- Payment tracking
- Discount and tax calculations
- Multiple payment methods

### Financial Tracking
- Cashbook entries
- Bankbook transactions
- Balance calculations
- Financial reports
- Audit trail

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///business_web.db
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=development
```

### Database Configuration
The application uses SQLite by default. For production, you can configure other databases:

```python
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname

# MySQL
DATABASE_URL=mysql://user:password@localhost/dbname
```

## 📡 API Endpoints

### Authentication
- `POST /auth/api/login` - User login
- `POST /auth/api/logout` - User logout
- `GET /auth/api/check-auth` - Check authentication status

### Parties
- `GET /api/parties` - List all parties
- `GET /api/parties/<code>` - Get specific party
- `POST /api/parties` - Create new party
- `PUT /api/parties/<code>` - Update party
- `DELETE /api/parties/<code>` - Delete party

### Items
- `GET /api/items` - List all items
- `GET /api/items/<code>` - Get specific item
- `POST /api/items` - Create new item
- `PUT /api/items/<code>` - Update item
- `DELETE /api/items/<code>` - Delete item

### Transactions
- `GET /api/purchases` - List purchases
- `POST /api/purchases` - Create purchase
- `GET /api/sales` - List sales
- `POST /api/sales` - Create sale

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/search` - Search parties and items

## 🎨 Customization

### Styling
The application uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #f59e0b;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... more colors */
}
```

### Adding New Features
1. Create new models in `models.py`
2. Add forms in `forms.py`
3. Create API endpoints in `api.py`
4. Add routes in `app.py`
5. Create templates in `templates/`

## 🚀 Deployment

### Production Setup
1. Set environment variables for production
2. Use a production WSGI server (Gunicorn)
3. Configure a reverse proxy (Nginx)
4. Set up SSL certificates
5. Configure database backups

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

## 🔒 Security Features

- Password hashing with bcrypt
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure session management
- Input validation and sanitization

## 📈 Performance

- Database query optimization
- Caching support
- Lazy loading for large datasets
- Image optimization
- Minified CSS and JavaScript

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🔄 Updates

### Version 1.0.0
- Initial release
- Basic business management features
- Multi-user authentication
- Mobile-responsive design
- RESTful API

### Planned Features
- Advanced reporting
- Email notifications
- SMS integration
- Barcode scanning
- Mobile app
- Multi-language support
- Advanced analytics
- Inventory alerts

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies** 