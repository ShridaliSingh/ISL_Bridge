import time
from groq import Groq
from dotenv import load_dotenv
import os

CONFIRM_THRESHOLD = 0.6

load_dotenv()

class TextAnalyzer :

    def __init__(self):
        self.sign = None
        self.word = []
        self.sentence = []
        self.start = None
        self.space = None
        self.client = Groq(api_key =os.getenv("GROQ_API_KEY"))

    def process(self, raw_sign):
         
        confirmed_sign = self.confirm_sign(raw_sign)

        if confirmed_sign is None:
            pass
        elif confirmed_sign == 'SPACE' :
            self.sentence = self._build_sentence()
        else :
            self.word = self._add_letter(confirmed_sign)

        return self.sign, self.word, self.sentence

            
    def _confirm_sign(self,raw_sign):

        if raw_sign != self.sign :
            self.start = time.time()
            self.sign = raw_sign
             
        elif self.sign == raw_sign and time.time() - self.start >= CONFIRM_THRESHOLD : 
            self.start = time.time()
            return self.sign
        
        return None
         
    def _add_letter(self, confirmed_sign):
        self.word.append(confirmed_sign)
        return self.word
    
    def _build_sentence(self):
        letters = "".join(self.word) #string

        prompt = f"""This are few letters that the user spelled - {letters}, 
                    the user tried to form a word from these letters, the letters are in sequence and 
                    should be treated as the attempted spelling. Return a word that can be the possible 
                    word that the user wanted to spell. If you cant think of anything then there can be few extra
                    letters or wrong letters in between,or less letters than what the actual word contains, be careful of 
                    it and return just a meaningful word and not a whole sentence. Return only the word that you think
                    the letters formed, dont add anything extra like 'this word might be...' blah blah. and return the word in uppercase"""

        
        response = self.client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages = [{"role" : "user", "content" : prompt}]
        )

        word = response.choices[0].message.content  #string

        self.sentence.append(word)

        self.word = []

        return self.sentence


         


