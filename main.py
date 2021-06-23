from flask import Flask , jsonify, request
from werkzeug.exceptions import abort
from flask_restful import Api,Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy,Model

app=Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)

#  DB Model to define the column of the Db.

class VideoModel(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    views=db.Column(db.Integer, nullable=False)
    likes=db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"This is DB"

#  Just the first time
# db.create_all()

names={"tim": {"age": 19, "gender": "Male"},
        "bob": {"age": 43, "gender": "Female"},
        "Chill": {"age": 61, "gender": "Male"},
}

#  Similar to WTforms for Input via arguments
video_put_args=reqparse.RequestParser()
video_put_args.add_argument('name', type=str, help='Name of video')
video_put_args.add_argument('views', type=int, help='Views of video')
video_put_args.add_argument('likes', type=int, help='Likes of video is required', required= True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument('name', type=str, help='Name of video')
video_update_args.add_argument('views', type=int, help='Views of video')
video_update_args.add_argument('likes', type=int, help='Likes of video is required')


video_l={ 1: {"name": "Stereo hearts" , "Duration": "5 mins 20 secs"},
         2: {"name": "Amstradam" , "Duration": "3 mins 15 secs"},
         3: {"name": "Castle of glass" , "Duration": "3 mins 15 secs"},}

videos={}

# ==========================================================================================

# Custom Abort.

def abort_if_videoid_doesnt_exist(video_id):
    if video_id not in videos:
        abort(404, message ="Video Id is Invalid...")


def abort_if_videoid_already_exist(video_id):
    if video_id in videos:
        abort(409, message ="Video Id already Exists...")

# ==========================================================================================

# Using Dictionary as Db.

class Video2(Resource):
    def get(self,video_id):
        abort_if_videoid_doesnt_exist(video_id)
        return videos[video_id]

    def post(self,video_id):
        abort_if_videoid_already_exist(video_id)
        args = video_put_args.parse_args()
        videos[video_id]=args
        return videos[video_id], 201

    def delete(self,video_id):
        abort_if_videoid_doesnt_exist(video_id)
        del videos[video_id]
        return '',204

class HelloWorld(Resource):
    def get(self,name):
        return names[name]
    def post(self):
        return {"data":"Posted"}

api.add_resource(HelloWorld,'/helloworld/<string:name>')    
api.add_resource(Video2,'/video2/<int:video_id>')

# ==========================================================================================

# Using Sqlite as DB.

# This helps in json serealization of the output. Ie. it defines how the output or return is to be shown.
resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

class Video(Resource):
    # @marshal_with is a decorator for custom type of output in format "resource_fields".
        @marshal_with(resource_fields)
        def get(self, video_id):
            result = VideoModel.query.filter_by(id=video_id).first()
            if not result:
                abort(404, message="Could not find video with that id")
            return result

        @marshal_with(resource_fields)
        def post(self, video_id):
            args = video_put_args.parse_args()
            result = VideoModel.query.filter_by(id=video_id).first()
            if result:
                abort(409, message="Video id taken...")
            video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
            db.session.add(video)
            db.session.commit()
            return video, 201

        @marshal_with(resource_fields)
        def patch(self,video_id):
            args= video_update_args.parse_args()
            res = VideoModel.query.filter_by(id=video_id).first()
            if not res:
                abort(404, "Video Doesnt exists...")
            if args['name']:
                res.name = args['name']
            if args['views']:
                res.views = args['views']
            if args['likes']:
                res.likes = args['likes']

            db.session.commit()
            return res

        def delete(self,video_id):
            res = VideoModel.query.filter_by(id=video_id).first()
            if not res:
                abort(404, "Video Doesnt exists...")
            VideoModel.query.filter_by(id=video_id).delete()
            db.session.commit()
            return {"Data":"Deleted Successfully"} ,204

api.add_resource(Video,'/video/<int:video_id>')

@app.route('/')
def hello_world():
    return 'Hello, Worl!'

if __name__ == '__main__':
    app.run(debug=True)
