import config
import requests
from scrape import linkedin_scrapper


class KeywordExtractor:
    def __init__(self, person_dict):
        self.text = ""
        self.person_dict = person_dict
        self.keywords = ""

        self.extract_information()
        if self.text != "":
            self.extract_keywords()

    def extract_information(self):
        for x in self.person_dict["Interests"].keys():
            if x == 'Companies':
                pass
            elif x == 'Influencers':
                y = self.person_dict["Interests"][x]
                for z in y:
                    self.text += z["Description"] + '. '

        if "Recent Activities" in self.person_dict:
            for x in self.person_dict["Recent Activities"]:
                    y = x["Author Description"]
                    self.text += (y+'. ') if y is not None else ''

    def extract_keywords(self):
        r = requests.post(
            "https://api.deepai.org/api/text-tagging",
            data={'text': self.text},
            headers={'api-key': config.api_key}
        )
        self.keywords = r.json()['output']


def linkedin_data(profile_link):
    person_dict = linkedin_scrapper(profile_link=profile_link)
    person = KeywordExtractor(person_dict=person_dict)
    person_dict["keywords"] = person.keywords.split("\n")
    return person_dict

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == "__main__":
    x = linkedin_data("https://www.linkedin.com/in/richardyang98/")
    # print("People Following: ")
    # print('\t'+y for y in x['Interests']['Influencers'])
    # print()
    print("Industries Following: ")
    z = set([y["Industry"] for y in x['Interests']['Companies']])
    for y in z:
        print('\t' + y)
    print()
    print("Keywords: ")
    for y in x["keywords"]:
        print('\t' + y)
    printProgressBar(7, 7, "exiting\t\t\t\t\t\t\t", "Complete", length=50, printEnd="\r\n")
