"""
Retrieve publication list for Rice solar physics research group from ADS
"""
import os
import argparse
import datetime

import yaml
import ads

PROPERTIES = ['author', 'year', 'pub', 'bibcode', 'title']
OTHER_PROPERTIES = ['citation', 'pubdate', 'property']
AFF = 'Rice'


def get_people(people_list):
    if os.path.exists(people_list):
        with open(people_list, 'r') as f:
            people = yaml.load(f)
        return [pn for p in people if 'pub_name' in p for pn in p['pub_name']]
    else:
        return people_list.split(',')


def query_ads(people):
    """
    Query ads for given list of people for given affiliation
    """
    all_pubs = []
    for p in people:
        query = list(ads.SearchQuery(author=p, aff=AFF, fl=PROPERTIES+OTHER_PROPERTIES))
        for q in query:
            if not accept_publication(q):
                continue
            tmp = {p: q.__dict__[p] for p in PROPERTIES}
            tmp['year'] = int(tmp['year'])
            tmp['rs_author'] = [a for a in q.author if a in people]
            tmp['citation_count'] = len(q.citation) if q.citation is not None else 0
            tmp['date'] = '-'.join(['01' if dt == '00' else dt for dt in q.pubdate.split('-')])
            all_pubs.append(tmp)

    return all_pubs


def accept_publication(pub):
    """
    Reject some publications. Add any conditions here.
    """
    if 'NOT REFEREED' in pub.property:
        return False
    if len(pub.author) > 10:
        return False
    return True


def sort_and_filter(pubs):
    """
    Sort by year and remove duplicates
    FIXME: why so many duplicates?
    """
    pubs = sorted(pubs, key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
    unique_pubs = []
    for p in pubs:
        if p['title'] in [up['title'] for up in unique_pubs]:
            continue
        else:
            unique_pubs.append(p)

    return unique_pubs


def write_publication_file(filename, pubs):
    """
    Write publications to YAML file
    """
    years = sorted(list(set([int(p['year']) for p in pubs])), reverse=True)
    pubs = {'pubs': pubs, 'years': years}
    with open(filename, 'w') as f:
        f.write(yaml.dump(pubs, default_flow_style=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build publication list from ADS for Rice Solar group')
    parser.add_argument("-k", "--ads_key", help="Path to file containing ADS key needed to query database")
    parser.add_argument("-f", "--pub_file", help="YAML file to write publication entries to")
    parser.add_argument("-p", "--people", help="YAML file containing author info or comma-delimited author list")
    args = parser.parse_args()
    
    if os.path.exists(args.ads_key):
        with open(args.ads_key,'r') as f:
            args.ads_key = f.read()
    ads.config.token = args.ads_key
    
    pubs = sort_and_filter(query_ads(get_people(args.people)))
    write_publication_file(args.pub_file, pubs)
    