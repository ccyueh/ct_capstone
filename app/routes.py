from app import app, db
from flask import request, jsonify
from app.models import Party, User, Bottle, Rating, Characteristic, party_guests, rating_characteristics
from datetime import datetime

@app.route('/')
def index():
    return ''

@app.route('/api/parties/save', methods=['POST'])
def createParty():
    try:
        data = request.json

        if None not in data.values():
            party = Party(
                start=data.get('start'),
                end=data.get('end'),
                party_name=data.get('party_name'),
                location=data.get('location'),
                host_id=data.get('host_id')
            )

            db.session.add(party)
            db.session.commit()

            return jsonify({ 'success': 'New party created.' })
        else:
            return jsonify({ 'error': 'Error #001: All fields are required.' })
    except:
        return jsonify({ 'error': 'Error #002: Invalid parameters.' })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json

        if data.get('email') and data.get('password') and data.get('password2'):
            # check if re-typed password matches
            if data.get('password') == data.get('password2'):
                user = User(
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email')
                )

                user.set_password(data.get('password'))

                db.session.add(user)
                db.session.commit()
                return jsonify({ 'success': 'User registered.' })
            else:
                return jsonify({ 'error': 'Error #003: Password and re-typed password must match.' })
        else:
            return jsonify({ 'error': 'Error #004: E-mail and password fields are required.' })
    except:
        return jsonify({ 'error': 'Error #005: Invalid parameters.' })

@app.route('/api/guests/save', methods=['POST'])
def addGuest():
    try:
        data = request.json

        if data.get('party_id') and data.get('user_id'):
            party = db.session.query(Party).filter_by(party_id=data.get('party_id')).first()
            user = db.session.query(User).filter_by(user_id=data.get('user_id')).first()
            party.guests.append(user)

            db.session.add(party)
            db.session.commit()

            return jsonify({ 'success': 'Guest added to party.' })
        else:
            return jsonify({ 'error': 'Error #006: Party and user IDs are required.' })
    except:
        return jsonify({ 'error': 'Error #007: Could not add guest to party.' })

@app.route('/api/bottles/save', methods=['POST'])
def addBottle():
    # user adds bottle for party before party begins
    try:
        data = request.json

        if data.get('label_img') and data.get('party_id') and data.get('user_id'):
            if Bottle.query.filter_by(party_id=data.get('party_id'), user_id=data.get('user_id')).first():
                return jsonify({ 'error': 'Error #008: User already added bottle for this party.' })

            bottle = Bottle(
                producer=data.get('producer'),
                bottle_name=data.get('bottle_name'),
                vintage=data.get('vintage'),
                label_img=data.get('label_img'),
                party_id=data.get('party_id'),
                user_id=data.get('user_id')
            )

            db.session.add(bottle)
            db.session.commit()

            return jsonify({ 'success': 'Bottle added.' })
        else:
            return jsonify({ 'error': 'Error #008: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #009: Could not add bottle.' })

@app.route('/api/ratings/save', methods=['POST'])
def rate():
    try:
        data = request.json

        if Rating.query.filter_by(bottle_id=data.get('bottle_id'), user_id=data.get('user_id')).first():
            return jsonify({ 'error': 'Error #008: Bottle already rated by user.' })

        if data.get('stars') and data.get('user_id') and data.get('bottle_id'):
            rating = Rating(
                stars=data.get('stars'),
                description=data.get('description'),
                user_id=data.get('user_id'),
                bottle_id=data.get('bottle_id'))

            for characteristic_id in data.get('characteristics'):
                characteristic = Characteristic.query.filter_by(characteristic_id=characteristic_id).first()
                rating.characteristics.append(characteristic)

            db.session.add(rating)
            db.session.commit()

            return jsonify({ 'success': 'Rating added.' })
        else:
            return jsonify({ 'error': 'Error #010: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #011: Could not add rating.' })

@app.route('/api/characteristics/save', methods=['POST'])
def addCharacteristic():
    try:
        characteristic_name = request.json.get('characteristic_name')

        if characteristic_name:
            characteristic = Characteristic(characteristic_name=characteristic_name)

            db.session.add(characteristic)
            db.session.commit()

            return jsonify({ 'success': 'Characteristic added.' })
        else:
            return jsonify({ 'error': 'Error #012: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #013: Could not add characteristic.' })

@app.route('/api/ratings/retrieve', methods=['GET'])
def getRating():
    try:
        user_id = request.args.get('user_id')
        bottle_id = request.args.get('bottle_id')

        # get user's rating/tasting notes for specific bottle
        if bottle_id and user_id:
            rating = Rating.query.filter_by(user_id=user_id, bottle_id=bottle_id).first()

            results = Characteristic.query.join(rating_characteristics).join(Rating).filter(Rating.rating_id==1).all()
            characteristics = [result.characteristic_name for result in results]

            return jsonify({ 'success': 'Rating retrieved.', 'rating': rating, 'characteristics': characteristics })
        # get star ratings for specific bottle, or list of who rated it
        elif bottle_id:
            results = Rating.query.filter_by(bottle_id=bottle_id).all()
            star_ratings = [result.stars for result in results]
            rated_by = [result.user_id for result in results]

            return jsonify({ 'success': 'Rating info retrieved.', 'star_ratings': star_ratings, 'rated_by': rated_by })
        else:
            return jsonify({ 'error': 'Error #014: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #015: Could not find rating.' })

@app.route('/api/parties/retrieve', methods=['GET'])
def getParty():
    try:
        party_id = request.headers.get('party_id')
        host_id = request.headers.get('host_id')
        user_id = request.headers.get('user_id')

        # get party information for specific party
        if party_id:
            party = Party.query.filter_by(party_id=party_id).first()

            return jsonify({ 'success': 'Party info retrieved.', 'party': party})
        elif host_id or user_id:
            # get party information for parties hosted by user
            if host_id and not user_id:
                results = Party.query.filter_by(host_id=host_id).all()
            # get party information for parties attended by user
            elif user_id and not host_id:
                results = Party.query.join(party_guests).join(User).filter(User.user_id == user_id).all()
            else:
                return jsonify({ 'error': 'Error #016: Missing parameters.' })

            parties = []
            for result in results:
                party = {
                    'party_id': result.party_id,
                    'start': result.start,
                    'end': result.end,
                    'party_name': result.party_name,
                    'location': result.location
                }
                parties.append(party)

            return jsonify({ 'success': 'Party info retrieved.', 'parties': parties })
            # use party_id(s) to get more information (guests, bottles, ratings)
    except:
        return jsonify({ 'error': 'Error #017: Could not find party/parties.' })

@app.route('/api/bottles/retrieve', methods=['GET'])
def getBottles():
    # get bottle information for all bottles for a party
    try:
        party_id = request.headers.get('party_id')

        if party_id:
            results = Bottle.query.filter_by(party_id=party_id).all()
            bottles = []

            for result in results:
                bottle = {
                    'bottle_id': result.bottle_id,
                    'producer': result.producer,
                    'bottle_name': result.bottle_name,
                    'vintage': result.vintage,
                    'label_img': result.label_img,
                    'user_id': result.user_id
                }
                bottles.append(bottle)

            return jsonify({ 'success': 'Retrieved bottles.', 'bottles': bottles })
        else:
            return jsonify({ 'error': 'Error #018: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #019: Could not find bottles.' })
