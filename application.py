from app import create_app
from app.helpers.validation import setUrl
from flask_restful import reqparse

application = create_app()


@application.before_request
def before_request_callback():  
    parser = reqparse.RequestParser()
    parser.add_argument('zinc_id', type=str)
    args = parser.parse_args()
    zinc_id = args.get('zinc_id')  
    if zinc_id:
        setUrl(zinc_id)


if __name__ == '__main__':
    application.debug = True
    application.run()
    # application.run(debug=True, host='0.0.0.0', port=5077)
