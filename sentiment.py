# -*- coding: utf-8 -*-

"""
    The sentiment module is responsible for analysing the tone of any given
    tweet regarding a certain candidate to an election.
"""

import math
from vaderSentiment import vaderSentiment

class TweetSentimentAnalyser:
    """
    Class responsible for determining the positiveness or negativeness
    of any given tweet, in the context of an election.
    """

    def __init__(self, language: str="en"):
        self.engine = vaderSentiment.SentimentIntensityAnalyzer(
            lexicon_file="vader_lexicon.txt")

        self.translate_from = None
        if language not in ["en", "en-US", "en-UK"]: # languages other than french
            self.translate_from = language

    def analyse_tweet(self, tweet_text: str, retweets: int) -> float:
        """Analyse a tweet text and return a global sentiment score."""
        polarity_scores = self.engine.polarity_scores(tweet_text)
        score = polarity_scores["compound"]
        score_sign = +1 if score >= 0 else -1
        score_factor = math.pow(abs(score), 1/2)
        retweets_factor = 1 + 0.5 * math.log(retweets if retweets >= 1 else 1)
        return score_sign * score_factor * retweets_factor
