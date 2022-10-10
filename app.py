#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
from multiprocessing.pool import AsyncResult
from unittest import result
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import datetime
from flask_wtf import FlaskForm

from model import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
#CHEDJOU==> in model.py file

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# CHEDJOU==> : i first create my table with db.create_all() before using migration for other updates
# db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # CHEDJOU==>num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  datas = {}
  data = []
  for city_state in db.session.query(Venue.city,Venue.state).distinct():
    datas["city"] = city_state[0]
    datas["state"] = city_state[1]
    venue_city={}
    venue_city_list=[]
    #CHEDJOU==> datetime object containing current date and time
    now = datetime.now()
    for v in Venue.query.filter_by(city=city_state[0], state=city_state[1]).distinct():
      num_upcoming_shows = Venue.query.join(Shows).filter(id==v.id , Shows.start_time >= now).count()
      venue_city["id"] = v.id
      venue_city["name"] = ''.join(v.name)
      venue_city["num_upcoming_shows"] = num_upcoming_shows
      venue_city_list.append(venue_city)
      venue_city={}
     
    datas['venues'] = venue_city_list
    data.append(datas)
    datas={}
  
  # datad=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  
  return render_template('pages/venues.html', areas=data);

def row2dict(row):
  d = {}
  for column in row.__table__.columns:
      d[column.name] = str(getattr(row, column.name))
  return d

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  venues_result = db.session.query(Venue).filter(Venue.name.ilike("%{0}%".format(search_term))).all()
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue_city={}
  venue_city_list=[]
  response={}
  response['count'] = len(venues_result)
  response["data"]=[]
  # datetime object containing current date and time
  now = datetime.now()
  for venue_result in venues_result:
    num_upcoming_shows = Venue.query.join(Shows).filter(id==venue_result.id , Shows.start_time >= now).count()
    venue_city["id"] = venue_result.id
    venue_city["name"] = ''.join(venue_result.name)
    venue_city["num_upcoming_shows"] = num_upcoming_shows
    response["data"].append(venue_city)
    venue_city={}
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  list_venues = Venue.query.all()
  result_venues = []
  venue_info = {}
  for l in list_venues:
    venue_info=l.as_dict()
    print(venue_info)
    now = datetime.now()
    
    #CHEDJOU==> PAST SHOW AGGREGATION
    past_shows_artist_info = db.session.query(Artist).join(Shows).join(Venue).filter(Venue.id==l.id).filter(Shows.start_time <= now).all()
    infor_past_show={}
    list_info_past_show=[]
    for info in past_shows_artist_info:
      infor_past_show['artist_id'] = info.id
      infor_past_show['artist_name'] = info.name
      infor_past_show['artist_image_link'] = info.image_link
      st=db.session.query(Shows.start_time).join(Venue).join(Artist).filter(Shows.venue_id==l.id).filter(Shows.artist_id==info.id).filter(Shows.start_time <= now).first()
      infor_past_show['start_time'] = "{0}".format(st[0])
      list_info_past_show.append(infor_past_show)
      infor_past_show={}
    venue_info['past_shows'] = list_info_past_show
  #CHEDJOU==> UPCOMMING SHOW AGREGATION
  
    upcomming_shows_artist_info = db.session.query(Artist).join(Shows).join(Venue).filter(Venue.id==l.id, Shows.start_time >= now).all()
    infor_upcomming_show={}
    list_info_upcomming_show=[]
    for info in upcomming_shows_artist_info:
      infor_upcomming_show['artist_id'] = info.id
      infor_upcomming_show['artist_name'] = info.name
      infor_upcomming_show['artist_image_link'] = info.image_link
      st=db.session.query(Shows.start_time).join(Venue).join(Artist).filter(Shows.venue_id==l.id).filter(Shows.artist_id==info.id).filter(Shows.start_time >= now).first()
      infor_upcomming_show['start_time'] = "{0}".format(st[0])
      list_info_upcomming_show.append(infor_upcomming_show)
      infor_upcomming_show={}
    venue_info['upcoming_shows'] = list_info_upcomming_show
    venue_info['past_shows_count'] = len(list_info_past_show)
    venue_info['upcoming_shows_count'] = len(list_info_upcomming_show)
    result_venues.append(venue_info)
    venue_info={}
  
  
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  
  data = list(filter(lambda d: d['id'] == venue_id, result_venues))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm()
  
  if form.validate_on_submit():
    error=False
    data={}
    try :
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('name')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
      venue = Venue(name=name,
                    city=city, 
                    state=state, 
                    address=address, 
                    phone=phone, 
                    image_link=image_link,
                    genres= genres,
                    facebook_link=facebook_link,
                    website_link=website_link,
                    seeking_talent=True if seeking_talent=='y' else False,
                    seeking_description=seeking_description)
      
      db.session.add(venue)
    # TODO: modify data to be the data object returned from db insertion
      data = venue
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
          db.session.close()       

    # on successful db insert, flash success
    if not error :
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    else : 
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  #CHEDJOU==>if submit validator ares not OK
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')  
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  try:
    venue = Venue.query.get(venue_id)
    # CHEDJOU==>FIRST DELETE SHAOW WITH venue_id BECAUSE OF CASCADE OPTION  
    Shows.query.filter(Shows.venue_id==venue_id).delete()
    #CHEDJOU==> NOW DELETE DE VENU
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  return redirect(url_for('index'))
    
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  
  # MA REPONSE est à la ligne 15 du fichier venues.html
  
  # clicking that button delete it from the db then redirect the user to the homepage

  #MA REPONSE EST À PARTIR DE LA LIGNE 20 DU FICHIER venues.html
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data = Artist.query.all()
  result_dict={}
  result_list=[]
  results = db.session.query(Artist.id, Artist.name).all()
  for result in results :
    result_dict["id"]=result.id
    result_dict["name"]=result.name
    result_list.append(result_dict)
    result_dict={}
  data = result_list
  
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term=request.form.get('search_term', '')
 
  artists_result = db.session.query(Artist).filter(Artist.name.ilike("%{0}%".format(search_term))).all()

  artist_city={}
  artist_city_list=[]
  response={}
  response['count'] = len(artists_result)
  response["data"]=[]
  
  #CHEDJOU==> datetime object containing current date and time
  now = datetime.now()
  for artist_result in artists_result:
    num_upcoming_shows = Artist.query.join(Shows).filter(id==artist_result.id , Shows.start_time >= now).count()
    artist_city["id"] = artist_result.id
    artist_city["name"] = ''.join(artist_result.name)
    artist_city["num_upcoming_shows"] = num_upcoming_shows
    response["data"].append(artist_city)
    artist_city={}
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  list_artists = Artist.query.all()
  result_artists = []
  artist_info = {}
  
  for l in list_artists:
    artist_info=l.as_dict()
    print(artist_info)
    
    now = datetime.now()
    #CHEDJOU==> PAST SHOW AGGREGATION
    past_shows_venue_info = db.session.query(Venue).join(Shows).join(Artist).filter(Artist.id==l.id, Shows.start_time <= now).all()
    infor_past_show={}
    list_info_past_show=[]
    for info in past_shows_venue_info:
      infor_past_show['venue_id'] = info.id
      infor_past_show['venue_name'] = info.name
      infor_past_show['venue_image_link'] = info.image_link
      st=db.session.query(Shows.start_time).join(Venue).join(Artist).filter(Shows.venue_id==info.id).filter(Shows.artist_id==l.id).filter(Shows.start_time <= now).first()
      infor_past_show['start_time'] = "{0}".format(st[0])
      list_info_past_show.append(infor_past_show)
      infor_past_show={}
    artist_info['past_shows'] = list_info_past_show
    
  #CHEDJOU==> UPCOMMING SHOW AGREGATION
  
    upcomming_shows_venue_info = db.session.query(Venue).join(Shows).join(Artist).filter(Artist.id==l.id, Shows.start_time >= now).all()
    infor_upcomming_show={}
    list_info_upcomming_show=[]
    for info in upcomming_shows_venue_info:
      infor_upcomming_show['venue_id'] = info.id
      infor_upcomming_show['venue_name'] = info.name
      infor_upcomming_show['venue_image_link'] = info.image_link
      st=db.session.query(Shows.start_time).join(Venue).join(Artist).filter(Shows.venue_id==info.id).filter(Shows.artist_id==l.id).filter(Shows.start_time >= now).first()
      infor_upcomming_show['start_time'] = "{0}".format(st[0])
      list_info_upcomming_show.append(infor_upcomming_show)
      infor_upcomming_show={}
    artist_info['upcoming_shows'] = list_info_upcomming_show
    artist_info['past_shows_count'] = len(list_info_past_show)
    artist_info['upcoming_shows_count'] = len(list_info_upcomming_show)
    result_artists.append(artist_info)
    artist_info={}
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  
  data = list(filter(lambda d: d['id'] == artist_id, result_artists))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).as_dict()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  if form.validate_on_submit():
    try :
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')
      
      artist=Artist.query.get(artist_id)
      artist.name=name
      artist.city=city
      artist.state=state
      artist.phone=phone
      artist.facebook_link=facebook_link
      artist.website_link=website_link
      artist.seeking_venue=True if seeking_venue=='y' else False
      artist.seeking_description=seeking_description
      artist.genres = genres
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
          db.session.close()       
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id).as_dict()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  if form.validate_on_submit():
    error=False
    data={}
    try :
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('name')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
      venue = Venue.query.get(venue_id)
      venue.name=name
      venue.city=city
      venue.state=state, 
      venue.address=address
      venue.phone=phone
      venue.image_link=image_link
      venue.facebook_link=facebook_link
      venue.website_link=website_link
      venue.seeking_talent=True if seeking_talent=='y' else False
      venue.seeking_description=seeking_description
      # genres_db=db.session.query(Genres).filter(Genres.name.in_(genres)).all()
      # print(genres_db)
      venue.genres = genres
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
          db.session.close()    
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
        
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  #CHEDJOU==> if submit validators are OK
  if form.validate_on_submit():
    error=False
    data={}
    try :
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')
      artist = Artist(name=name,
                    city=city, 
                    state=state,
                    phone=phone,
                    genres = genres,
                    facebook_link= facebook_link,
                    website_link= website_link,
                    seeking_venue=True if seeking_venue=='y' else False,
                    seeking_description=seeking_description)
      # genres_db=db.session.query(Genres).filter(Genres.name.in_(genres)).all()
    
      db.session.add(artist)
      data = artist
      
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
          db.session.close()       

    # on successful db insert, flash success
    if not error :
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    else : 
      print(data)
      flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shw={}
  results=[]
  list_show = db.session.query(Venue.id, Venue.name,Artist.id,Artist.name, Artist.image_link, Shows.start_time).filter(Shows.venue_id==Venue.id).filter(Shows.artist_id==Artist.id).all()
  print(list_show)
  for sh in list_show:
    shw["venue_id"] = sh[0]
    shw["venue_name"] = sh[1]
    shw["artist_id"] = sh[2]
    shw["artist_name"] = sh[3]
    shw["artist_image_link"] = sh[4]
    start_temps = sh[5]
    shw["start_time"] = "{0}".format(start_temps)
    results.append(shw)
    shw={}
  print(results)
  data = results
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if form.validate_on_submit():
    error=False
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try :
      artist_id = request.form.get('artist_id')
      venue_id = request.form.get('venue_id')
      start_time = request.form.get('start_time')
      show_objt = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show_objt)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
          db.session.close()
    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    if not error:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
