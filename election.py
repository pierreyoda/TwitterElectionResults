# -*- coding: utf-8 -*-

"""
    Module defining the data models fed to the TER forecaster.
"""

import json
import datetime as dt

class CandidateData:
    """
        Stores all the necessary data defining a candidate to an election.
    """

    def __init__(self, party: [str], names: [str], poll_score: float, real_score: float):
        self.party = party
        self.names = names
        self.poll_score = poll_score # percentage of votes in the lastest polls before the election
        self.real_score = real_score # the percentage of votes in the actual election (None: N/A)

    def __repr__(self) -> str:
        return """CandidateData
            \t- party = {}
            \t- names = {}
            \t- real score = {}
            \t- poll score = {}""".format(
                ", ".join(self.party),
                ", ".join(self.names),
                "{} %".format(self.real_score) if self.real_score is not None else "N/A",
                "{} %".format(self.poll_score)
            )

class ElectionDataset:
    """
        Modelizes an election.
    """

    def __init__(self):
        self.date = dt.date.today()
        self.twitter_campaign_duration = dt.timedelta(days=30)
        self.candidates = {}

    @staticmethod
    def from_file(filename: str):
        """Build a new ElectionDatase from the given JSON file.

        The configuration format is as following :
        {
            "election_date": "YYYY-MM-dd" (for instance: "2014-03-23"),
            "campaign_duration": "[number]d [number]w" (d: days, w: weeks),
            "candidates": {
                "[candidate name]": {
                    "names": ["list", "of", "candidate", "names"],
                    "party": ["list", "of", "party", "names"],
                    "real_score": "none" or "xx.xx" (for instance: "53.2" % of the popular vote)
                    "poll_score": "xx.xx" (percentage)
                },
                [other candidates...]
            }
        }
        """

        dataset = ElectionDataset()
        with open(filename) as file:
            data = json.load(file)

            # parse election date
            dataset.date = dt.datetime.strptime(data["election_date"], "%Y-%m-%d")

            # parse twitter campaign duration
            duration = dt.timedelta()
            durations = data["campaign_duration"].split(' ')
            for fragment in durations:
                if len(fragment) < 2:
                    print("Invalid campaign duration ('{}') : ignoring.".format(fragment))
                    continue
                kind = fragment[-1] # get the last character
                number = int(fragment[:-1])
                if kind == "d": # days
                    duration += dt.timedelta(days=number)
                elif kind == "w": # weeks
                    duration += dt.timedelta(weeks=number)
                else:
                    print("Invalid campaign duration unit ('{}') : ignoring.".format(kind))
            dataset.twitter_campaign_duration = duration

            # load candidate date
            for candidate, candidate_data in data["candidates"].items():
                real_score, poll_score = None, None
                if candidate_data["real_score"] is not None:
                    if candidate_data["real_score"].lower() != "none":
                        real_score = float(candidate_data["real_score"])
                if candidate_data["poll_score"] is not None:
                    poll_score = float(candidate_data["poll_score"])
                dataset.candidates[candidate] = CandidateData(
                    party=candidate_data["party"],
                    names=candidate_data["names"],
                    poll_score=poll_score,
                    real_score=real_score
                )

        return dataset

    def __repr__(self) -> str:
        return "ElectionDataset" \
            + "\n\tdata = {}".format(self.date) \
            + "\n\tduration = {}".format(self.twitter_campaign_duration) \
            + "\n\tcandidates = {{\n\t{}".format("\n\n\t".join(
                [repr(c) for c in self.candidates.values()])) \
            + "\n\t}"

def get_test_dataset() -> ElectionDataset:
    """Build and return a proper ElectionDataset for test purposes."""

    dataset = ElectionDataset()
    dataset.date = dt.date(2016, 11, 8)
    dataset.twitter_campaign_duration = dt.timedelta(days=60)

    candidate_clinton = CandidateData(party=['Democratic Party', 'democrats', 'dems', 'DNC'],
                                      names=['Hillary Clinton', 'HC', 'Clinton', 'Hillary'],
                                      real_score=48.2, poll_score=45.9)
    candidate_trump = CandidateData(party=['Republican Party', 'reps', 'republicans', 'GOP'],
                                    names=['Donald John Trump', 'Donald Trump', 'Trump'],
                                    real_score=46.1, poll_score=42.8)

    dataset.candidates = {'Clinton': candidate_clinton, 'Trump': candidate_trump}

    return dataset
