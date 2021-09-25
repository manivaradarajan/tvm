import json
import sys


def read_lines(file):
    pasurams = set()
    with open(file) as f:
        for line in f:
            item = json.loads(line)
            pasurams.add(item['number'])
    for i in range(1, 10):
        for j in range(1, 10):
            limit = 11
            if i == 2 and j == 7:
                # kesavan thamar
                limit = 13
            for k in range(1, limit):
                p = '%s.%s.%s' % (i, j, k)
                if not p in pasurams:
                    print('Missing', p)
            
    
if __name__ == "__main__":
    read_lines(sys.argv[1])
