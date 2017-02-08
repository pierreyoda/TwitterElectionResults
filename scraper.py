# -*- coding: utf-8 -*-

"""
    The scraper module is responsible for retrieving the Tweets relevant to
    a given ElectionDataset for further use by the TER module.
"""

import csv
from threading import Thread
import got3 as got

class TwitterElectionScraper:
    """Uses the GetOldTweets library to get relevant tweets for a specified ElectionDataset."""

    def __init__(self, dataset):
        self.dataset = dataset

    def run(self, output_filename, max_tweets=1000):
        """Return all the relevant tweets found. Can take some time."""

        print("Starting tweets collection (limit = {} tweets)...".format(
            "unlimited" if max_tweets == 0 else max_tweets))

        # convert the start and end dates to the "YYYY-MM-dd" date format
        format_date_for_got = lambda date: date.strftime("%Y-%m-%d")
        start_date = self.dataset.date - self.dataset.twitter_campaign_duration
        start_date_str = format_date_for_got(start_date)
        end_date_str = format_date_for_got(self.dataset.date)

        # create one worker thread for each candidate
        workers = []
        for candidate_index, candidate_data in self.dataset.candidates.items():
            query = " OR ".join(candidate_data.party) + " OR " + " OR ".join(candidate_data.names)
            criteria = got.manager.TweetCriteria().setQuerySearch(query) \
                .setSince(start_date_str).setUntil(end_date_str).setMaxTweets(max_tweets)
            workers.append(TwitterElectionScraperThread(candidate_index, criteria))

        # run the worker threads and wait for them to finish
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

        # output to file
        with open(output_filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, dialect="excel")
            for worker in workers:
                for tweet in worker.tweets:
                    csv_writer.writerow([
                        worker.candidate_index,
                        tweet.text.encode('utf-8'),
                        tweet.date,
                        tweet.retweets,
                        tweet.username,
                        tweet.hashtags
                    ])

        print("Tweets collection done, results in '{}'.".format(output_filename))

class TwitterElectionScraperThread(Thread):
    """
        Worker thread using the GetOldTweets library to get relevant tweets for
        the given got.manager.TweeterCriteria.
    """

    def __init__(self, candidate_index: int, criteria: got.manager.TweetCriteria):
        Thread.__init__(self)
        self.candidate_index = candidate_index
        self.criteria = criteria
        self.tweets = []

    def run(self):
        self.tweets = got.manager.TweetManager.getTweets(self.criteria)
