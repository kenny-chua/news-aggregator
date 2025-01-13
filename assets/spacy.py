import spacy
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Load spaCy model for sentence tokenization
nlp = spacy.load("en_core_web_sm")


# Function to split text into sentences
def segment_text(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]


# Function to compute cosine similarity and perform clustering
def cluster_sentences(sentences, n_clusters=3):
    # Convert sentences into TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)

    # Group sentences by cluster
    clusters = {i: [] for i in range(n_clusters)}
    for idx, label in enumerate(kmeans.labels_):
        clusters[label].append(sentences[idx])

    return clusters


# Function to restructure text into readable paragraphs
def restructure_text(text, n_clusters=3):
    sentences = segment_text(text)
    clusters = cluster_sentences(sentences, n_clusters)

    # Combine sentences in each cluster into paragraphs
    paragraphs = []
    for cluster in clusters.values():
        paragraphs.append(" ".join(cluster))

    return "\n\n".join(paragraphs)


# Sample text
text = """
Los Angeles Lakers head coach JJ Redick lamented losing “things that you can’t replace” as he described the pain of seeing his rental home burned down in the Pacific Palisades wildfire. Speaking to reporters on Friday following the Lakers’ practice, an emotional Redick said that he witnessed “complete devastation and destruction” in his local community when he returned home in the aftermath of the fire. “I went through most of the village and it’s all gone, and I don’t think you can ever prepare yourself for something like that,” Redick said. “Our home is gone. “We were renting for the year to try to figure out where we wanted to be long-term. Everything we owned that was of any importance to us, almost 20 years together as a couple and 10 years of parenting, was in that house. There’s certain things that you can’t replace, that will never be replaced.” He added: “It’s an awful feeling to lose your home. I think what has happened over the last 72 hours from me being up there and from having a number of people that had homes in the Palisades that are also staying at the hotel, you really get a sense of just the communal destruction. I got back to the hotel, and of course my wife and I are emotional. I’m not sure I’ve wept or wailed like that in several years.” Redick was a basketball analyst for ESPN prior to becoming a head coach and moving to the Los Angeles area. During his 15-year playing career, he spent four seasons with the Los Angeles Clippers. “The Palisades community has really just been so good to us,” Redick said while fighting back tears. “I think that’s the part for us that we’re really struggling with, is just the loss of community. And I recognize that people make up community, and we’re going to rebuild, and we want to help lead on that. But all the churches, the schools, the library, it’s all gone.” After speaking with reporters, Redick was comforted by Lakers guard Austin Reaves on the team’s practice court. Los Angeles were scheduled to return to the court on Saturday night against the San Antonio Spurs at Crypto.com Arena but the game has been postponed. “The Los Angeles community is on our hearts,” the team said in a statement. “The Lakers look forward to getting back on the court soon, honoring LA’s first responders and recognizing the heartbreak endured across our beloved community.” The Clippers were set to host the Charlotte Hornets at the Intuit Dome on Saturday but that game has also been postponed. More than 100,000 residents remain under evacuation orders as fires continue to sweep across LA County and fire departments battle to contain them. Officials have confirmed at least 11 deaths but say it’s not yet safe to assess the true total. Redick was not the only NBA coach to be affected by the fires. On Thursday, Golden State Warriors head coach Steve Kerr said that his childhood home in Pacific Palisades, where his mother still lived, has been destroyed. “That’s my hometown, and all my friends who are from there, pretty much they’ve all lost their homes, their family homes, childhood homes,” Kerr told reporters. “Our whole high school’s gone. The town looks like it’s just been completely wiped out … It’s hard to even fathom how Pacific Palisades rebuilds and how it becomes a thriving community again. It’s just shocking.”
"""

# Run the restructuring function
restructured_text = restructure_text(text, n_clusters=3)
print(restructured_text)
