from app import db
import sqlalchemy
from sqlalchemy.ext.associationproxy import association_proxy

class SubstanceModel(db.Model):
    __bind_key__ = 'tin'
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
    def find_by_sub_id(cls, sub_id):
        return cls.query.filter_by(sub_id=sub_id).first()

    def json(self):
        return {'sub_id': self.sub_id, 'smiles': self.smiles, 'supplier_code': [ c.supplier_code for c in self.catalogs], 'catalogs': [ c.catalog.json() for c in self.catalogs]}

    def json2(self, zinc_id):
        return {'zinc_id': zinc_id, 'sub_id': self.sub_id, 'smiles': self.smiles, 'supplier_code': [ c.supplier_code for c in self.catalogs], 'catalogs': [ c.catalog.json() for c in self.catalogs]}