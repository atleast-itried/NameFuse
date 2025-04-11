from flask_sqlalchemy import SQLAlchemy
from names_dataset import NameDataset
import random
from typing import List, Dict, Optional

db = SQLAlchemy()
names_db = NameDataset()

class NameDistribution:
    DISTRIBUTION = {
        'ES': {'count': 250},  # Spanish
        'GB': {'count': 250},  # English
        'CH': {'count': 100},  # Swiss
        'DE': {'count': 250},  # German
        'IT': {'count': 250},  # Italian
        'IE': {'count': 100},  # Irish
        'IL': {'count': 100},  # Hebrew
        'VA': {'count': 50},   # Latin
    }

    @staticmethod
    def get_name_probability(name: str, country_code: str) -> float:
        """Get the probability that a name belongs to a specific country."""
        result = names_db.search(name)
        if not result or 'first_name' not in result:
            return 0.0
        
        country_probs = result['first_name'].get('country', {})
        # Map country codes to country names
        country_mapping = {
            'ES': 'Spain',
            'GB': 'United Kingdom',
            'CH': 'Switzerland',
            'DE': 'Germany',
            'IT': 'Italy',
            'IE': 'Ireland',
            'IL': 'Israel',
            'VA': 'Italy'  # Using Italy as proxy for Latin names
        }
        
        return country_probs.get(country_mapping.get(country_code, ''), 0.0)

    @staticmethod
    def get_gender(name: str) -> Optional[str]:
        """Get the likely gender for a name."""
        result = names_db.search(name)
        if not result or 'first_name' not in result:
            return None
        
        gender_probs = result['first_name'].get('gender', {})
        if not gender_probs:
            return None
        
        return max(gender_probs.items(), key=lambda x: x[1])[0]

class Name(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(2), nullable=False)  # Country code
    gender = db.Column(db.String(10), nullable=False)
    
    def get_country_info(self) -> Dict[str, float]:
        """Get country distribution information for the name."""
        result = names_db.search(self.name)
        if not result or 'first_name' not in result:
            return {}
        
        return result['first_name'].get('country', {})
    
    @staticmethod
    def get_gender(name: str) -> Optional[str]:
        """Get the likely gender for a name."""
        result = names_db.search(name)
        if not result or 'first_name' not in result:
            return None
        
        gender_probs = result['first_name'].get('gender', {})
        if not gender_probs:
            return None
        
        return max(gender_probs.items(), key=lambda x: x[1])[0]
    
    @staticmethod
    def initialize_names():
        """Initialize the name database with the required distribution."""
        # Distribution of names by country
        distribution = {
            'ES': 250,  # Spanish
            'GB': 250,  # English
            'CH': 100,  # Swiss
            'DE': 250,  # German
            'IT': 250,  # Italian
            'IE': 100,  # Irish
            'IL': 100,  # Hebrew
        }
        
        # Clear existing names
        Name.query.delete()
        
        # Get top names for each country and filter by probability
        for country_code, total_count in distribution.items():
            target_per_gender = total_count // 2  # Equal split between genders
            
            names_by_gender = {'Female': [], 'Male': []}
            
            # Get names from the dataset
            top_names = names_db.get_top_names(n=2000)  # Get more names to ensure enough for each gender
            
            for name in top_names.get(country_code, {'M': [], 'F': []}).get('M', []):
                gender = Name.get_gender(name)
                if gender == 'Male':
                    names_by_gender['Male'].append(name)
                
            for name in top_names.get(country_code, {'M': [], 'F': []}).get('F', []):
                gender = Name.get_gender(name)
                if gender == 'Female':
                    names_by_gender['Female'].append(name)
            
            # Add equal numbers of male and female names
            for gender in ['Female', 'Male']:
                available_names = len(names_by_gender[gender])
                for name in names_by_gender[gender][:min(target_per_gender, available_names)]:
                    db.session.add(Name(
                        name=name,
                        origin=country_code,
                        gender=gender
                    ))
            
            db.session.commit()

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.Integer, db.ForeignKey('name.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    liked = db.Column(db.Boolean, nullable=False)
    matched = db.Column(db.Boolean, default=False)
    
    name = db.relationship('Name', backref=db.backref('matches', lazy=True))
    
    @staticmethod
    def clear_matches():
        """Clear all matches from the database."""
        Match.query.delete()
        db.session.commit()
    
    @staticmethod
    def create_match(name_id: int, user_id: int, liked: bool) -> bool:
        """Create a match record and check if both users liked the name."""
        # Create new match
        match = Match(name_id=name_id, user_id=user_id, liked=liked)
        db.session.add(match)
        
        # Check if other user liked the same name
        other_user_id = 1 if user_id == 2 else 2
        other_match = Match.query.filter_by(
            name_id=name_id,
            user_id=other_user_id,
            liked=True
        ).first()
        
        # If both users liked the name, mark as matched
        if liked and other_match:
            match.matched = True
            other_match.matched = True
        
        db.session.commit()
        return match.matched 