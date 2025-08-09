# import spacy
# nlp = spacy.load("en_core_web_trf")
# doc1 = nlp("We live in Spokane and want to start IVF soon.")
# doc2 = nlp("Spokane is bad")
# doc3 = nlp("Orange is spherical in shape but Jackson,Wyoming is not")
# doc4 = nlp("11370 Anderson St, Loma Linda, CA 92354")
# loc1 = [ent.text for ent in doc1.ents if ent.label_ == "GPE"]
# loc2 = [ent.text for ent in doc2.ents if ent.label_ == "GPE"]
# loc3 = [ent.text for ent in doc3.ents if ent.label_ == "GPE"]
# loc4 = [ent.text for ent in doc4.ents if ent.label_ == "GPE"]
# # -> ["Los Angeles"]
# print(loc1)
# print(loc2)
# print(loc3)
# print(loc4)

import spacy

nlp = spacy.load("en_core_web_trf")


def extract_location(prompt):
    print("Extracting Location")
    doc = nlp(prompt)
    locs = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    if locs:
        return locs[0]
    return None








