from cartblanche.app import db


class CatalogModel(db.Model):
    #__bind_key__ = 'tin'
    __tablename__ = 'catalog'

    cat_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    version = db.Column(db.String)
    short_name = db.Column(db.String)
    free = db.Column(db.Boolean)
    purchasable = db.Column(db.Integer)


    def __init__(self, cat_id=None, short_name=None, name=None):
        self.cat_id = cat_id
        self.name = name
        self.short_name = short_name

    def json(self):
        return {'catalog_name': self.name, 'short_name': self.short_name}

    def json2(self):
        return {
            '
            ': self.name,
            'version': self.version,
            'short_name': self.short_name,
            'free': self.free,
            'purchasable': self.purchasable
        }

    @property
    def token(self):
        return self.short_name.rstrip()

    def __repr__(self):
        return "Catalog({0}, '{2}')".format(self.cat_id, self.token)

    def __str__(self):
        return self.name


class CatalogContentModel(db.Model):
    #__bind_key__ = 'tin'
    __tablename__ = 'catalog_content'


    cat_content_id = db.Column(db.BigInteger, primary_key=True)
    cat_id_fk = db.Column(db.BigInteger,db.ForeignKey('catalog.cat_id'))
    catalog = db.relationship('CatalogModel', backref=db.backref('catalog_content'))

    supplier_code = db.Column(db.String, index=True, nullable=False)
    depleted = db.Column(db.Boolean, default=False)
    
    # substances = db.relationship("SubstanceModel", secondary="catalog_substance", back_populates="catalog_contents")


class CatalogSubstanceModel(db.Model):
    #__bind_key__ = 'tin'
    __tablename__ = 'catalog_substance'

    cat_sub_itm_id = db.Column(db.BigInteger, primary_key=True)
    cat_content_fk = db.Column(db.BigInteger, db.ForeignKey('catalog_content.cat_content_id'))
    sub_id_fk = db.Column(db.BigInteger, db.ForeignKey('substance.sub_id'))

    # substance = db.relationship(SubstanceModel, backref=db.backref('catalog_substance', uselist=False))
    # catalog_content = db.relationship(CatalogContentModel, backref=db.backref('catalog_substance', uselist=False))






