import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)


app = Flask(__name__)



@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
   
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    recent_date = dt.strptime(recent_date, "%Y-%m-%d")

    first_date = recent_date - dt.timedelta(days=365)

    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()
    return jsonify(last_year_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date


    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")

    first_date = recent_date - dt.timedelta(days=365)

    total_number_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
 
    active_station = (total_number_stations[0])
    active_station = (active_station[0])
 
    session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.station == active_station).all()
   
    active_station_year_obs = session.query(Measurement.tobs).\
    filter(Measurement.station == active_station).filter(Measurement.date >= first_date).all()
    return jsonify(active_station_year_obs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)

    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
       
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
  
    return jsonify(results)

if __name__ == '__main__':
    app.run()
