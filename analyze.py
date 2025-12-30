from wordcloud import WordCloud
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sentimentAnalyzer = SentimentIntensityAnalyzer()
from nltk.corpus import wordnet, stopwords
nltk.download('stopwords')
stopWords = set(stopwords.words('english'))
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
wordLemmatizer = WordNetLemmatizer()
from nltk.corpus import wordnet
nltk.download('averaged_perceptron_tagger')
import re
from random_username.generate import generate_username
from nltk.tokenize import word_tokenize, sent_tokenize


#Welcome User
def welcomeUser():
    print("Welcome to the text analysis tool, I will mine and analyze a body of text from a file you give me.")

#Get Username
def getUsername():

    maxAttempts = 3
    attempts = 0

    while attempts < maxAttempts:

        #Print message prompting user to input their name
        inputPrompt = ""
        if attempts == 0:
            inputPrompt = "\nTo begin, please enter your username:\n"
        else:
            inputPrompt = "\nPlease try again:\n"
        # ask user for input
        usernameFromInput = input(inputPrompt)
        
        # validate username
        if len(usernameFromInput) < 5 or not usernameFromInput.isidentifier():
            print("Your username must be at least 5 characters long, alphanumeric only (a-z/A-Z/0-9), have no spaces, and cannot start with a number!")
        else:
            return usernameFromInput

        attempts += 1

    # if we get here, user didn't provide a valid username, so assign a generated one
    print(f"\nExhausted all {maxAttempts} attempts, assigning username instead....")
    return generate_username()[0]

#Greet User
def greetUser(name):
    print("\nHello " + name)

#Get text from file
def getArticleText():
    f = open("files/article.txt", "r", encoding="utf-8")
    rawText = f.read()
    f.close()
    return rawText.replace("\n", '').replace("\r", '')

# Extract Sentences from raw text body
def tokenizeSentences(rawText):
    return sent_tokenize(rawText)

# Extract Words from list of sentences
def tokenizeWords(sentences):
    words = []
    for sentence in sentences:
        words.extend(word_tokenize(sentence))
    return words

def extractKeySentences(sentences, searchPattern):
    matchedSentences = []
    for sentence in sentences:
        #if sentence matches desired pattern, add to matchedSentences
        if re.search(searchPattern, sentence.lower()):
            matchedSentences.append(sentence)
    return matchedSentences

#Get the average words per sentence, excluding punctuation
def getWordsPerSentence(sentences):
    if not sentences or len(sentences) == 0:
        return 0
    totalWords = 0
    for sentence in sentences:
        totalWords += len(sentence.split(" "))
    return totalWords / len(sentences) 

# Convert part of speech from pos_tag() function
# into wordnet compatible pos tag
posToWordnetTag = {
    "J": wordnet.ADJ,
    "V": wordnet.VERB,
    "N": wordnet.NOUN,
    "R": wordnet.ADV
}
def treebankPosToWordnetPos(partOfSpeech):
    posFirstChar = partOfSpeech[0]
    if posFirstChar in posToWordnetTag:
        return posToWordnetTag[posFirstChar]
    return wordnet.NOUN

# Convert raw list of (word, POS) tuple to a list of strings
# that only include valid english words
def cleanseWordList(posTaggedWordTuples):
    cleansedWords = []
    invalidWordPattern = "[^a-zA-Z-+]"
    for posTaggedWordTuple in posTaggedWordTuples:
        word = posTaggedWordTuple[0]
        pos = posTaggedWordTuple[1]
        cleansedWord = word.replace(".", "").lower()
        if (not re.search(invalidWordPattern, cleansedWord)) and len(cleansedWord) > 1 and cleansedWord not in stopWords:
            cleansedWords.append(wordLemmatizer.lemmatize(cleansedWord, treebankPosToWordnetPos(pos)))
    return cleansedWords


def analyzeText(textToAnalyze):
    articleSentences = tokenizeSentences(textToAnalyze)
    articleWords = tokenizeWords(articleSentences)

    #Get sentence Analytics
    stockSearchPattern = "[0-9]"
    keySentences = extractKeySentences(articleSentences, stockSearchPattern)
    wordsPerSentence = getWordsPerSentence(articleSentences)

    #Get word Analytics
    wordsPosTagged = nltk.pos_tag(articleWords)
    articleWordsCleansed = cleanseWordList(wordsPosTagged)

    # Generate word cloud
    separator = " "
    wordCloudFilePath = "results/wordcloud.png"
    if articleWordsCleansed:
        wordcloud = WordCloud(width = 1000, height = 700, background_color="white", colormap="Set3", \
            collocations=False).generate(separator.join(articleWordsCleansed))
        wordcloud.to_file(wordCloudFilePath)

    # Run Sentiment Analysis
    sentimentResult = sentimentAnalyzer.polarity_scores(textToAnalyze)

    # Collate analyses into one dictionary
    finalResult = {
        # "username": username,
        "data": {
            "keySentences": keySentences,
            "wordsPerSentence": round(wordsPerSentence, 1),
            "sentiment": sentimentResult,
            "wordCloudFilePath": wordCloudFilePath
        },
        "metadata": {
            "sentencesAnalyzed": len(articleSentences),
            "wordsAnalyzed": len(articleWordsCleansed)
        }
    }
    return finalResult

def runAsFile():
    # Get User Details
    welcomeUser()
    username = getUsername()
    greetUser(username)

    # Extract and Tokenize  Text
    articleTextRaw = getArticleText()
    analyzeText(articleTextRaw)

