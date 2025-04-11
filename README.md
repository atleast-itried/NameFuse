# NameFuse

A web application that helps couples find the perfect baby name by matching their preferences. Each partner can independently like or dislike names, and when both partners like the same name, it's a match!

## Features

- Role-based access (Wife/Husband)
- Filter names by gender and origin
- Real-time match notifications
- Separate matches page
- Support for multiple name origins:
  - British
  - German
  - Italian
  - Spanish
  - Swiss
  - Irish
  - Hebrew

## Installation

1. Clone the repository:
```bash
git clone https://github.com/atleast-itried/NameFuse.git
cd NameFuse
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

The application will be available at http://localhost:8080

## Usage

1. Open http://localhost:8080 in your browser
2. Choose your role (Wife or Husband)
3. Start swiping through names:
   - Use filters to narrow down by gender and origin
   - Like or dislike names using the buttons
   - Get notified when you and your partner match on a name
4. View all matches in the matches page
5. Clear matches to start fresh

## Technologies Used

- Python 3.11+
- Flask
- SQLAlchemy
- names-dataset
- Bootstrap 5
- Font Awesome

## License

MIT License 