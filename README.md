# Blog Application

A Flask-based blog application with robust form validation, user authentication, and blog post management.

## Features

### User Management
- User registration with validation
- Secure login system
- User profile management
- Role-based access control

### Blog Post Management
- Create, read, update, and delete blog posts
- Blog post categorization
- Draft/Published/Private post status
- Like/Dislike functionality
- Comments system

### Form Validation

#### Registration Requirements
- Username: 3-20 characters, letters, numbers, and underscores only
- Name: 2-50 characters
- Email: Valid email format required
- Password Requirements:
  - At least 8 characters long
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character (!@#$%^&*(),.?":{}|<>)

#### Blog Post Requirements
- Title: 5-100 characters
- Category: Must select from available options:
  - Top 10s
  - John's Journeys
  - Moments to Memories
  - Reviews
- Date: Valid date required
- Content: Minimum 10 characters
- Type: Must select from:
  - Published
  - Draft
  - Private

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd blog
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python tempCreateTables2.py
python tempFillTables.py
```

5. Set up environment variables:
- Create a `.env` file in the root directory
- Add the following variables:
  ```
  FLASK_APP=app.py
  FLASK_ENV=development
  SECRET_KEY=your_secure_secret_key
  ```

6. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
blog/
├── app.py              # Main application file
├── forms.py            # Form definitions and validation
├── requirements.txt    # Project dependencies
├── static/            
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Image uploads
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── login.html     # Login form
│   ├── register.html  # Registration form
│   └── ...           # Other templates
└── database.db        # SQLite database
```

## Dependencies

- Flask==3.1.0
- Flask-WTF==1.2.1
- email-validator==2.2.0
- And others (see requirements.txt)

## Form Validation Details

### User Registration
- Username validation ensures unique usernames
- Email validation checks for valid format
- Password validation ensures strong passwords
- All fields are required

### Blog Posts
- Title length is enforced
- Category must be selected from predefined options
- Content length minimum is enforced
- Post type must be selected
- Date must be valid

### Login
- Username and password are required
- Case-sensitive matching
- Session-based authentication

## Security Features

- CSRF protection on all forms
- Password validation rules
- Secure session handling
- Input sanitization
- Error handling and user feedback

## Error Handling

- Form validation errors are displayed clearly
- Database errors are caught and handled
- User-friendly error messages
- Redirect handling for invalid routes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 