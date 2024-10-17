from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True)
    iso = Column(String, unique=True)

    # One-to-many relationship with County
    counties = relationship("County", back_populates="country")


class County(Base):
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String)
    code = Column(String)
    country_id = Column(Integer, ForeignKey('countries.id'))

    # One-to-many relationship with District
    districts = relationship("District", back_populates="county")

    # Many-to-one relationship with Country
    country = relationship("Country", back_populates="counties")

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String)
    code = Column(String)
    county_id = Column(Integer, ForeignKey('counties.id'))

    # One-to-many relationship with Ward
    wards = relationship("Ward", back_populates="district")

    # Many-to-one relationship with County and Country
    county = relationship("County", back_populates="districts")

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String)
    code = Column(String)
    district_id = Column(Integer, ForeignKey('districts.id'))

    # One-to-many relationship with Postcode
    postcodes = relationship("Postcode", back_populates="ward")

    # Many-to-one relationship with District
    district = relationship("District", back_populates="wards")

class Fourdigit(Base):
    __tablename__ = "fourdigits"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)

    # One-to-many relationship with Postcode
    fourdigits = relationship("Postcode", back_populates="fourdigit")

class Threedigit(Base):
    __tablename__ = "threedigits"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)

    # One-to-many relationship with Postcode
    threedigits = relationship("Postcode", back_populates="threedigit")
   

class Postcode(Base):
    __tablename__ = "postcodes"

    id = Column(Integer, primary_key=True, index=True)

    fourdigit_id = Column(Integer, ForeignKey("fourdigits.id"))
    threedigit_id = Column(Integer, ForeignKey("threedigits.id"))

    latitude = Column(Float)
    longitude = Column(Float)

    ward_id = Column(Integer, ForeignKey("wards.id"))

    # Many-to-one relationship with Ward
    ward = relationship("Ward", back_populates="postcodes")

    fourdigit =  relationship("Fourdigit", back_populates="fourdigits")
    threedigit =  relationship("Threedigit", back_populates="threedigits")

