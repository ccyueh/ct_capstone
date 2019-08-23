from app import app, db
from flask import request, jsonify
from app.models import Party, User, Bottle, Rating, Characteristic, party_guests, rating_characteristics
from datetime import datetime, timedelta
import time
import jwt

@app.route('/')
def index():
    return ''

@app.route('/authenticate/register', methods=['POST'])
def register():
    try:
        token = request.headers.get('token')
        
        # decode token back to dictionary
        data = jwt.decode(
        token,
        app.config['SECRET_KEY'],
        algorithm=['HS256']
        )
        
        if data.get('email') and data.get('password') and data.get('password2'):
            # check if re-typed password matches
            if data.get('password') == data.get('password2'):
                user = User(
                first_name=data.get('first'),
                last_name=data.get('last'),
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

@app.route('/authenticate/login', methods=['GET'])
def login():
    try:
        token = request.headers.get('token')

        # decode token back to dictionary
        data = jwt.decode(
        token,
        app.config['SECRET_KEY'],
        algorithm=['HS256']
        )

        user = User.query.filter_by(email=data.get('email')).first()
        if user is None or not user.check_password(data.get('password')):
            return jsonify({ 'error': 'Error #019: Incorrect email and/or password.' })
        else:
            return jsonify({ 'success': 'You are now logged in.', 'token': user.get_token() })
    except:
        return jsonify({ 'error': 'Error #019: Could not log in.' })

@app.route('/api/users/retrieve', methods=['GET'])
def getUser():
    try:
        user_id = request.args.get('user_id')
        if user_id:
            result = User.query.filter_by(user_id=user_id).first()
            user = {
                'first_name': result.first_name,
                'last_name': result.last_name,
                'email': result.email,
                'password_hash': result.password_hash
            }
        else:
            return jsonify({ 'error': 'Error #016: Missing user ID.' })

        return jsonify({ 'success': 'User info retrieved.', 'user': user })
    except:
        return jsonify({ 'error': 'Error #017: Could not find user.' })

@app.route('/api/parties/save', methods=['POST'])
def createParty():
    try:
        data = request.json

        party_id = data.get('party_id')
        date = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        party_name = data.get('party_name')
        location = data.get('location')
        host_id = data.get('host_id')
        voting = data.get('voting')
        reveal = data.get('reveal')

        if date:
            if start_time:
                start = datetime.strptime(f'{date} {start_time}', '%Y-%m-%d %H:%M')
            if end_time:
                end = datetime.strptime(f'{date} {end_time}', '%Y-%m-%d %H:%M')
            if start_time and end_time:
                if start_time > end_time:
                    end += timedelta(days=1)

        if party_id:
            party = Party.query.filter_by(party_id=party_id).first()
            if voting:
                party.voting = voting
            if reveal:
                party.reveal = reveal
            if voting or reveal:
                db.session.add(party)
                db.session.commit()

                return jsonify({ 'success': 'Voting/bottle reveal status changed.' })

        if None not in data.values() and "" not in data.values():
            # modify existing party - edit details, start/stop voting, reveal bottles
            if party_id:
                party.start = start
                party.end = end
                party.party_name = party_name
                party.location = location

            # create new party
            else:
                party = Party(
                    start=start,
                    end=end,
                    party_name=party_name,
                    location=location,
                    host_id=host_id
                )

            db.session.add(party)
            db.session.commit()

            return jsonify({ 'success': 'Party created/edited.' })
        else:
            return jsonify({ 'error': 'Error #001: All fields are required.' })
    except:
        return jsonify({ 'error': 'Error #002: Invalid parameters.' })


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

        bottle_id = data.get('bottle_id')
        producer = data.get('producer')
        bottle_name = data.get('bottle_name')
        vintage = data.get('vintage')
        label_img = data.get('label_img')
        party_id = data.get('party_id')
        user_id = data.get('user_id')

        if label_img and party_id and user_id:
            if bottle_id:
                bottle = Bottle.query.filter_by(bottle_id=bottle_id).first()

                bottle.producer = producer
                bottle.bottle_name = bottle_name
                bottle.vintage = vintage
                bottle.label_img = label_img

            else:
                bottle = Bottle(
                    producer=producer,
                    bottle_name=bottle_name,
                    vintage=vintage,
                    label_img=label_img,
                    party_id=party_id,
                    user_id=user_id
                )

            db.session.add(bottle)
            db.session.commit()

            return jsonify({ 'success': 'Bottle added/edited.' })
        else:
            return jsonify({ 'error': 'Error #008: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #009: Could not add bottle.' })

@app.route('/api/ratings/save', methods=['POST'])
def rate():
    try:
        data = request.json

        rating_id = data.get('rating_id')
        stars = data.get('stars')
        description = data.get('description')
        user_id = data.get('user_id')
        bottle_id = data.get('bottle_id')
        characteristics = data.get('characteristics')

        if stars and user_id and bottle_id:
            if rating_id:
                rating = Rating.query.filter_by(rating_id=rating_id).first()

                rating.stars = stars
                rating.description = description
                rating.characteristics = []

            else:
                rating = Rating(
                    stars=stars,
                    description=description,
                    user_id=user_id,
                    bottle_id=bottle_id)

            for characteristic_id in characteristics:
                characteristic = Characteristic.query.filter_by(characteristic_id=characteristic_id).first()
                rating.characteristics.append(characteristic)

            db.session.add(rating)
            db.session.commit()

            return jsonify({ 'success': 'Rating added/edited.' })
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

@app.route('/api/parties/retrieve', methods=['GET'])
def getParty():
    try:
        party_id = request.args.get('party_id')
        host_id = request.args.get('host_id')
        user_id = request.args.get('user_id')

        # get party information for specific party
        if party_id and not host_id and not user_id:
            results = Party.query.filter_by(party_id=party_id).all()
        # get party information for parties hosted by user
        elif host_id and not user_id and not party_id:
            results = Party.query.filter_by(host_id=host_id).all()
        # get party information for parties attended by user
        elif user_id and not host_id and not party_id:
            results = Party.query.join(party_guests).join(User).filter(User.user_id == user_id).all()
        else:
            return jsonify({ 'error': 'Error #016: Retrieve parties using one ID only.' })

        parties = []
        for result in results:
            party = {
                'party_id': result.party_id,
                'start': result.start,
                'end': result.end,
                'party_name': result.party_name,
                'location': result.location,
                'host_id': result.host_id,
                'voting': result.voting,
                'reveal': result.reveal
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
        party_id = request.args.get('party_id')
        user_id = request.args.get('user_id')

        bottles = []
        if party_id:
            results = Bottle.query.filter_by(party_id=party_id).all()
            if user_id:
                results = Bottle.query.filter_by(party_id=party_id, user_id=user_id).all()

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
            
            if len(bottles) == 1:
                bottles = bottles[0]

            return jsonify({ 'success': 'Retrieved bottles.', 'bottles': bottles })
        else:
            return jsonify({ 'error': 'Error #018: Missing parameters.' })
    except:
        return jsonify({ 'error': 'Error #019: Could not find bottles.' })

@app.route('/api/ratings/retrieve', methods=['GET'])
def getRating():
    try:
        user_id = request.args.get('user_id')
        bottle_id = request.args.get('bottle_id')

        # get user's rating/tasting notes for specific bottle
        if bottle_id and user_id:
            result = Rating.query.filter_by(user_id=user_id, bottle_id=bottle_id).first()
            if result:
                rating = {
                    'bottle_id': result.bottle_id,
                    'rating_id': result.rating_id,
                    'stars': result.stars,
                    'description': result.description,
                }

                results = db.session.query(Characteristic.characteristic_name).join(rating_characteristics).join(Rating).filter(Rating.rating_id == result.rating_id).all()
                characteristics = [result[0] for result in results]
                rating['characteristics'] = characteristics

                return jsonify({ 'success': 'Rating retrieved.', 'rating': rating})
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
