import json
import sys


def identify_missing(file):
    pasurams = set()
    dupes = set()
    with open(file) as f:
        for line in f:
            item = json.loads(line)
            number = item['number']
            if number in pasurams:
                dupes.add(number)
            pasurams.add(item['number'])
            check_fields_missing(item)

    missing = set()
    for i in range(1, 11):
        for j in range(1, 11):
            limit = 12
            if i == 2 and j == 7:
                # kesavan thamar
                limit = 14
            for k in range(1, limit):
                p = '%s.%s.%s' % (i, j, k)
                if not p in pasurams:
                    missing.add(p)

    if len(missing):
        print('Missing: ', missing)
    if len(dupes):
        print('Dupes: ', dupes)


def check_fields_missing(item):
    missing_fields = []
    for k, v in item.items():
        if not v:
            missing_fields.append(k)
    if len(missing_fields):
        print(item['number'], 'is missing', missing_fields)
            
    
if __name__ == "__main__":
    identify_missing(sys.argv[1])
