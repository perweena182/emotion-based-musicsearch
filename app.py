from flask import Flask, request, jsonify
import cv2
import numpy as np
from keras.models import model_from_json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
#app = Flask(__name__)
from flask_cors import CORS
import base64

app = Flask(__name__)
#CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})
# ... rest of your Flask code



import os

# Get the directory of the current script
script_directory = os.path.dirname(os.path.realpath(__file__))

# Construct the full path to the model.json file in the parent directory
json_file_path = os.path.join(script_directory, '..', 'model.json')

# Now open the file using the correct path
with open(json_file_path, 'r') as json_file:
    loaded_model_json = json_file.read()

# Load emotion detection model
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
#json_file = open('model.json', 'r')
#loaded_model_json = json_file.read()
#json_file.close()
model = model_from_json(loaded_model_json)
#model.load_weights("model.h5")
model.load_weights(os.path.join(script_directory, '..', 'model.h5'))




    # Initialize Spotify API
client_id = '5f71389d89ad4360be90c4546d1dec91'
client_secret = 'a438326b731b47dd8b925172f5ff865a'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
class MusicRecommender:
    def __init__(self, client_id, client_secret):
        self.emotion_genre_mapping = {
            'happy': ['pop', 'upbeat', 'dance'],
            'sad': ['ballad', 'acoustic', 'slow'],
            #'energetic': ['rock', 'electronic', 'hip-hop'],
            #'relaxed': ['jazz', 'ambient', 'chill']
            'disgusted': ['metal', 'rock', 'heavy-metal'],
            'fearful': ['ambient', 'motivating', 'scared'],
            'neutral': ['slow', 'alone', 'ambient'],
            'angry': ['calm', 'chill', 'alone'],
            'surprised': ['classical', 'surprise', 'pop']
            # Add more emotions and corresponding genres as needed
        }

        # Set up Spotify API authentication
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    def recommend_music(self, emotion, num_tracks=10, language='Any', singer='Any'):
        emotion = emotion.lower()
        if emotion in self.emotion_genre_mapping:
            genres = self.emotion_genre_mapping[emotion]
            if language != 'Any':
                genres.append(language.lower())
            #     #genres.append(f'language:{language.lower()}')

            # if singer != 'Any':
            #     genres.append(singer.lower())
            #     #genres.append(f'artist:{singer.lower()}')
            #     #query = f'artist:{singer.lower()}'
            #     #print(f"Spotify API Query: {query}") 
      


            recommendations = set()  # Use a set to ensure unique tracks

            # Make requests to the Spotify API with different genres until we have enough unique tracks
            while len(recommendations) < num_tracks:
                random.shuffle(genres)
                recommended_genre = genres[0]
                query = f"{recommended_genre}"
                if language != 'Any':
                    query += f"{language.lower()}song"
                # if singer != 'Any':
                #     query += f" artist:{singer.lower()}"
                # #query = f"genre:{recommended_genre}{singer.lower()}"
                print(f"Spotify API Query: {query}") 
                results = self.sp.search(q=query, type='track', limit=num_tracks)

                if results['tracks']['items']:
                    for track_item in results['tracks']['items']:
                        track_name = track_item['name']
                        artist_name = track_item['artists'][0]['name']
                        track_url = track_item['external_urls']['spotify']

                        album_images = track_item['album']['images']
                        thumbnail_url = album_images[0]['url'] if album_images else None

                        # Use a tuple to represent a track and add it to the set
                        track_tuple = (track_name, artist_name, track_url, thumbnail_url)
                        recommendations.add(track_tuple)

            # Convert the set back to a list
            recommendations = list(recommendations)[:num_tracks]

            # Extract information from the tuple for each recommendation
            recommendations_data = [{
                'track_name': track_tuple[0],
                'artist_name': track_tuple[1],
                'track_url': track_tuple[2],
                'thumbnail_url': track_tuple[3]
            } for track_tuple in recommendations]
            for recommendation in recommendations_data:
                query = f'{recommendation["artist_name"]} {recommendation["track_name"]} song'
                youtube_link = self.get_youtube_link(query)
                recommendation['youtube_link'] = youtube_link

            return {
                'recommended_genre': recommended_genre,
                'recommendations': recommendations
            }
        else:
            return {"error": "Sorry, I don't have recommendations for that emotion."}

    def get_youtube_link(self, query):
        youtube = build('youtube', 'v3', developerKey='AIzaSyB85hkTfmkYVayM65i6xXoyZ7dkgUirtiE')

        try:
            # Search for videos on YouTube
            search_response = youtube.search().list(
                q=query,
                type='video',
                part='id',
                maxResults=1
            ).execute()

            # Extract the video ID from the search results
            video_id = search_response['items'][0]['id']['videoId']

            # Construct the YouTube video URL
            youtube_link = f'https://www.youtube.com/watch?v={video_id}'

            return youtube_link
        except HttpError as e:
            print(f'YouTube API Error: {e}')
    #         return None
    

    




