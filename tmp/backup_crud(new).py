from sqlalchemy.orm import Session, selectinload, aliased
from sqlalchemy import select, and_, or_
import models, schemas
from fastapi import HTTPException
from typing import List, Optional, Dict

# Get 4 digit post codes /postcode/
def get_fourpostcode(db: Session, skip: int = 0, limit: int = 20, query: str = '') -> List[models.Fourdigit]:
    stmt = select(models.Fourdigit)
    if query:
        stmt = stmt.where(models.Fourdigit.code.contains(query.lower())).limit(80)
    else:
        stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

# Get 3 digit post codes /postcode/{slug}/
def get_threepostcode(db: Session, fourdigit: str = '', skip: int = 0, limit: int = 20, query: str = '') -> List[models.Threedigit]:
    if query:
        stmt = select(models.Threedigit).where(models.Threedigit.code.contains(query.lower())).limit(80)
        return db.execute(stmt).scalars().all()
    
    fourdigit_record = db.execute(select(models.Fourdigit).where(models.Fourdigit.code == fourdigit)).scalar_one_or_none()
    if not fourdigit_record:
        raise HTTPException(status_code=404, detail="Outcode not found")
    
    subquery = select(models.Postcode.threedigit_id).where(models.Postcode.fourdigit_id == fourdigit_record.id).distinct().scalar_subquery()
    stmt = select(models.Threedigit).where(models.Threedigit.id.in_(subquery)).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

# Get 7 digit postcode details /postcode/{fourdigit}/{threedigit}/ #not optimized
def get_postcode_details(db: Session, fourdigit: str = '', threedigit: str = '') -> Optional[models.Postcode]:
    fourdigit_record = db.execute(select(models.Fourdigit).where(models.Fourdigit.code == fourdigit)).scalar_one_or_none()
    threedigit_record = db.execute(select(models.Threedigit).where(models.Threedigit.code == threedigit)).scalar_one_or_none()
    
    if not fourdigit_record or not threedigit_record:
        return None

    stmt = select(models.Postcode).options(
        selectinload(models.Postcode.ward)
        .selectinload(models.Ward.district)
        .selectinload(models.District.county)
        .selectinload(models.County.country)
    ).where(and_(
        models.Postcode.fourdigit_id == fourdigit_record.id,
        models.Postcode.threedigit_id == threedigit_record.id
    ))
    return db.execute(stmt).scalar_one_or_none()

# Get postcodes by area /area/{code}/
def get_postcode_by_areacode(db: Session, skip: int, limit: int, slug: str) -> List[models.Fourdigit]:
    stmt = select(models.Fourdigit).where(models.Fourdigit.code.startswith(slug)).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

# County by country /{country}/
def get_county(db: Session, country: str) -> Optional[models.Country]:
    stmt = select(models.Country).options(
        selectinload(models.Country.counties)
    ).where(models.Country.slug == country)
    return db.execute(stmt).scalar_one_or_none()

# District by country/county
def get_district(db: Session, country: str, county: str) -> Optional[models.County]:
    stmt = select(models.County).options(
        selectinload(models.County.districts)
    ).join(models.Country).where(
        and_(models.Country.slug == country, models.County.slug == county)
    )
    return db.execute(stmt).scalar_one_or_none()

# Ward by country/county/district 
def get_ward(db: Session, country: str, county: str, district: str) -> Optional[models.District]:
    stmt = select(models.District).options(
        selectinload(models.District.wards)
    ).join(models.County).join(models.Country).where(
        and_(
            models.Country.slug == country,
            models.County.slug == county,
            models.District.slug == district
        )
    )
    return db.execute(stmt).scalar_one_or_none()

# Postcodes by country/county/district/ward @optimized than old
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
def get_search_results(db: Session, skip: int, limit: int, query: str, querytype: str) -> List[Dict[str, str]]:
    if querytype != 'postcode':
        return {"error": "Invalid query type"}
    query_parts = query.replace(' ', ' ').split()
    if len(query_parts) == 1:
        outcode_query = f"{query_parts[0]}%"
        incode_query = "%"
    elif len(query_parts) >= 2:
        outcode_query = f"{query_parts[0]}%"
        incode_query = f"{query_parts[1]}%"
    else:
        outcode_query = "%"
        incode_query = "%"
    Fourdigit = aliased(models.Fourdigit)
    Threedigit = aliased(models.Threedigit)
    stmt = (
        select(Fourdigit.code.label('fourdigit'), Threedigit.code.label('threedigit'))
        .select_from(models.Postcode)
        .join(Fourdigit, models.Postcode.fourdigit_id == Fourdigit.id)
        .join(Threedigit, models.Postcode.threedigit_id == Threedigit.id)
        .where(and_(
            Fourdigit.code.ilike(outcode_query),
            Threedigit.code.ilike(incode_query)
        ))
        .offset(skip)
        .limit(limit)
    )
    results = db.execute(stmt).all()

    return [
        {
            "fourdigit": result.fourdigit,
            "threedigit": result.threedigit
        } for result in results
    ]