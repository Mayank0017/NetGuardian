from fastapi import FastAPI, Request
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import numpy as np
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.models import load_model
import nltk
import joblib
from urllib.parse import urlparse

# Ensure stopwords are downloaded
nltk.download('stopwords')

# Initialize PorterStemmer
ps = PorterStemmer()

# Load the fake news model
fake_news_model = load_model('Model/fake_news_model2.h5')

# Parameters for fake news model (use the same values as during training)
voc_size = 5000
sent_length = 30

# Load the phishing URL model and scaler
phishing_url_model = joblib.load('Model/phishing_url_model.pkl')
scaler = joblib.load('Model/scaler.pkl')

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

def preprocess_text(text):
    # Remove non-alphabetic characters
    review = re.sub('[^a-zA-Z]', ' ', text)
    review = review.lower()
    review = review.split()
    
    # Stemming and removing stop words
    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    return ' '.join(review)

def one_hot_encode(text, voc_size):
    # One-hot encode the text
    onehot_repr = [one_hot(text, voc_size)]
    return onehot_repr

def pad_sequence(onehot_repr, sent_length):
    # Pad the sequence
    embedded_doc = pad_sequences(onehot_repr, padding='pre', maxlen=sent_length)
    return embedded_doc

@app.post('/predict-fake-news')
async def predict_fake_news(request: TextRequest):
    text = request.text
    
    # Preprocess the text
    preprocessed_text = preprocess_text(text)
    
    # One-hot encode and pad the text
    onehot_repr = one_hot_encode(preprocessed_text, voc_size)
    padded_doc = pad_sequence(onehot_repr, sent_length)
    
    # Predict the class
    prediction = fake_news_model.predict(padded_doc)
    
    # Return the class (0 for real, 1 for fake)
    result = int(prediction >= 0.5)
    return {"prediction": "Fake" if result == 1 else "Real"}

# -----------------------------------------------------------------------------------
# Add Phishing URL Detection Model Endpoint

