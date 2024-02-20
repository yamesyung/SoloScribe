import spacy

nlp = spacy.load("en_core_web_sm")

input_text = input("Enter the text for entity recognition (type 'exit' to end): ")

doc = nlp(input_text)

for ent in doc.ents:
    print(f"Entity: {ent.text}, Type: {ent.label_}")
