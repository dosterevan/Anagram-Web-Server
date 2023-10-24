"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made
from a scrambled string)
"""

import flask
from flask import jsonify, request
import logging

# Our modules
from src.letterbag import LetterBag
from src.vocab import Vocab
from src.jumble import jumbled
import src.config as config


###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

WORDS = Vocab(CONFIG.VOCAB)
SEED = CONFIG.SEED
try:
    SEED = int(SEED)
except ValueError:
    SEED = None


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    flask.g.vocab = WORDS.as_list()
    flask.session["target_count"] = min(
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(
        flask.g.vocab, flask.session["target_count"], seed=None if not SEED or SEED < 0 else SEED)
    flask.session["matches"] = []
    app.logger.debug("Session variables have been set")
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


@app.route("/_keep_going")
def keep_going():
    flask.g.vocab = WORDS.as_list()

    #jumble = flask.session["jumble"]
    text = request.args.get("text", type=str)

    #in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)

    #match = (matched and in_jumble)

    app.logger.debug("Got a JSON request")
    rslt = {"matched": matched}
    app.logger.debug(print(rslt))
    return flask.jsonify(result=rslt)

@app.route("/success")
def success():
    return flask.render_template('success.html')


#######################
# Form handler.
#   You'll need to change this to a
#   a JSON request handler
#######################

@app.route("/_check")
def check():
    """
    User has submitted the form with a word ('attempt')
    that should be formed from the jumble and on the
    vocabulary list.  We respond depending on whether
    the word is on the vocab list (therefore correctly spelled),
    made only from the jumble letters, and not a word they
    already found.
    """
    app.logger.debug("Entering check")

    # The data we need, from form and from cookie 
    text = request.args.get("text", type=str)
    jumble = flask.session["jumble"]
    matches = flask.session.get("matches", [])  # Default to empty list

    # Is it good?
    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)
    result = len(matches) >= flask.session["target_count"]  #Our goal

    # layout of general JSON format
    response_data = {
        'result': False,
        'redirect_url': False,
        'matches': matches,
        'target' : flask.session["target_count"],
        'message': None
    }
    
    # Respond appropriately
    if result:
        # If result is met, then we set our url to success
        message = "Congrats you solved it, press any character to continue!"
        return flask.jsonify(message = message, redirect_url = flask.url_for("success"), result = True)
    elif matched and in_jumble and not (text in matches):
        # Cool, they found a new word
        response_data['message'] = "Congrats you found the match: {}. Clear the box to continue".format(text)
        matches.append(text)
        flask.session["matches"] = matches
        return flask.jsonify(response_data)
    elif text in matches:
        # We already found this word
        response_data['message'] = "You already found {}".format(text)
        app.logger.debug(print(response_data))
        return flask.jsonify(response_data)
    elif not matched:
        # Word is not in lsit
        response_data['message'] = "{} isn't in the list of words".format(text)
        return flask.jsonify(response_data)
    elif not in_jumble:
        # 
        response_data['message'] = '"{}" can\'t be made from the letters {}'.format(text, jumble)
        return flask.jsonify(response_data)
    else:
        app.logger.debug("This case shouldn't happen!")
        assert False  # Raises AssertionError


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


#############

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0", debug=CONFIG.DEBUG)
