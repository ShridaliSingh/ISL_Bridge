import time
from groq import Groq
from dotenv import load_dotenv
import os

CONFIRM_THRESHOLD = 1.5

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
         
        confirmed_sign = self._confirm_sign(raw_sign)

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
        if not self.word:
            return self.sentence
        
        letters = "".join(self.word) #string

        prompt = f"""The user has gestured a sequence of letters from Indian Sign Language along with 
        numbers from 0 to 9, and you are receiving this sequence as {letters}. These letters, read in 
        the SAME ORDER they are given, are meant to spell a single word, but the spelling is not perfect, 
        and it is YOUR JOB to figure out what that word is. The sequence may contain EXTRA letters that don't 
        belong, it may be MISSING some letters, or it may include a few WRONG letters, so you must look past these 
        mistakes and work out the correct intended word.The wrong letters will at most times be in the MIDDLE of the letters.
        First try removing duplicate consecutive letters and see if a word forms, before trying to replace letter.For sequences 
        of 1-2 letters that form common English words like I, A, AM, IS, IT, BE, DO — return them exactly as they are
        The word you return must be a SINGLE word and never a phrase, 
        it must be written entirely in UPPERCASE, and its length should be SIMILAR to the number of letters given — for 
        example, if only 2 letters are provided, the word should be roughly 2 to 4 letters long rather than something much 
        longer or shorter — and as a guide, the word has APPROXIMATELY {len(self.word)} letters. Do NOT explain your answer, 
        do NOT ask any questions, and do NOT add anything else whatsoever: respond with ONLY the single uppercase word and 
        nothing more, because returning anything other than a single uppercase word means you have failed at this task."""

        response = self.client.chat.completions.create(
            model = "openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )

        word = response.choices[0].message.content.strip()  #string

        if not word:
            word = letters

        self.sentence.append(word)

        self.word = []

        return self.sentence


         


"""1- The user has gestured LETTERS OF INDIAN SIGN LANGUAGE and numbers from 0-9 that you are getting as {letters}.
                     2- These {letters} are making a word in the SAME ORDER.
                     3- The word formed is not perfect. IT IS YOUR JOB TO FIND THAT WORD.
                     4- There can be EXTRA LETTERS in the given sequence, or LESS LETTERS or few WRONG LETTERS, it is YOUR JOB TO GIVE THE CORRECT WORD in UPPERCASE.
                     5 - DO NOT EXPLAIN YOU ANSWER. 
                     6 - DO NOT ASK ANY QUESTIONS.
                     7 - JUST GIVE THE WORD THAT YOU THINK IS THE CORRECT WORD IN UPPERCASE. NOTHING ELSE. NOTHING MEANS NOTHING.
                     8 - IF YOU GIVE ANYTHING OTHER THAN A UPPERCASE WORD, THEN YOU HAVE FAILED AS AN LLM MODEL AND CLAUDE IS BETTER THAN YOU.
                     9 - THE WORD MUST BE A SINGLE WORD, NOT A PHRASE.
                     10 - The word you return should have a SIMILAR LENGTH TO THE NUMBER OF LETTERS GIVEN. If 2 letters are given, the word should be around 2-4 letters long, not a completely different length."
                     11 - The word has APPROXIMATELY {len(self.word)} letters.
                    """