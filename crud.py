from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, select
import models, schemas





#get 4 digit post codes
def get_postcode(db: Session, skip: int = 0, limit: int = 20, query: str =''):
    if query!='':
        return db.query(models.Fourdigit).filter(models.Fourdigit.code.contains(query.lower())).offset(0).limit(80).all()
    return db.query(models.Fourdigit).offset(skip).limit(limit).all()

#get 3 digit post codes
def get_postcode_by_fourdigit(db: Session, fourdigit: str = '', skip: int = 0, limit: int = 20, query: str = ''):
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





# def get_county(db: Session, county_slug: str,country_slug: str, ):
#     return db.query(models.County).options(
#         joinedload(models.County.districts)
#     ).filter(models.County.slug == county_slug, models.Country.slug==country_slug).first()

# def get_postcode(db: Session, post_code_id: int):
#     return db.query(models.Postcode).options(
#         joinedload(models.Postcode.ward)
#         .joinedload(models.Ward.district)
#         .joinedload(models.District.county)
#         .joinedload(models.County.country)
#     ).filter(models.Postcode.id == post_code_id).first()

# def get_postcode_by_code(db: Session, fourdigits: str, threedigits: str):
#     fourdigit_record = db.query(models.Fourdigit).filter(models.Fourdigit.code == fourdigits).first()
#     if not fourdigit_record:
#         return None
#     threedigit_record = db.query(models.Threeigit).filter(models.Threeigit.code == threedigits).first()
#     if not threedigit_record:
#         return None

#     return db.query(models.Postcode).options(
#         joinedload(models.Postcode.ward)
#         .joinedload(models.Ward.district)
#         .joinedload(models.District.county)
#         .joinedload(models.County.country)
#     ).filter(
#         and_(
#             models.Postcode.fourdigit_id == fourdigit_record.id,
#             models.Postcode.threedigit_id == threedigit_record.id
#         )
#     ).first()

# def get_ward(db: Session, ward_slug: int):
#     return db.query(models.ward).options(
#         joinedload(models.Ward.district)
#         .joinedload(models.District.county)
#         .joinedload(models.County.country)
#     ).filter(models.Ward.slug == ward_slug).first()