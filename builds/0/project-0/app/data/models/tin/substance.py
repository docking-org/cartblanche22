from app import db
from app.helpers.validation import base62, get_basic_tranche, get_compound_details, get_new_tranche
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func
from sqlalchemy.orm import load_only
import random
import sqlalchemy as sa
from app.data.models.tin.tranches_mapping import Tranches
from app.data.models.tin.catalog import CatalogSubstanceModel

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

    catalog_contents = db.relationship("CatalogContentModel",
                                       secondary="catalog_substance",
                                       backref="substances",
                                       lazy='joined')
    tranche_id = db.Column('tranche_id', db.Integer)

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
        offset = abs(int(count * random.random())-int(limit))
        return cls.query.offset(offset).limit(limit)

    @classmethod
    def get_random3(cls, limit):
        offset = func.floor(func.random() * 100)
        return cls.query.offset(offset).limit(limit)

    @classmethod
    def find_by_sub_id(cls, sub_id):
        return cls.query.filter_by(sub_id=sub_id).first()

    @hybrid_property
    def zinc_id(self):
        if self.tranche:
            return "ZINC{}{}{}".format(self.tranche['mwt'], self.tranche['logp'], base62(self.sub_id).zfill(10))
        return "Unknown"

    @hybrid_property
    def tranche(self):
        if self.tranche_id:
            tranchee = Tranches.query.filter_by(tranche_id=self.tranche_id).first()
            return get_new_tranche(tranchee.tranche_name)
        return get_basic_tranche(self.smiles)

    def json_ids(self):
        return {
            'zinc_id': self.zinc_id,
            'smiles': self.smiles
        }

    def json(self):
        return {
            'tranche': self.tranche,
            'zinc_id': self.zinc_id,
            'sub_id': self.sub_id,
            'smiles': self.smiles,
            'supplier_code': [c.supplier_code for c in self.catalog_contents],
            'catalogs': [c.catalog.json() for c in self.catalog_contents],
            'tranche_details': get_compound_details(self.smiles),
            'tranche_id': self.tranche_id
        }

    def json2(self):
        return {
            'tranche': self.tranche,
            'zinc_id': self.zinc_id,
            'sub_id': self.sub_id,
            'smiles': self.smiles
        }

    def json_all(self, tin_url):
        res = {
            'sub_id': self.sub_id,
            'zinc_id': self.zinc_id,
            'smiles': self.smiles,
            'inchikey': str(self.inchikey).strip(),
            'purchasable': self.purchasable,
            'supplier_code': [c.supplier_code for c in self.catalog_contents],
            'catalogs': [c.catalog.json() for c in self.catalog_contents],
            'server': tin_url
            # 'logp': self.logp
        }

        return {**res, **self.tranche}

