from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, and_ , or_
import models, schemas
from fastapi import HTTPException
from typing import Optional




#get 4 digit post codes /postcode/
def get_fourpostcode(db: Session, skip: int = 0, limit: int = 20, query: str =''):
    if query!='':
        return db.query(models.Fourdigit).filter(models.Fourdigit.code.contains(query.lower())).offset(0).limit(80).all()
    return db.query(models.Fourdigit).offset(skip).limit(limit).all()

#get 3 digit post codes /postcode/{slug}/
def get_threepostcode(db: Session, fourdigit: str = '', skip: int = 0, limit: int = 20, query: str = ''):
    if query!='':
        return db.query(models.Threedigit).filter(models.Threedigit.code.contains(query.lower())).offset(0).limit(80).all()
    fourdigit_record = db.query(models.Fourdigit).filter(models.Fourdigit.code == fourdigit).first()
    if not fourdigit_record:
        raise HTTPException(status_code=404, detail="Outcode not found")
    threedigit_ids = db.query(models.Postcode.threedigit_id).filter(models.Postcode.fourdigit_id == fourdigit_record.id).distinct().all()
    threedigit_ids = [result[0] for result in threedigit_ids]
    if not threedigit_ids:
        return []
    final_query = db.query(models.Threedigit).filter(models.Threedigit.id.in_(threedigit_ids)).offset(skip).limit(limit)

    return final_query.all()
    

#get 7 digit postcode details /postcode/{fourdigit}/{threedigit}/
def get_postcode_details(db: Session, fourdigit: str='', threedigit: str=''):
    fourdigit_record = db.query(models.Fourdigit).filter(models.Fourdigit.code == fourdigit).first()
    if not fourdigit_record:
        return []
    threedigit_record = db.query(models.Threedigit).filter(models.Threedigit.code == threedigit).first()
    if not threedigit_record:
        return []

    return db.query(models.Postcode).options(
        joinedload(models.Postcode.ward)
        .joinedload(models.Ward.district)
        .joinedload(models.District.county)
        .joinedload(models.County.country)).filter(and_(
        models.Postcode.fourdigit_id==fourdigit_record.id,
        models.Postcode.threedigit_id==threedigit_record.id)).first()

#get_postcodes_by_area /area/{code}/
def get_postcode_by_areacode(db: Session, skip, limit, slug):
    return db.query(models.Fourdigit).filter(models.Fourdigit.code.startswith(slug)).offset(skip).limit(limit).all()


#county by country /{country}/
def get_county(db: Session, country: str):
    return db.query(models.Country).options(
        joinedload(models.Country.counties)
    ).filter(models.Country.slug == country).first()

#district by country/county
def get_district(db: Session, country: str, county: str):
    country_record = db.query(models.Country).filter(models.Country.slug == country).first()
    if not country_record:
        raise HTTPException(status_code=404, detail="Not found")
    return db.query(models.County).options(
        joinedload(models.County.districts)
    ).filter(and_(models.County.slug == county, models.County.country_id == country_record.id)).first()
#ward by country/county/district 
def get_ward(db: Session, country: str, county: str, district: str):
    country_record = db.query(models.Country).filter(models.Country.slug == country).first()
    if not country_record:
        raise HTTPException(status_code=404, detail="Not found")
    county_record = db.query(models.County).filter(and_(models.County.slug == county,
      models.County.country_id == country_record.id)).first()
    if not county_record:
        raise HTTPException(status_code=404, detail="Not found")

    return db.query(models.District).options(
        joinedload(models.District.wards)
    ).filter(and_(models.District.county_id == county_record.id,
    models.District.slug == district)).first()

#postcodes by country/county/district/ward

# def get_postcodes(db: Session, country: str, county: str, district: str, ward: str):
#     country_record = db.query(models.Country).filter(models.Country.slug == country).first()
#     if not country_record:
#         return []
#     county_record = db.query(models.County).filter(and_(models.County.slug == county,
#       models.County.country_id == country_record.id)).first()
#     if not county_record:
#         return []
#     distinct_record = db.query(models.District).filter(and_(models.District.slug == district,
#       models.District.county_id == county_record.id)).first()
#     if not distinct_record:
#         return []
    
#     return db.query(models.Ward).options(
#         joinedload(models.Ward.postcodes)
#         .joinedload(models.Postcode.fourdigit),
#         joinedload(models.Ward.postcodes)
#         .joinedload(models.Postcode.threedigit)
#     ).filter(and_(models.Ward.slug == ward,
#     models.Ward.district_id == distinct_record.id)).first()
#optimized previous one 

def get_postcodes(db: Session, country: str, county: str, district: str, ward: str) -> Optional[models.Ward]:
    stmt = select(models.Ward).options(
        selectinload(models.Ward.postcodes).selectinload(models.Postcode.fourdigit),
        selectinload(models.Ward.postcodes).selectinload(models.Postcode.threedigit)
    ).join(models.District).join(models.County).join(models.Country).where(
        and_(
            models.Country.slug == country,
            models.County.slug == county,
            models.District.slug == district,
            models.Ward.slug == ward
        )
    )
    return db.execute(stmt).scalar_one_or_none()



# Get search results
def get_search_results(db: Session, skip: int, limit: int, query: str, querytype: str):
    query_parts = query.lower().replace(' ', ' ').split(' ')
    query1 = query_parts[0] if len(query_parts) > 0 else ''
    query2 = query_parts[1] if len(query_parts) > 1 else ''
    if querytype == 'postcode':
        fourdigit_results = db.query(models.Fourdigit).filter(models.Fourdigit.code.ilike(f"{query1}%")).all()
        threedigit_results = db.query(models.Threedigit).filter(models.Threedigit.code.ilike(f"{query2}%")).all()
        postcodes = db.query(models.Postcode).join(models.Fourdigit).join(models.Threedigit)
        if fourdigit_results:
            postcodes = postcodes.filter(models.Postcode.fourdigit_id.in_([f.id for f in fourdigit_results]))
        if threedigit_results:
            postcodes = postcodes.filter(models.Postcode.threedigit_id.in_([t.id for t in threedigit_results]))
        results = postcodes.offset(skip).limit(limit).all()
        return [
            {
                "fourdigit": result.fourdigit.code,
                "threedigit": result.threedigit.code
            } for result in results
        ]
    else:
        return {"error": "Invalid query type"}