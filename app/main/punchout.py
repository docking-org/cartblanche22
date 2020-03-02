from flask import Response, request, current_app, redirect, jsonify, url_for
from flask_login import current_user, login_user
from app.main import application
import xmltodict
from app.data.models.users import Users
from time import time
import jwt
from app import db
import datetime
import string
import random


@application.route('/punchoutOrder', methods= ['GET'])
def punchoutOrder():
    randStr = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
    data = genProlog("1.0", randStr)
    data += '''
<Header>
    <From>
        <Credential domain='DUNS'>
            <Identity>-YOUR IDENTITY-</Identity>
        </Credential>
    </From>
<To>
    <Credential domain='NetworkID'>
        <Identity>-YOUR IDENTITY-</Identity>
    </Credential>
</To>
<Sender>
    <Credential domain='NetworkId'>
        <Identity>smartbuy</Identity>
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
            itemId = "<ItemID><SupplierPartID>'{}'</SupplierPartID></ItemID>".format(vendor.supplier_code)
            itemDetail = "<ItemDetail><ManufacturerName>'{}'</ManufacturerName><UnitPrice><Money currency='USD'>'{}'</Money></UnitPrice><Description xml:lang='en'>pack size of {}{} of {}</Description><UnitOfMeasure>EA</UnitOfMeasure><Classification domain='UNSPSC'>12350000</Classification></ItemDetail>".format(vendor.cat_name,  vendor.price, vendor.pack_quantity, vendor.unit, item.identifier)
            message = message + itemIn + itemId + itemDetail + '</ItemIn>'
    message += '</PunchOutOrderMessage></Message>'
    data += message
    data += '</cXML>'
    # main = '<input type="hidden" name="cxml-urlencoded" value="' + data + '">'
    return Response( data, mimetype='text/xml')

@application.route('/punchoutSetup', methods= ['POST'])
def punchoutSetup():
    xml_data = request.get_data()
    content_dict = xmltodict.parse(xml_data)
    cookie = content_dict['cXML']['Request']['PunchOutSetupRequest']['BuyerCookie']
    url = content_dict['cXML']['Request']['PunchOutSetupRequest']['SupplierSetup']['URL']
    identity = content_dict['cXML']['Header']['Sender']['Credential']['Identity']
    password = content_dict['cXML']['Header']['Sender']['Credential']['SharedSecret']
    print(password)
    print(cookie, url)
    randStr = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
    data = genProlog("1.0", randStr)
    user = Users.query.filter_by(username=identity).first()
    if user is None or not user.check_password(password):
        print('Invalid username or password')
        data += '''
        <Response>
        <Status code="400" Text="Bad Request">Invalid Document. Something wrong with finding associated user.</Status>
        </Response>
        </cXML>'''
        return Response(data, mimetype='text/xml')
    print(user)
    token = jwt.encode(
            {'user_id': user.id, 'exp': time() + 1800},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    print(token)
    data += '''
    <Response>
    <Status code="200" text="OK"/>
    <PunchOutSetupResponse>
    <StartPage>
     '''
    url = ''.join(['<URL>https://cartblanche.docking.org/punchoutStart/',token, '</URL>'])
    # test = 'https://cartblanche.docking.org/punchoutStart/' + token
    print(url)
    data += url
    data += '''
    </StartPage>
    </PunchOutSetupResponse>
    </Response>
    </cXML>
    '''
    return Response(data, mimetype='text/xml')
    
@application.route('/punchoutStart/<token>', methods= ['GET', 'POST'])
def punchoutStart(token):
    # # decoding token
    print(token)
    try:
        user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
        user = Users.query.get(user_id)
        login_user(user)
        print(current_user)
        return redirect(url_for('main.sw'))
    except:
        return jsonify('something wrong with starting the page, token expired or user not found')

def genProlog(cXMLvers, randStr):
    vers = "1.2.014";
    sysID = "http://xml.cXML.org/schemas/cXML/" + vers + "/cXML.dtd";
    dt = datetime.datetime.now()
    nowNum = int(round(time()*1000))
    timeStr = dt.strftime("%y-%m-%dT%H:%M:%S")
    data = '<?xml version="1.0" encoding="UTF-8"?>\n';
    data += '<!DOCTYPE cXML SYSTEM "' + sysID + '">\n';
    data += '<cXML payloadID="' + str(nowNum) + ".";
    data += randStr + '@' + 'www.cartblanche.docking.org';
    data += '" timestamp="' + timeStr + '">';
    return data;
