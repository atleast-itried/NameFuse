from flask import Flask, jsonify, request, render_template
from .models import db, Name, Match
import os

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure the app
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get(
                'DATABASE_URL', 'sqlite:///namefuse.db'
            ),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
    else:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize names if database is empty
        if Name.query.count() == 0:
            Name.initialize_names()
    
    @app.route('/')
    def index():
        """Serve the login page."""
        return render_template('login.html')
    
    @app.route('/names')
    def names_page():
        """Serve the name selection page."""
        return render_template('index.html')
    
    @app.route('/matches-page')
    def matches_page():
        """Serve the matches page."""
        return render_template('matches.html')
    
    @app.route('/names/list')
    def get_names():
        """Get a list of names filtered by gender and origin."""
        gender = request.args.get('gender')
        origin = request.args.get('origin')
        
        query = Name.query
        if gender:
            query = query.filter_by(gender=gender)
        if origin:
            query = query.filter_by(origin=origin)
            
        names = query.order_by(db.func.random()).limit(10).all()
        return jsonify([{
            'id': name.id,
            'name': name.name,
            'origin': name.origin,
            'gender': name.gender
        } for name in names])
    
    @app.route('/like', methods=['POST'])
    def like_name():
        """Like or dislike a name."""
        data = request.get_json()
        name_id = data.get('name_id')
        user_id = data.get('user_id')
        liked = data.get('liked', True)
        
        if not all([name_id, user_id]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        matched = Match.create_match(name_id, user_id, liked)
        
        response = {'matched': matched}
        if matched:
            name = Name.query.get(name_id)
            response['name'] = name.name
            
        return jsonify(response)
    
    @app.route('/matches')
    def get_matches():
        """Get all matched names."""
        matches = Match.query.filter_by(matched=True).distinct(Match.name_id).all()
        return jsonify([{
            'id': match.id,
            'name': match.name.name,
            'origin': match.name.origin,
            'gender': match.name.gender
        } for match in matches])
    
    @app.route('/clear-matches', methods=['POST'])
    def clear_matches():
        """Clear all matches from the database."""
        Match.clear_matches()
        return jsonify({'status': 'success'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 