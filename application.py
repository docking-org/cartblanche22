from app import create_app

application = create_app()

if __name__ == '__main__':
    # from gevent import monkey
    # from psycogreen.gevent import patch_psycopg
    #
    # monkey.patch_all(subprocess=True)
    # patch_psycopg()
    application.debug = True
    print("before application run")
    application.run()

