# from flask import Flask,render_template
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello():
#     return render_template('index.html')
#
# # this below @app.route is route end point in flask
# @app.route('/about')
# def about():
#     win = "I will win soon"
#     return render_template('about.html',message = win)
# # return variable through render_template module and render template also through above way
#
# @app.route('/bootstrap')
# def boot():
#
#     return render_template('bootstrap.html')
# # return variable through render_template module and render template also through above way
#
#
# app.run(debug=True)