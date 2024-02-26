import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

input_text = input("Enter the text for entity recognition (type 'exit' to end): ")

doc = nlp(input_text)

options = {"compact": True, "color": "blue"}

displacy.serve(doc, auto_select_port=True, style="ent")
displacy.serve(doc, auto_select_port=True, style="dep", options=options)