@app.route('/api/capture-emotion', methods=['POST'])
def capture_emotion():

    print('Received request to /api/capture-emotion')
    selected_language = request.json.get('selectedLanguage', 'Any')
    selected_singer = request.json.get('selectedSinger', 'Any')
    print('Received Language:', selected_language)

    cap = cv2.VideoCapture(0)

   
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    
    max_iterations = 10
    current_iteration = 0

    
    captured_emotion = None
    captured_frame = None

    
    #while current_iteration < max_iterations:
    while True:
        print(f'Current Iteration: {current_iteration}')
        
        ret, frame = cap.read()

        
        if not ret:
            print("Error: Could not read frame.")
            cap.release()
            exit()

       
        frame = cv2.resize(frame, (1280, 720))

        
        face_detector = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        
        num_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
        #print(f'Number of faces detected: {len(num_faces)}')

        
        for (x, y, w, h) in num_faces:
            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
            roi_gray_frame = gray_frame[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)

          
            emotion_prediction = model.predict(cropped_img)
            maxindex = int(np.argmax(emotion_prediction))
            captured_emotion = emotion_dict[maxindex]

            cv2.putText(frame, captured_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2, cv2.LINE_AA)

        
        cv2.imshow('Emotion Detection', frame)

        
        if captured_emotion is not None:
            captured_frame = frame.copy()
            print("Emotion successfully captured:", captured_emotion)
           # cv2.waitKey(10000)
            break

        
        current_iteration += 1

    
    print("Loop finished")
    if captured_frame is not None:
           #cv2.imwrite('captured_emotion_frame.jpg', captured_frame)
            _, buffer = cv2.imencode('.jpg', captured_frame)
            captured_frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Save the base64-encoded string to a file (optional)
            with open('captured_emotion_frame.txt', 'w') as file:
             file.write(captured_frame_base64)
    cap.release()
    cv2.destroyAllWindows()

    



    if captured_emotion:
        recommender = MusicRecommender(client_id, client_secret)
        #recommendations = recommender.recommend_music(captured_emotion, num_tracks=10)
        recommendations_data = recommender.recommend_music(captured_emotion, num_tracks=10, language=selected_language, singer=selected_singer)
        if 'recommendations' in recommendations_data:
            recommendations = []
            for recommendation_tuple in recommendations_data['recommendations']:
                recommendation = {
                    'track_name': recommendation_tuple[0],
                    'artist_name': recommendation_tuple[1],
                    'track_url': recommendation_tuple[2],
                    'thumbnail_url': recommendation_tuple[3]
                }
                query = f'{recommendation["artist_name"]} {recommendation["track_name"]} emotion'
                youtube_link = recommender.get_youtube_link(query)
                recommendation['youtube_link'] = youtube_link
                print(f"Query: {query}")
                print(f"YouTube Link: {youtube_link}")
                recommendations.append(recommendation)
        
       
        
        return jsonify({
            'captured_emotion': captured_emotion,
            #'captured_frame_path': "C:\\Users\\Afshan Perween\\OneDrive\\Pictures\\Documents\\Machine_Learning_Apps\\faceexpressiondetection\\captured_emotion_frame.jpg",
            'captured_frame_base64': captured_frame_base64,
            #'recommendations': recommendations
            'recommendations': recommendations_data['recommendations']

         })
    else:
        return jsonify({"error": "Emotion not captured."})



if __name__ == '__main__':
    app.run(debug=True)
#curl -X POST http://127.0.0.1:5000/api/capture-emotion
# <p>Captured Emotion: {capturedEmotion}</p>
 # <img src={song.thumbnail_url} alt={`${song.artist_name} - ${song.track_name}`} />
 #                  <p>{song.artist_name} - {song.track_name}</p>