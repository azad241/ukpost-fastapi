from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)



app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://192.168.0.103:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=None)
def root():
    return {'status':'Working...'}

#get 4 digit postcode
@app.get("/postcode/", response_model=None)
def read_postcode(skip: int = 0, limit: int = 20, query: str = '', db: Session = Depends(get_db)):
    return crud.get_postcode(db=db, skip=skip, limit=limit, query=query)

#get 3 digit postcode
@app.get("/postcode/{slug}/", response_model=None)
def read_postcode_by_fourdigit(slug: str='', skip: int = 0, limit: int = 20, query: str = '', db: Session = Depends(get_db)):
    return crud.get_postcode_by_fourdigit(db=db, fourdigit=slug, skip=skip, limit=limit, query=query)

#get 7 digit postcode details
@app.get("/postcode/{fourdigit}/{threedigit}/", response_model=None)
def read_postcode_details(fourdigit: str='', threedigit: str='', db: Session = Depends(get_db)):
    return crud.get_postcode_details(db=db, fourdigit=fourdigit, threedigit=threedigit)

# @app.get("/country/{slug}/", response_model=None)
# def read_country(slug: str, db: Session = Depends(get_db)):
#     return crud.get_country(db=db, slug = slug)

# @app.get("/{country_slug}/{county_slug}/", response_model=None)
# def read_county(country_slug: str, county_slug:str, db: Session = Depends(get_db)):
#     return crud.get_county(db=db, country_slug = country_slug, county_slug=county_slug )


# @app.get("/postcode/{id}/", response_model=None)
# def read_postcode_by_id(id: int, db: Session = Depends(get_db)):
#     return crud.get_postcode(db=db, post_code_id = id)

# @app.post("/postcodes/", response_model=schemas.Postcode)
# def create_postcode(postcode: schemas.PostcodeCreate, db: Session = Depends(get_db)):
#     return crud.create_postcode(db=db, postcode=postcode)
#
# @app.get("/cities/{city_id}", response_model=schemas.City)
# def read_city(city_id: int, db: Session = Depends(get_db)):
#     db_city = crud.get_city(db=db, city_id=city_id)
#     if db_city is None:
#         raise HTTPException(status_code=404, detail="City not found")
#     return db_city
