import requests
import json
import os
from pydub import AudioSegment
import speech_recognition as sr

# The endpoint URL for your GraphQL API
GRAPHQL_URL = "https://openapi.radiofrance.fr/v1/graphql"  # This URL might differ. Please replace with the correct endpoint.

# The GraphQL query
GRAPHQL_QUERY = """
{
  diffusionsOfShowByUrl(
    url: "https://www.radiofrance.fr/franceculture/podcasts/de-cause-a-effets-le-magazine-de-l-environnement"
    first: 1
  ) {
    edges {
      node {
        podcastEpisode {
          url
          playerUrl
          title
        }
      }
    }
  }
}
"""

# Headers
HEADERS = {
    "x-token": "9b970db2-9fde-4501-a80f-ba5b66b6afcc",
}

def download_mp3(url, filename="temp.mp3"):
    response = requests.get(url, stream=True)
    response.raise_for_status() # Raise an exception for HTTP errors
    with open(filename, "wb") as mp3_file:
        for chunk in response.iter_content(chunk_size=8192):
            mp3_file.write(chunk)
    return filename

def convert_mp3_to_wav(mp3_filepath, wav_filepath="temp.wav"):
    audio = AudioSegment.from_mp3(mp3_filepath)
    audio.export(wav_filepath, format="wav")
    return wav_filepath

def speech_to_text(wav_filepath):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filepath) as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"API unavailable or unresponsive: {e}"

def get_all_text_from_podcast(data):
    first_episode_url = get_podcast_url(data)
    print(f"Downloading from: {first_episode_url}")
    mp3_filepath = download_mp3(first_episode_url)
    wav_filepath = convert_mp3_to_wav(mp3_filepath)
    text = speech_to_text(wav_filepath)
    print("Transcription:\n", text)

    # Clean up temporary files
    os.remove(mp3_filepath)
    os.remove(wav_filepath)
def get_podcast_url(data):
    url = data["data"]["diffusionsOfShowByUrl"]["edges"][0]["node"]["podcastEpisode"]["url"]
    cleaned_result = url.replace("\nnull", "")
    return cleaned_result
def fetch_data():
    # Making the request
    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": GRAPHQL_QUERY}
    )

    # Error handling
    if response.status_code == 200:
        get_all_text_from_podcast(response.json())
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    result = fetch_data()
    print(json.dumps(result, indent=4))


