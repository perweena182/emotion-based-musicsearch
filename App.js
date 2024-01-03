import React, { useState } from 'react';
import './App.css';
const App = () => {
  const [capturedEmotion, setCapturedEmotion] = useState(null);
  const [capturedFrameBase64, setCapturedFrameBase64] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [languages, setLanguages] = useState(['Any', 'English', 'Hindi', 'German', 'korean','Arabic','Japanese']);
  const [selectedLanguage, setSelectedLanguage] = useState('Any');
  const [famousSingers, setFamousSingers] = useState(['Any']);
  const [selectedSinger, setSelectedSinger] = useState('Any');
  const [customLanguage, setCustomLanguage] = useState('');
  const [customSinger, setCustomSinger] = useState('');


  const captureEmotion = async () => {
    try {
      console.log('Before fetch');
      console.log('Selected Language:', selectedLanguage);
      console.log('Custom Language:', customLanguage);

      const response = await fetch('http://localhost:5000/api/capture-emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
           selectedLanguage,
          selectedSinger,
        }),
       
      });
      console.log('Full response:', response);
      console.log('After fetch');


      if (!response.ok) {
        throw new Error('Failed to capture emotion.');
      }

      const data = await response.json();
      console.log(data);
      setCapturedEmotion(data.capturedEmotion);
      setRecommendations(data.recommendations);
      if (data.captured_frame_base64) {
        setCapturedFrameBase64(data.captured_frame_base64);
      }
    } catch (error) {
      console.error('Error capturing emotion:', error.message);
    }
  };
    const handleLanguageChange = (value) => {
    setSelectedLanguage(value);
    setCustomLanguage(''); // Clear the custom language when selecting from the dropdown
    //setCustomLanguage(value === 'custom' ? customLanguage : '');
  };

  const handleSingerChange = (value) => {
    setSelectedSinger(value);
    setCustomSinger(''); // Clear the custom singer when selecting from the dropdown
  };
  const openTrackUrl = (url) => {
   window.open(url, '_blank');
  };
//   const openTrackUrl = (url) => {
//   window.location.href = url;
// };


  return (
    <div className="App">
          <h1 className="heading">Emotion-based Music Recommendation</h1>

      <div>
        <label htmlFor="language">Select Language : </label>
        <select
          id="language"
          onChange={(e) => handleLanguageChange(e.target.value)}
          value={selectedLanguage === 'Any' ? '' : selectedLanguage}
        >
          {languages.map((language, index) => (
            <option key={index} value={language}>
              {language}
            </option>
          ))}
          
        </select>
        {selectedLanguage === 'custom' && (
          <input
            type="text"
            placeholder="Type your language..."
            value={customLanguage}
            onChange={(e) => setCustomLanguage(e.target.value)}
          />
        )}
      </div>
      <div>
        <label htmlFor="singer">Select  Singer  :  </label>
        <select
          id="singer"
          onChange={(e) => handleSingerChange(e.target.value)}
          value={selectedSinger === 'Any' ? '' : selectedSinger}
        >
          {famousSingers.map((singer, index) => (
            <option key={index} value={singer}>
              {singer}
            </option>
          ))}
          
        </select>
        {selectedSinger === 'custom' && (
          <input
            type="text"
            placeholder="Type your singer..."
            value={customSinger}
            onChange={(e) => setCustomSinger(e.target.value)}
          />
        )}
      </div>

      <button onClick={captureEmotion}>Capture  Emotion</button>
      {capturedEmotion!==null && capturedFrameBase64 !== null && (
         <div>
          <h2 className="capture">Captured Frame:</h2>
          <img className="captured-frame"
            src={`data:image/jpeg;base64,${capturedFrameBase64}`}
            alt="Captured Emotion Frame"
          />
       
          <div>
          {recommendations ? (
            <div>
              <h1 className="recommend">Recommended Songs:</h1>
          
                        <div className="thumbnails">
                        {console.log('Recommendations:', recommendations)}
                {recommendations.map((song, index) => (
                 
                    <div key={index} className="thumbnail" >
                 <img
              src={song[3]} // Accessing imageURL from the subarray
              alt={`${song[1]} - ${song[0]}`} // Accessing artistName and songName from the subarray
              
            />
            <p>{song[1]} - {song[0]}</p>
                  <a href={song[2]} target="_blank" rel="noopener noreferrer" id="spotify">
                     Listen on Spotify
                      </a>
        
                    
                    <a href={song.youtube_link} target="_blank" rel="noopener noreferrer" onClick={(e) => {
   e.preventDefault();
   console.log('Clicked on YouTube link:', song.youtube_link);
}}>
   Watch on YouTube
</a>


                  
                    </div>
                ))}
                 </div>
              </div>
            
          ) : (

            <p>Loading recommendations...</p>
          )}
        </div>
        </div>
      )}
       <footer>
      <p>&copy; 2023 Emotion-based Music Recommendation System. All rights reserved.</p>
    </footer>
    </div>
  );
};

export default App;
//<option value="custom">-- Type Your Language --</option>