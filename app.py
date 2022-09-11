from flask import Flask, jsonify
import pandas as pd
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect = True)
measurement = base.classes.measurement
station = base.classes.station
session = Session(engine)

@app.route("/")
def home():
    return (
        """
        <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br>
        <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br>
        <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br>
        <a href='/api/v1.0/start/end'>/api/v1.0/start/end</a>
        """
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_year = dt.datetime(2017, 8, 23) - dt.timedelta(365)
    last_year_query = session.query(measurement.date, measurement.prcp).filter(measurement.date > last_year).all()
    session.close()
    year_precip = {date: prcp for date, prcp in last_year_query}
    return jsonify(year_precip)

@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(measurement.station).all()
    session.close()
    station_json = list(np.ravel(station_query))
    return jsonify(station_json)

@app.route("/api/v1.0/tobs")
def tobs():
    station_count = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    tobs_query = session.query(measurement.tobs).filter(measurement.station == station_count[0][0]).all()
    session.close()
    tobs_json = list(np.ravel(tobs_query))
    return jsonify(tobs_json)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        start_query = session.query(measurement.tobs).filter(measurement.date > start).all()
        session.close()
        response = [np.max(start_query), np.min(start_query), np.mean(start_query)]
        return jsonify(response)
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    start_query = session.query(measurement.tobs).filter(measurement.date > start).filter(measurement.date < end).all()
    session.close()
    response = [np.max(start_query), np.min(start_query), np.mean(start_query)]
    return jsonify(response)

if __name__ == "__main__":
    app.run()