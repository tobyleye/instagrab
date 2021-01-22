from flask import Flask, request
from dotenv import load_dotenv
import logging
import ig

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

@app.route('/api')
def scrape_post():
    url  = request.args.get('url')
    if not url:
        return {'message': 'url is missing'}, 400
    # validate url while attempting to extract the post shortcode from url
    post_shortcode = ig.extract_shortcode_from_url(url)
    if not post_shortcode:
        return { 'message': 'url is invalid' }, 400
    try:
        response = ig.scrape_post(post_shortcode)
        return response
    except Exception as err:
        logging.exception('An internal error occured {}'.format(err))
        return { 'message': 'an unknown error occured', 'error': '{}'.format(err) }, 500
        
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occured during a request')
    return """
        An internal error occured: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

if __name__ == "__main__":
    app.run(debug=True)
