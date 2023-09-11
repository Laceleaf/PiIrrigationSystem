from flask import Flask, render_template, Response
import picamera
import time
import io


app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    with picamera.PiCamera() as camera:
        camera.resolution=(640, 480)
        camera.framerate=30

        while True:
            frame=io.BytesIO()
            camera.capture(frame, 'jpeg', use_video_port=True)
            yield(b'--frame\r\n'b'content-Type: image/jpeg\r\n\r\n' + frame.getvalue() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(host='169.254.170.93', port=5000, debug=True)
