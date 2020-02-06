from flask import Response, request
from flask_login import current_user
from app.main import application
import xmltodict

@application.route('/punchoutOrder', methods= ['GET'])
def res():
    data = '''<!DOCTYPE cXML SYSTEM 'http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd'>
<cXML payloadID='958074737352&amp;www.workchairs.com'
timestamp='2004-06-14T12:59:09-07:00'>
<Header>
<From>
<Credential domain='DUNS'>
<Identity>12345678</Identity>
</Credential>
</From>
<To>
<Credential domain='NetworkID'>
<Identity>AN01000002792</Identity>
</Credential>
</To>
<Sender>
<Credential domain='www.workchairs.com'>
<Identity>PunchoutResponse</Identity>
</Credential>
<UserAgent>Our PunchOut Site V4.2</UserAgent>
</Sender>
</Header>'''
    message = "<Message><PunchOutOrderMessage><BuyerCookie>1J3YVWU9QWMTB</BuyerCookie>"
    PunchOutOrderMessageHeader = "<PunchOutOrderMessageHeader operationAllowed='edit'><Total><Money currency='USD'>'{}'</Money></Total></PunchOutOrderMessageHeader>".format(current_user.totalPrice)
    message += PunchOutOrderMessageHeader
    for item in current_user.items_in_cart:
        for vendor in item.vendors:
            itemIn = "<ItemIn quantity='{}'>".format(vendor.purchase_quantity)
            itemId = "<ItemID><SupplierPartID>'{}'</SupplierPartID><SupplierPartAuxiliaryID>'{}'</SupplierPartAuxiliaryID></ItemID>".format(vendor.supplier_code, vendor.cat_name)
            itemDetail = "<ItemDetail><UnitPrice><Money currency='USD'>'{}'</Money></UnitPrice><Description xml:lang='en'>blablabla</Description><UnitOfMeasure>EA</UnitOfMeasure><Classification domain='UNSPSC'>14111514</Classification></ItemDetail>".format(vendor.price)
            message = message + itemIn + itemId + itemDetail + '</ItemIn>'
    message += '</PunchOutOrderMessage></Message>'
    data += message
    data += "</cXML>"
    print(data)
    return Response(data, mimetype='text/xml')

@application.route('/punchoutSetup', methods= ['POST'])
def test():
    xml_data = request.get_data()
    content_dict = xmltodict.parse(xml_data)
    print(content_dict['cXML']['Header']['From']['Credential']['@domain'])
    data = '''
    <!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML payloadID="958074700772@www.workchairs.com" timestamp="2005-06-14T12:59:09-07:00">
<Response>
<Status code="200" text="success"/>
<PunchOutSetupResponse>
<StartPage>
<URL>http://cartblanche.docking.org</URL>
</StartPage>
</PunchOutSetupResponse>
</Response>
</cXML>
'''

    return Response(data, mimetype='text/xml')
    