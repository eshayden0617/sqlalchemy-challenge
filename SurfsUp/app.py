# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(bind=engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Welcome to the Climate Analysis API"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    #convert the data to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def station():
   # Query active stations
    active_stations = session.query(Station.station, Station.name).all()
    
    session.close()
    
    # Convert the data to a list of dictionaries
    stations_list = [{"station": station, "name": name} for station,
                     name in active_stations]
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def get_tobs():  # Add parentheses after the function name
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == "USC00519281").\
                        filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    # Convert the data to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_range(start):
    # Convert the start parameter to a datetime object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    # Query to calculate temperature statistics for dates greater than or equal to start date
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()
    
    # Extract the calculated statistics
    tmin, tavg, tmax = results[0]
    
    # Create a dictionary with the temperature statistics
    temperature_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start, end):
    # Convert the start and end parameters to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    # Query to calculate temperature statistics for dates within the specified range
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
    
    # Extract the calculated statistics
    tmin, tavg, tmax = results[0]
    
    # Create a dictionary with the temperature statistics
    temperature_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    
    return jsonify(temperature_data)

           
if __name__ == '__main__':
    app.run(debug=True)