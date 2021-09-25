import json
import sys


def identify_missing(file):
    pasurams = set()
    with open(file) as f:
        for line in f:
            item = json.loads(line)
            pasurams.add(item['number'])

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

    print(missing)
            
    
if __name__ == "__main__":
    identify_missing(sys.argv[1])
