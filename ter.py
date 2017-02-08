# -*- coding: utf-8 -*-

"""
    The Tweeter Election Results forecaster takes an election model (see 'election' module)
    and retrieves relevant past tweets to predict the winner of an election.
"""

import csv
import datetime as dt
from collections import defaultdict
from sentiment import TweetSentimentAnalyser

class TwitterElectionResults:
    """
    The main class of the Twitter Election Results prediction system.
    """

    def __init__(self, dataset, tweets_file):
        self.analyser = TweetSentimentAnalyser()
        self.dataset = dataset
        self.tweets = []
        with open(tweets_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, dialect="excel")
            for row in csv_reader:
                if len(row) == 0:
                    continue
                row_encoded = [s.encode('utf-8') for s in row]
                self.tweets.append(list(row_encoded))

    def forecast(self, results_filename):
        """
        Predict the election results from the collected tweets and output
        the forecast to the given file.
        """

        analyser = TweetSentimentAnalyser()

        candidates = self.dataset.candidates
        party_key_from_candidate = lambda candidate: candidate.party[0]
        number_tweets = len(self.tweets)
        if number_tweets == 0:
            print("No tweets were found in the file '{}' : aborting the prediction."
                  .format(number_tweets))

        # General statistics dictionnaries
        # NB: defaultdict allows for efficiently incrementing the value of a key/value
        # pair that may not be initialized yet without checking its existence
        stats_tweets_per_user = defaultdict(int)
        stats_dates = defaultdict(int)
        stats_hashtags = defaultdict(int)
        stats_parties = {party_key_from_candidate(c): 0 for c in candidates.values()}

        # Tweet analysis
        results_per_candidate = {candidate_key: [0, 0] for candidate_key in candidates.keys()}
        for tweet in self.tweets:
            # retrieve the tweet data (text) and metadata (retweets, date...)
            candidate_key = tweet[0].decode('utf-8')
            text = tweet[1].decode('utf-8')
            datetime_str = tweet[2].decode('utf-8')
            datetime = dt.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S") # parse the datetime
            retweets = int(tweet[3])
            username = tweet[4].decode('utf-8')
            hashtags = None if len(tweet[5]) == 0 else tweet[5].decode('utf-8').split(' ')

            # basic statistics (individual users & hashtags)
            stats_tweets_per_user[username] += 1
            date = datetime.strftime("%Y-%m-%d") # keep only the date
            stats_dates[date] += 1
            if hashtags is not None:
                for hashtag in hashtags:
                    if hashtag == '#': # ignore empty hashtag
                        continue
                    stats_hashtags[hashtag.lower()] += 1

            # per-candidate analysis
            for key, data in candidates.items():
                # party mentions statistics
                party_key = party_key_from_candidate(data)
                for party_designation in data.party:
                    if party_designation in text:
                        stats_parties[party_key] += 1
                        break
                # basic forecast : 1 tweet = 1 vote for the mentionned candidate
                for candidate_name in data.names:
                    if candidate_name in text:
                        results_per_candidate[key][0] += 1

            # sentimenal-analysis forecast :
            score = analyser.analyse_tweet(text, retweets)
            results_per_candidate[candidate_key][1] += score

        # Data interpretation
        compound_sum = sum([v[1] for v in results_per_candidate.values()])
        sort_default_dict = lambda dict, reverse:\
            sorted(dict.items(), key=lambda k_v: k_v[1], reverse=reverse)

        # Write the results file
        votes_sum = sum([v[0] for v in results_per_candidate.values()])
        with open(results_filename, 'w+') as results_file:
            csv_writer = csv.writer(results_file, dialect="excel")

            # per candiadate forecast
            for candidate, results in results_per_candidate.items():
                csv_writer.writerow([
                    candidate,
                    results,
                    "{} %".format(100 * results[0] / votes_sum),
                    "{} %".format(100 * results[1] / compound_sum)
                ])

            # general statistics
            for party, occurences in sort_default_dict(stats_parties, True):
                csv_writer.writerow([party, occurences])
            for username, occurences in sort_default_dict(stats_tweets_per_user, True):
                csv_writer.writerow([username, occurences])
            for hashtag, occurences in sort_default_dict(stats_hashtags, True):
                csv_writer.writerow([hashtag, occurences])

        print(results_per_candidate)
