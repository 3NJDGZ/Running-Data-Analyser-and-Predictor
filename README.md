# Running-Data-Analyser-and-Predictor

## Roadmap

- [x] **Version 1.0**
  - [x] Initial project setup.
  - [x] Integrate stravalib. -> need to change this completely, need to integrate garminconnect instead due to strava data regulations
    - [ ] need to completely redo data pipeline....
  - [x] Setup up Front End (basic).
    - [ ] login page.
    - [ ] about page.
    - [ ] stats page.
    - [ ] user page.
  - [x] Setup ML Back End.
    - [ ] predict intensity
    - [ ] predict marathon, 5k, 10k, half marathon, 15k times... 
  - [x] Connect ML Back end and Front End together.
  - [x] Implement caching system.
    - [ ] refactor caching system to adopt integration of garminconnect
    - [ ] redis DB as cache temporary rapid cache.
    - [ ] mongo DB as persistent permanent data store.

## Important Links/docs:
- https://getbootstrap.com/docs/5.3/getting-started/introduction/
- https://stravalib.readthedocs.io/en/latest/index.html
- https://www.w3schools.com/bootstrap5/
- https://developers.strava.com/docs/reference/ 
- https://dev.to/nandamtejas/implementing-flask-application-using-object-oriented-programming-oops-5cb
- https://github.com/cyberjunky/python-garminconnect
