from flask_sqlalchemy import SQLAlchemy
import time
import datetime
from sqlalchemy import func


# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Association table for many-to-many relationship between Mother and Provider
mother_provider_association = db.Table(
    'mother_provider_association',
    db.Column('mother_id', db.Integer, db.ForeignKey('mothers.id'), primary_key=True),
    db.Column('provider_id', db.Integer, db.ForeignKey('providers.id'), primary_key=True)
)

# Define Mother model
class Mother(db.Model):
    __tablename__ = 'mothers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    public_or_private = db.Column(db.Boolean, nullable=True, default=False)
    opt_in_ads = db.Column(db.Boolean, nullable=True, default=False)
    prev_children = db.Column(db.Integer, nullable=False, default=0)
    deliver_yet = db.Column(db.Boolean, nullable=False, default=False)
    DOB = db.Column(db.Date, nullable=True) #this id DOB of baby. If not given birth yet, urge them to put 1st of expected month.
    providers = db.relationship('Provider', secondary=mother_provider_association, backref='mothers')
    posts = db.relationship('Post', backref='mother', lazy=True)

    #THE 4 PREFRENCE INFORMATION. THIS CAN BE NULL
    cravings = db.Column(db.String(255), nullable=True)
    pains_nausea = db.Column(db.String(255), nullable=True)
    thoughts_concerns = db.Column(db.String(255), nullable=True)
    other_info_dietary_restrictions = db.Column(db.String(255), nullable=True)

    #add include_providers in case we are accessing from opposite side.
    def serialize(self, include_providers = True):
        data =  {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'public_or_private': self.public_or_private,
            'opt_in_ads': self.opt_in_ads,
            'prev_children': self.prev_children,
            'deliver_yet': self.deliver_yet,
            'DOB': self.DOB.isoformat(), 

            #In serialization, truncate to first 25 characters if below preference information is given. 
            'cravings': (self.cravings[:25] + '...') if self.cravings and len(self.cravings) > 25 else self.cravings,
            'pains_nausea': (self.pains_nausea[:25] + '...') if self.pains_nausea and len(self.pains_nausea) > 25 else self.pains_nausea,
            'thoughts_concerns': (self.thoughts_concerns[:25] + '...') if self.thoughts_concerns and len(self.thoughts_concerns) > 25 else self.thoughts_concerns,
            'other_info_dietary_restrictions': (self.other_info_dietary_restrictions[:25] + '...') if self.other_info_dietary_restrictions and len(self.other_info_dietary_restrictions) > 25 else self.other_info_dietary_restrictions,
            'posts': [post.serialize() for post in self.posts]
        }
        if include_providers:
            data["providers"] = [provider.serialize(include_mothers=False) for provider in self.providers]
        return data
    

# Define Provider model
class Provider(db.Model):
    __tablename__ = 'providers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    license_number = db.Column(db.String, nullable=True)
    state_name = db.Column(db.String, nullable=True)
    diploma_date = db.Column(db.Date, nullable=True)

    def serialize(self,include_mothers = True):
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'license_number': self.license_number,
            'state_name': self.state_name,
            'diploma_date': self.diploma_date.isoformat(),
        }
        if include_mothers:
            data["mothers"] = [mother.serialize(include_providers=False) for mother in self.mothers]
        return data
    
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at= db.Column(db.DateTime(timezone=True), server_default=func.now())
    mother_id = db.Column(db.Integer, db.ForeignKey('mothers.id'), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'mother_id': self.mother_id,
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)


"""
Creates few starting Mother, Provider, Post, Events.
"""
def create_hardcoded():
    try:
        if not (Mother.query.count() == 0 and Provider.query.count() == 0 and Post.query.count() == 0):
            return  # Abort if data already exists

        # Providers data
        providers_data = [
            {
                'username': 'provider1',
                'password': 'password1',
                'full_name': 'Provider One',
                'email': 'provider1@example.com',
                'license_number': '12345',
                'state_name': 'California',
                'diploma_date': datetime.date(2000, 1, 1)
            },
            {
                'username': 'provider2',
                'password': 'password2',
                'full_name': 'Provider Two',
                'email': 'provider2@example.com',
                'license_number': '67890',
                'state_name': 'New York',
                'diploma_date': datetime.date(2005, 5, 5)
            },
            {
                'username': 'provider3',
                'password': 'password2',
                'full_name': 'Provider Three',
                'email': 'provider2@example.com',
                'license_number': '34839',
                'state_name': 'New York',
                'diploma_date': datetime.date(2005, 5, 5)
            }
        ]

        # Add providers to database
        providers_dict = {}
        for data in providers_data:
            provider = Provider(**data)
            db.session.add(provider)
            providers_dict[provider.username] = provider

        db.session.commit()  # Commit providers first

        # Mothers data
        mothers_data = [
            {
                'username': 'mother1',
                'password': 'password1',
                'full_name': 'Mother One',
                'email': 'mother1@example.com',
                'public_or_private': True,
                'opt_in_ads': False,
                'prev_children': 1,
                'deliver_yet': True,
                'DOB': datetime.date(2024, 5, 15)
            },
            {
                'username': 'mother2',
                'password': 'password2',
                'full_name': 'Mother Two',
                'email': 'mother2@example.com',
                'public_or_private': False,
                'opt_in_ads': True,
                'prev_children': 0,
                'deliver_yet': False,
                'DOB': datetime.date(2024, 10, 1)
            },
            {
                'username': 'mother3',
                'password': 'password3',
                'full_name': 'Mother Three',
                'email': 'mother3@example.com',
                'public_or_private': True,
                'opt_in_ads': True,
                'prev_children': 2,
                'deliver_yet': False,
                'DOB': datetime.date(2025, 1, 1)
            }
        ]

        # Add mothers to database
        for data in mothers_data:

            mother = Mother(**data)
            db.session.add(mother)

        db.session.commit()  # Commit mothers 
        #not adding associations in hard-coded

        # Posts data
        posts_data = [
            {
                'title': 'First Post',
                'content': 'This is the content of the first post.',
                'mother_id': 1
            },
            {
                'title': 'Second Post',
                'content': 'This is the content of the second post.',
                'mother_id': 1
            },
            {
                'title': 'Third Post',
                'content': 'This is the content of the third post.',
                'mother_id': 2
            }
        ]

        # Add posts to database
        for data in posts_data:
            post = Post(**data)
            db.session.add(post)

        db.session.commit()  # Commit posts

        # Events data
        events_data = [
            {
                'title': 'First Event -- 6/24',
            },
            {
                'title': 'Second Event -- 6/28',
            }
        ]
        # Add events to database
        for event in events_data:
            event = Event(**data)
            db.session.add(event)
        db.session.commit()
        
        print("Data initialization successful!")

    except Exception as e:
        db.session.rollback()  # Rollback in case of any exception
        print(f"Data initialization failed: {str(e)}")
