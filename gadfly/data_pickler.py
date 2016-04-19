import pickle
import numpy
import statistics
import random
import spacy_singleton
from multiprocessing.dummy import Pool as ThreadPool

"""
There must be better ways to incorporate cities. Perhaps better threading.
Perhaps better splitting of categories of cities.
See: acknowledgements.md

(1) pickle_state_abreviations()
This creates a simple dictionary to check AP style state name abbreviations.


"""


def pickle_state_abreviations():
    us_state_abbreviations = {"Ala.": "Alabama", "Neb.": "Nebraska",
                              "Ariz.": "Arizona", "Nev.": "Nevada",
                              "Ark.": "Arkansas", " N.H.": "New Hampshire",
                              "Calif.": "California", "N.J.": "New Jersey",
                              "Colo.": "Colorado", "N.M.": "New Mexico",
                              "Conn.": "Connecticut", "N.Y.": "New York",
                              "Del.": "Delaware", " N.C.": "North Carolina",
                              "Fla.": "Florida", " N.D.": "North Dakota",
                              "Ga.": "Georgia", "Okla.": "Oklahoma",
                              "Ill.": "Illinois", "Ore.": "Oregon",
                              "Ind.": "Indiana", "Pa.": "Pennsylvania",
                              "Kan.": "Kansas", "R.I.": "Rhode Island",
                              "Ky.": "Kentucky", "S.C.": "South Carolina",
                              "La.": "Louisiana", "S.D.": "South Dakota",
                              "Md.": "Maryland", "Tenn.": "Tennessee",
                              "Mass.": "Massachusetts", "Vt.": "Vermont",
                              "Mich.": "Michigan", "Va.": "Virginia",
                              "Minn.": "Minnesota", "Wash.": "Washington",
                              "Miss.": "Mississippi", "W.Va.": "West Virginia",
                              "Mo.": "Missouri", "Wis.": "Wisconsin",
                              "Mont.": "Montana", "Wyo.": "Wyoming"}

    pickle.dump(us_state_abbreviations, open(
      "reference_data/_us_state_abbreviations_dict.p", "wb"))


def most_similar_spans(tgt):
    bag = entities
    similarities = [(ent, str(numpy.round(numpy.array(
                                          [ent.similarity(tgt)]),
                                          3))) for ent in bag]
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    similarities = list(set([span.text_with_ws.strip() for span,
                             sim in similarities]))

    return tgt.text_with_ws.strip(), similarities[1:10]


def find_prob(span):
    span_prob = statistics.mean([token.prob for token in span])
    return span, span_prob


def pickle_gpe():
    _gpe_dict = dict()
    gpe_files = ["us_states.txt", "countries.txt", "continents.txt"]
    for each in gpe_files:
        print(each)
        f = open("reference_data/"+each, "r")
        gpes = f.readlines()
        f.close()
        gpes = ", ".join((gpes))
        parsed_text = spacy_singleton.spacy_en()(gpes)
        print("Text parsed...")
        global entities
        entities = [ent for ent in parsed_text.ents
                    if ent.label_ != ""]
        print("Entities complete...")

        # Make the Pool of workers
        pool = ThreadPool(50)
        print("Created Pool #2...")
        results = pool.map(most_similar_spans, entities)
        print("Results created...")
        # close the pool and wait for the work to finish
        pool.close()
        print("Pool #2 closed...")
        pool.join()
        print("Pool #2 joined...")

        for name, alts in results:
            _gpe_dict[name] = (each[:-4], alts)

        print("{} _gpe_dict_ entries added.".format(len(_gpe_dict)))

    pickle.dump(_gpe_dict, open("reference_data/_gpe_dict.p", "wb"))


def pickle_cities():
    _gpe_cities_dict = dict()
    gpe_cities_files = ["us_cities.txt", "cities.txt"]
    for each in gpe_cities_files:
        with open("reference_data/"+each, "r") as f:
            _gpe_cities_dict = {city.strip(): "city" for city in f.readlines()}
    pickle.dump(_gpe_cities_dict, open("reference_data/_gpe_cities_dict.p",
                                       "wb"))

pickle_gpe()
