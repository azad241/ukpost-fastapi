from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
models.Base.metadata.create_all(bind=engine)



app = FastAPI()

origins = [
    "https://mydomain.com",
    "http://192.168.0.103:3000",
    "192.168.0.103:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def block_direct_ip_access(request: Request, call_next):
    host = request.headers.get("host")
    # Block access if the request is not through api.mydomain.com
    if host and "api.mydomain.com" not in host:
        return JSONResponse(status_code=403, content={"detail": "Access denied."})
    response = await call_next(request)
    return response



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=None)
def root():
    return {'status':'Working...'}


#Searching
@app.get("/search/", response_model=None)
def read_search_results(query: str = '', querytype: str = 'postcode', skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_search_results(db=db, query = query.lower(), querytype = querytype.lower(), skip=skip, limit=limit)

#get 4digitpostcode
@app.get("/postcode/", response_model=None)
def read_fourpostcode(skip: int = 0, limit: int = 20, query: str = '', db: Session = Depends(get_db)):
    return crud.get_fourpostcode(db=db, skip=skip, limit=limit, query=query)

#get 3digitpostcode by 4digitpostcode
@app.get("/postcode/{slug}/", response_model=None)
def read_threepostcode(slug: str='', skip: int = 0, limit: int = 20, query: str = '', db: Session = Depends(get_db)):
    return crud.get_threepostcode(db=db, fourdigit=slug, skip=skip, limit=limit, query=query)

#get 7 digit postcode details by 4digitpostcode/3digitpostcode
@app.get("/postcode/{fourdigit}/{threedigit}/", response_model=None)
def read_postcode_details(fourdigit: str='', threedigit: str='', db: Session = Depends(get_db)):
    return crud.get_postcode_details(db=db, fourdigit=fourdigit, threedigit=threedigit)

#postcodes by area code(one or two letter)
@app.get("/area/{code}/", response_model=None)
def read_postcode_by_areacode(code: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_postcode_by_areacode(db=db, slug = code.lower(), skip=skip, limit=limit)

#county by country
@app.get("/{country}/", response_model=None)
def read_county(country: str, db: Session = Depends(get_db)):
    return crud.get_county(db=db, country = country)
#district by country/county
@app.get("/{country}/{county}/", response_model=None)
def read_district(country: str, county: str, db: Session = Depends(get_db)):
    return crud.get_district(db=db, country = country, county = county)
#ward by country/county/district 
@app.get("/{country}/{county}/{district}/", response_model=None)
def read_ward(country: str, county: str, district: str, db: Session = Depends(get_db)):
    return crud.get_ward(db=db, country = country, county = county, district = district)
#postcodes by country/county/district/ward
@app.get("/{country}/{county}/{district}/{ward}/", response_model=None)
def read_postcodes(country: str, county: str, district: str, ward: str,  db: Session = Depends(get_db)):
    return crud.get_postcodes(db=db, country = country, county = county, district = district, ward = ward)




