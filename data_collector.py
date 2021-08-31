import tweepy,json,pandas,csv,nltk,string,re  # for pattern matching, used for removing URLs, Usernames and Punctuations
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from nltk.corpus import stopwords # for removing stopwords
from nltk.tokenize import RegexpTokenizer # for tokenizing
from nltk.stem import WordNetLemmatizer # for lemmatizing
from nltk.stem.porter import PorterStemmer # for stemming



def search_tokens():
    url='https://www.thesaurus.com/browse/happy?s=t'  
    '''
    #IF you are willing to search for customised tags uncomment the code snippet, then enter a word and all related tags 
    #shall be automatically searched
    
    #By default all sad related tags are being searched
    
    n=input()
    url = 'https://www.thesaurus.com/browse/'+n+'?s=t'
    '''
    content = urllib.request.urlopen(url)
    read_content = content.read()         #data collection phase (data contains metadata and original data)
    
    #print(read_content)          #metadata check
    
    q,cnt=False,0
    # reference: <a font-weight="inherit" href="/browse/dismal" data-linkid="nn1ov4" class="css-1m14xsh eh475bn1">dismal<!-- --> </a>
    bs = BeautifulSoup(read_content, 'html.parser')
    h1 = bs.find_all('a', class_="css-1m14xsh eh475bn1")    #data filter phase
    t_d=['sad']
    for i in h1:
        #z='#'+i.text
        t_d.append(i.text)
    return t_d




def raw_polished():     #raw data from Twitter is converted to a polished version where noise and other metadatas are removed
    ok=False
    l,ml,cnt=[],[],0
    with open('Plus.txt','r') as file:
        for line in file:
            for word in line.split():  
                if(word=='\"text\":' or word=='\"description\":'):
                    ok=True
                    w=''
                elif(word== '\"source\":'):
                    ok=False
                    l.append(w)
                elif(word=='\"translator_type\":'):
                    ok=False
                    l.append(w)
                    ml.append(l)
                    l=[]
                elif(ok):
                    w=w+word+' '
                    #print(w)      #debugging (check whether the variable is actually storing something)
    #print(ml)                     #debugging (check the final list for desired values) 
    with open('Plusconv.csv','w') as f:
        write = csv.writer(f) 
        write.writerow(['POST','DESCRIPTION'])  #the different tags to choose from are present in the update log 2021.02.06
        write.writerows(ml)
    


def remove_un(text):       #removing noise from the data
    
    free= re.sub(r'http\S+', '', text)
    free= re.sub(r'u0+','',free)
    free= re.sub(r'\\ud\S+', '', free)
    free= re.sub(r'\xa0\S+', '', free)
    free= re.sub(r'pic.\S+', '', free)
    free= re.sub('@[\w]+','',free)         #removing usernames
    free= "".join([char for char in free if char not in string.punctuation]) #removing punctuations
    return free 

def stop_lemm_stem(text):   #removing stopwords , lemmatizing and stemwords
    hs= (open('hindiswords.txt','r').readlines())
    free=[word for word in text if word not in stopwords.words('english')+stopwords.words('french')+hs]
    lemmatizer=WordNetLemmatizer()
    free=[lemmatizer.lemmatize(word) for word in free]
    stemmer=PorterStemmer()
    free=" ".join([stemmer.stem(word) for word in free])
    return free

def PHASE_1(READ=True):
    if(READ):                                           #since this process can be time consuming, data collection from Twitter everytime can
                                                        #be skipped by passing False as parameter 
        access_token="1356115757050937347-hIaRlwZpgGafrGhaMHjruo72PUGf4v"
        access_token_secret="GstHAPyelXZlZtFsXu0ieAEQlX4BPUfZpnqjoYRCWrPrq"
        consumer_key="LUE8ITDfE08n3ERjWpXyx0ZWc"
        consumer_secret="ydOXjuc6RhYKogpJ42fKNodT8qV5NTXzoZFny5LAKFOo4VubqR"
        auth= tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        tweet_list=[]
        class MyStreamListener(tweepy.StreamListener):
            def __init__(self,api=None):
                super(MyStreamListener,self).__init__()
                self.num_tweets=0
                self.file=open("Plus.txt","w")
            def on_status(self,status):
                tweet=status._json
                self.file.write(json.dumps(tweet)+ '\n')
                tweet_list.append(status)
                self.num_tweets+=1
                if self.num_tweets<1000:
                    return True
                else:
                    return False
                self.file.close()
        l = MyStreamListener()
        stream =tweepy.Stream(auth,l)
        stream.filter(track=search_tokens())
        tweets_data_path='Plus.txt'
        tweets_data=[]
        tweets_file=open(tweets_data_path,"r")
        #read in tweets and store on list
        for line in tweets_file:
            tweet=json.loads(line)
            tweets_data.append(tweet)
        tweets_file.close()
        #print(tweets_data[0])         #printing the raw data collected freshly from Twitter via Tweepy
        '''read_file = pandas.read_csv ('tweet.txt')
        read_file.to_csv ('Untitled Folder/converted.csv', index=None)'''
        raw_polished()                #creates a CSV file after removing all the unnecessary data
    
def PHASE_2(PROCESS=True):
    if(nltk.download('stopwords') and nltk.download('wordnet')):
        print("prerequistes checked")
        data=pd.read_csv("Depression_Tweet.csv")
        data.shape 
        pd.set_option('display.max_colwidth',None)
        
        data['POST']=[str(tweet) for tweet in data['POST']]
        
        data['POST']=data['POST'].apply(lambda x:remove_un(x)) #list(data['TWEET'])
        
        tokenizer=RegexpTokenizer(r'\w+')
        data['POST']=data['POST'].apply(lambda x:tokenizer.tokenize(x.lower()))
        
        data['POST']=data['POST'].apply(lambda x:stop_lemm_stem(x))
        print(data) #to check the final contents of preprocessed data
    
def main():
    PHASE_1()      #data collection phase
    PHASE_2()
    print('All complete')
if __name__ == "__main__":
    main()
