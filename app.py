# Import the dependencies
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:////Users/nathalylamas/Documents/Bootcamp/Homework/sqlalchemy-challenge/Resources/hawaii.sqlite")


Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start a session
    session = Session(engine)

    # Calculate the date one year ago from the last data point
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    # Convert to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    # Close the session
    session.close()
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Start a session
    session = Session(engine)

    # Query all stations
    stations_data = session.query(Station.station).all()
    
    # Convert the list of tuples into a list
    stations_list = [station[0] for station in stations_data]
    
    # Close the session
    session.close()

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Start a session
    session = Session(engine)

    # Calculate the date one year ago from the last data point
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station for the last year
    most_active_station_id = 'USC00519281'  # Replace with actual station ID if different
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= prev_year).all()
    
    # Convert to a list
    tobs_list = [temp[0] for temp in tobs_data]
    
    # Close the session
    session.close()
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start=None, end=None):
    # Start a session
    session = Session(engine)

    # Query for temperature stats for a given start (and optional end date)
    if not end:
        # Calculate min, avg, and max temperature for all dates >= start date
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    else:
        # Calculate min, avg, and max temperature for dates between start and end inclusive
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Unpack results and create a dictionary
    temp_dict = {
        "TMIN": temps[0][0],
        "TAVG": temps[0][1],
        "TMAX": temps[0][2]
    }
    
    # Close the session
    session.close()
    
    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5001)