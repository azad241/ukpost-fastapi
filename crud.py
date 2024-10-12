from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, select
import models, schemas





#get 4 digit post codes
def get_fourpostcode(db: Session, skip: int = 0, limit: int = 20, query: str =''):
    if query!='':
        return db.query(models.Fourdigit).filter(models.Fourdigit.code.contains(query.lower())).offset(0).limit(80).all()
    return db.query(models.Fourdigit).offset(skip).limit(limit).all()

#get 3 digit post codes
def get_threepostcode(db: Session, fourdigit: str = '', skip: int = 0, limit: int = 20, query: str = ''):
    if query!='':
        return db.query(models.Threeigit).filter(models.Threeigit.code.contains(query.lower())).offset(0).limit(80).all()
    fourdigit_record = db.query(models.Fourdigit).filter(models.Fourdigit.code == fourdigit).first()
    if not fourdigit_record:
        return []
    threedigit_ids = db.query(models.Postcode.threedigit_id).filter(models.Postcode.fourdigit_id == fourdigit_record.id).distinct().all()
    threedigit_ids = [result[0] for result in threedigit_ids]
    if not threedigit_ids:
        return []
    final_query = db.query(models.Threeigit).filter(models.Threeigit.id.in_(threedigit_ids)).offset(skip).limit(limit)

    return final_query.all()

#get 7 digit postcode details
def get_postcode_details(db: Session, fourdigit: str='', threedigit: str=''):
    fourdigit_record = db.query(models.Fourdigit).filter(models.Fourdigit.code == fourdigit).first()
    if not fourdigit_record:
        return []
    threedigit_record = db.query(models.Threeigit).filter(models.Threeigit.code == threedigit).first()
    if not threedigit_record:
        return []

    return db.query(models.Postcode).options(
        joinedload(models.Postcode.ward)
        .joinedload(models.Ward.district)
        .joinedload(models.District.county)
        .joinedload(models.County.country)).filter(and_(
        models.Postcode.fourdigit_id==fourdigit_record.id,
        models.Postcode.threedigit_id==threedigit_record.id)).first()
#county by country
def get_county(db: Session, country: str):
    return db.query(models.Country).options(
        joinedload(models.Country.counties)
    ).filter(models.Country.slug == country).first()
#district by country/county
def get_district(db: Session, country: str, county: str):
    country_record = db.query(models.Country).filter(models.Country.slug == country).first()
    if not country_record:
        return []
    return db.query(models.County).options(
        joinedload(models.County.districts)
    ).filter(and_(models.County.slug == county, models.County.country_id == country_record.id)).first()
#ward by country/county/district 
def get_ward(db: Session, country: str, county: str, district: str):
    country_record = db.query(models.Country).filter(models.Country.slug == country).first()
    if not country_record:
        return []
    county_record = db.query(models.County).filter(and_(models.County.slug == county,
      models.County.country_id == country_record.id)).first()
    if not county_record:
        return []

    return db.query(models.District).options(
        joinedload(models.District.wards)
    ).filter(and_(models.District.county_id == county_record.id,
    models.District.slug == district)).first()

#postcodes by country/county/district/ward
def get_postcodes(db: Session, country: str, county: str, district: str, ward: str):
    country_record = db.query(models.Country).filter(models.Country.slug == country).first()
    if not country_record:
        return []
    county_record = db.query(models.County).filter(and_(models.County.slug == county,
      models.County.country_id == country_record.id)).first()
    if not county_record:
        return []
    distinct_record = db.query(models.District).filter(and_(models.District.slug == district,
      models.District.county_id == county_record.id)).first()
    if not distinct_record:
        return []
    
    return db.query(models.Ward).options(
        joinedload(models.Ward.postcodes)
        .joinedload(models.Postcode.fourdigit),
        joinedload(models.Ward.postcodes)
        .joinedload(models.Postcode.threedigit)
    ).filter(and_(models.Ward.slug == ward,
    models.Ward.district_id == distinct_record.id)).first()