def extract_features_from_url(url):
    # Parse the URL
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""

    # Extract features from the URL
    features = []
    
    # Length of URL
    features.append(len(url))
    
    # Length of hostname
    features.append(len(hostname))
    
    # Number of dots in URL
    features.append(url.count('.'))
    
    # Number of hyphens in URL
    features.append(url.count('-'))
    
    # Number of '@' in URL
    features.append(url.count('@'))
    
    # Number of '?' in URL
    features.append(url.count('?'))
    
    # Number of '&' in URL
    features.append(url.count('&'))
    
    # Number of '=' in URL
    features.append(url.count('='))
    
    # Number of '_' in URL
    features.append(url.count('_'))
    
    # Number of '~' in URL
    features.append(url.count('~'))
    
    # Number of '/' in URL
    features.append(url.count('/'))
    
    # Number of ':' in URL
    features.append(url.count(':'))
    
    # Number of '.com' in URL
    features.append(url.count('.com'))
    
    # Presence of 'http' in path
    features.append(1 if 'http' in path else 0)
    
    # Presence of 'https' in path
    features.append(1 if 'https' in path else 0)
    
    features.append(sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0)
    
    # Ratio of digits in hostname
    features.append(sum(c.isdigit() for c in hostname) / len(hostname) if len(hostname) > 0 else 0)
    
    # Presence of punycode (e.g., xn--)
    features.append(int(re.search(r'xn--', url) is not None))
    
    # Port number presence
    features.append(int(parsed_url.port or 0))
    
    # TLD in path
    features.append(int(re.search(r'\.\w+/', path) is not None))
    
    # TLD in subdomain
    features.append(int(re.search(r'\.\w+\.', hostname) is not None))
    
    # Number of subdomains
    features.append(hostname.count('.'))
    
    # Presence of '-' in hostname
    features.append(int('-' in hostname))
    
    # Presence of URL shortening service
    shortening_services = ['bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly']
    features.append(int(any(service in url for service in shortening_services)))
    
    # Number of redirections (e.g., 'http://', 'https://')
    features.append(url.count('//'))
    
    # Length of words in raw
    features.append(len(re.findall(r'\w+', url)))
    
    # Character repetition
    features.append(max(len(m.group(0)) for m in re.finditer(r'(\w)\1*', url)) if re.search(r'(\w)\1*', url) else 0)
    
    # Shortest word in raw
    words = re.findall(r'\w+', url)
    features.append(min(len(w) for w in words) if words else 0)
    
    # Longest word in raw
    features.append(max(len(w) for w in words) if words else 0)
    
    # Average word length in raw
    features.append(sum(len(w) for w in words) / len(words) if words else 0)
    
    # Presence of domain in brand
    features.append(int(re.search(r'\b(?:brand)\b', hostname) is not None))
    
    # Presence of brand in subdomain
    features.append(int(re.search(r'\b(?:brand)\b', hostname.split('.')[0]) is not None))
    
    # Presence of brand in path
    features.append(int(re.search(r'\b(?:brand)\b', path) is not None))
    
    # Suspicious TLD
    features.append(int(re.search(r'\.(top|xyz|work|link|loan|wtf|science|men|party|click)', url) is not None))
    
    # Presence of login form
    features.append(int(re.search(r'<form[^>]*method=["\']post["\']', url) is not None))
    
    # Presence of external favicon
    features.append(int(re.search(r'favicon.ico', url) is not None))
    
    # Number of links in tags
    features.append(len(re.findall(r'<a[^>]+>', url)))
    
    # Presence of submit email
    features.append(int(re.search(r'mailto:', url) is not None))
    
    # Ratio of internal media
    features.append(sum(1 for m in re.finditer(r'\.(jpg|jpeg|png|gif|bmp|svg|ico)', url)) / len(url))
    
    # Ratio of external media
    features.append(sum(1 for m in re.finditer(r'\.(jpg|jpeg|png|gif|bmp|svg|ico)', url)) / len(url))
    
    # Presence of SFH
    features.append(int(re.search(r'secure|form|hide', url) is not None))
    
    # Presence of iframe
    features.append(int(re.search(r'<iframe', url) is not None))
    
    # Presence of popup window
    features.append(int(re.search(r'onclick="window.open', url) is not None))
    
    # Ratio of safe anchor
    features.append(sum(1 for m in re.finditer(r'href\s*=\s*["\']#["\']', url)) / len(url))
    
    # Presence of onmouseover
    features.append(int(re.search(r'onmouseover', url) is not None))
    
    # Presence of right-click protection
    features.append(int(re.search(r'oncontextmenu', url) is not None))
    
    # Presence of empty title
    features.append(int(re.search(r'<title></title>', url) is not None))
    
    # Presence of domain in title
    features.append(int(re.search(r'<title>.*domain.*</title>', url) is not None))
    
    # Presence of whois registered domain
    features.append(int(re.search(r'(Registered|Domain)', url) is not None))
    
    # Domain registration length
    features.append(int(re.search(r'Date:[^>]+', url).group(0).split(':')[-1].strip()) if re.search(r'Date:[^>]+', url) else 0)
    
    # Domain age
    features.append(int(re.search(r'Age:[^>]+', url).group(0).split(':')[-1].strip()) if re.search(r'Age:[^>]+', url) else 0)
    
    # Web traffic
    features.append(int(re.search(r'Web_traffic:[^>]+', url) is not None))
    
    # DNS record
    features.append(int(re.search(r'DNS_record:[^>]+', url) is not None))
    
    # Google index
    features.append(int(re.search(r'Index:', url) is not None))
    
    # Page rank
    features.append(int(re.search(r'Page_rank:[^>]+', url).group(0).split(':')[-1].strip()) if re.search(r'Page_rank:[^>]+', url) else 0)
    
    return features

@app.post('/predict-phishing-url')
async def predict_phishing_url(request: URLRequest):
    url = request.url
    print(f"Received URL: {url}")
    
    # Extract features from the URL
    features = extract_features_from_url(url)
    
    # Convert to numpy array and scale
    features_array = np.array(features).reshape(1, -1)
    scaled_features = scaler.transform(features_array)
    
    # Predict the class
    prediction = phishing_url_model.predict(scaled_features)
    
    # Return the class (0 for legitimate, 1 for phishing)
    result = int(prediction >= 0.5)
    return {"prediction": "Phishing" if result == 1 else "Legitimate"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
