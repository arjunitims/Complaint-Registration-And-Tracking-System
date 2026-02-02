import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

training_data = [
    ("My internet connection is very slow and keeps dropping", "Technical", "High", 24),
    ("The billing amount seems incorrect this month", "Billing", "Medium", 48),
    ("I need help setting up my email account", "Technical", "Low", 12),
    ("I was charged twice for the same service", "Billing", "High", 24),
    ("The customer service representative was rude", "Service Quality", "Medium", 36),
    ("My account got locked and I cannot login", "Account", "High", 12),
    ("I want to upgrade my plan", "General", "Low", 24),
    ("The website is not loading properly", "Technical", "Medium", 12),
    ("I received a damaged product", "Product", "High", 48),
    ("Need assistance with product installation", "Technical", "Medium", 24),
    ("I want to cancel my subscription", "Account", "Medium", 36),
    ("Payment gateway is not working", "Technical", "High", 6),
    ("I did not receive my refund yet", "Billing", "High", 72),
    ("The app keeps crashing on my phone", "Technical", "High", 12),
    ("I have a question about warranty", "General", "Low", 48),
    ("Delay in service activation", "Service Quality", "Medium", 48),
    ("Need technical support for configuration", "Technical", "Medium", 18),
    ("Invoice not received for last month", "Billing", "Low", 24),
    ("Password reset link not working", "Account", "Medium", 6),
    ("Product quality is poor", "Product", "Medium", 72),
    ("Network coverage is poor in my area", "Technical", "High", 96),
    ("Unauthorized charges on my account", "Billing", "High", 12),
    ("Want to provide feedback on service", "General", "Low", 36),
    ("Server downtime affecting work", "Technical", "High", 6),
    ("Need help with device setup", "Technical", "Low", 12),
    ("Billing cycle date needs to be changed", "Billing", "Low", 48),
    ("Customer support not responding", "Service Quality", "High", 24),
    ("Product warranty claim process", "Product", "Medium", 72),
    ("Unable to access online portal", "Account", "High", 8),
    ("Request for service enhancement", "General", "Low", 120),
]

texts = [item[0] for item in training_data]
categories = [item[1] for item in training_data]
priorities = [item[2] for item in training_data]
resolution_times = [item[3] for item in training_data]

category_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=100, stop_words='english')),
    ('classifier', MultinomialNB())
])
category_model.fit(texts, categories)

priority_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=100, stop_words='english')),
    ('classifier', RandomForestClassifier(n_estimators=50, random_state=42))
])
priority_model.fit(texts, priorities)

resolution_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=100, stop_words='english')),
    ('regressor', RandomForestRegressor(n_estimators=50, random_state=42))
])
resolution_model.fit(texts, resolution_times)

with open('category_model.pkl', 'wb') as f:
    pickle.dump(category_model, f)

with open('priority_model.pkl', 'wb') as f:
    pickle.dump(priority_model, f)

with open('resolution_model.pkl', 'wb') as f:
    pickle.dump(resolution_model, f)

print("Models trained and saved successfully!")
print(f"Categories: {set(categories)}")
print(f"Priorities: {set(priorities)}")
