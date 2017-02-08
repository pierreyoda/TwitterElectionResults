# -*- coding: utf-8 -*-

"""Main entry point for the TER forecasting system."""

import os.path
import argparse
import election
import scraper
import ter

def is_positive_integer(value):
    """Return True if the given value is a positive number, and False otherwise.
    Used with argparse to enforce a command line argument as a positive integer."""
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("'{}' is an invalid positive integer value"
                                             .format(value))
        return ivalue
    except ValueError: # int conversion error
        raise argparse.ArgumentTypeError("'{}' is an invalid integer value".format(value))

if __name__ == '__main__':
    # parse the command line arguments (with the standard module argparse)
    parser = argparse.ArgumentParser(description="Twitter Election Results")
    parser.add_argument('--mode',
                        default="predict",
                        type=str,
                        choices=["collect", "predict", "both"],
                        help="""Mode : 'collect' for collecting election tweets, 'predict' for
                        forecasting an election from its collected tweets, or "both" for doing both. 
                        Predict by default.""")
    parser.add_argument('--limit',
                        default="1000",
                        type=is_positive_integer,
                        help="""Define the maximum number of tweets collected for each candidate.
                        0 means unlimited (warning : can be very long). 1000 by default.""")
    parser.add_argument('election',
                        type=str,
                        help="""Choose the filename defining the election
                        (relative to the '/election/' folder). The collected tweets and/or
                        the forecasts will be stored respectively in the '/tweets/
                        and '/elections/' folders, with the same filename.""")

    args = parser.parse_args()
    election_name = args.election
    ter_mode = ["collect", "predict"] if (args.mode == "both") else [args.mode]
    tweets_limit = int(args.limit)

    # define the input (election JSON config) and output files (tweets and/or forecasts)
    election_config_file = "elections/{}.json".format(election_name)
    election_tweets_file = "tweets/{}.csv".format(election_name)
    election_prediction_file = "predictions/{}.csv".format(election_name)

    # check if the config election file does exist
    if not os.path.isfile(election_config_file):
        print("The election definition file '{}' cannot be found, aborting."
              .format(election_config_file))
        exit(1)

    # get the election metadata from that file
    election_data = election.ElectionDataset.from_file(election_config_file)
    print(election_data)

    # tweets scrapping
    if "collect" in ter_mode:
        scraper = scraper.TwitterElectionScraper(election_data)
        scraper.run(election_tweets_file, max_tweets=tweets_limit) # 0 : unlimited

    # election forecasting
    if "predict" in ter_mode:
        if not os.path.isfile(election_tweets_file):
            print("The collected tweeter file '{}' cannot be found, aborting.".format(
                election_tweets_file))
            exit(1)
        forecaster = ter.TwitterElectionResults(election_data, election_tweets_file)
        forecaster.forecast(election_prediction_file)
