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
Base.prepare(autoload_with=engine)

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<br>"
        f"/api/v1.0//"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    data = []
    for date, prcp in prcp_data:
        prcp_dic = {}
        prcp_dic[date] = prcp
        data.append(prcp_dic)
       
    return jsonify(data)

def station():
    active_stations = session.query(station.station,
                                    station.name,
                                    station.latitude,
                                    station.longitude,
                                    station.elevation).group_by(station.station).all()
    session.close()
    # my attempt at list comprehesion for a dictionary :3
    stations_list = [{'Station': row[0],
                 'Name': row[1],
                 'Latitude': row[2],
                 'longitude':row[3],
                 'elevation':row[4]} for row in active_stations]
    return jsonify(stations_list)

def tobs():
    temperature_data = session.query(Measurement.tobs).\
            filter(Measurement.station == "USC00519281").\
            filter(Measurement.date >= one_year_ago).all()

    # Convert the result to a list of temperatures
    temperatures = [temp[0] for temp in temperature_data]

    return jsonify(tobs)








if __name__ == '__main__':
    app.run(debug=True)