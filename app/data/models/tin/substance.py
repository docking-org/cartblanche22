from app import db
from sqlalchemy.ext.associationproxy import association_proxy
from app.helpers.validation import base62
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func
from sqlalchemy.orm import load_only
import random
import sqlalchemy as sa

TABLE_ROW_COUNT_SQL = \
    """ SELECT CAST(reltuples AS BIGINT) AS num_rows
        FROM pg_catalog.pg_class
        WHERE oid = CAST(:table AS pg_catalog.regclass)
    """


class SubstanceModel(db.Model):
    #__bind_key__ = 'tin'
    __tablename__ = 'substance'

    sub_id = db.Column(db.BigInteger, primary_key=True, nullable=False,
                    doc="A numeric (integer) representation of ZINC ID")
    smiles = db.Column(db.String(), 
                       unique=True, nullable=False,
                       doc="A query-enabled molecular structure (use the contains and match operators)")
    inchikey = db.Column('inchikey', db.CHAR(27), unique=True, nullable=False,
                      doc="The Substance's InChI key")
    purchasable = db.Column('purchasable', db.Integer, default=-1, nullable=True,
                         server_default='0',
                         doc="A numeric representation of the commercial availability of this compound "
                             "(high is better)")
    date_updated = db.Column(db.Date, nullable=True)

    catalogs = db.relationship("CatalogContentModel",  secondary="catalog_substance")

    @classmethod
    def get_random(cls, limit):
        return cls.query.options(load_only('sub_id')).offset(
            func.floor(
                func.random() *
                db.session.query(func.count(cls.sub_id))
            )
        ).limit(limit).all()

    @classmethod
    def get_random2(cls, limit):
        rowcount_query = sa.text(TABLE_ROW_COUNT_SQL)
        count = db.session.connection().execute(rowcount_query, table='substance').scalar()
        print("Row Count: ===========================================", count)
        offset = int(count * random.random())-int(limit)
        return cls.query.offset(offset).limit(limit)

    @classmethod
    def find_by_sub_id(cls, sub_id):
        return cls.query.filter_by(sub_id=sub_id).first()

    @hybrid_property
    def base62(self):
        return base62(self.sub_id)

    def json2(self, zinc_start):
        return {
            'zinc_id': "{}{}".format(zinc_start, self.base62),
            'sub_id': self.sub_id,
            'smiles': self.smiles,
            'supplier_code': [c.supplier_code for c in self.catalogs],
            'catalogs': [c.catalog.json() for c in self.catalogs]
        }

    def json_ids(self):
        return {
            'sub_id': self.sub_id,
            'smiles': self.smiles
        }

    def json(self):
        return {
            'sub_id': self.sub_id,
            'smiles': self.smiles,
            'supplier_code': [c.supplier_code for c in self.catalogs],
            'catalogs': [c.catalog.json() for c in self.catalogs]
        }
