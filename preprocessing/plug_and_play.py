import re, os, csv
from xml.dom import minidom
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB, ComplementNB
from nltk import TweetTokenizer

curr_dir = os.path.dirname(os.path.abspath(__file__))


def file_parsing(infile_path: str, outfile_path: str, query_or_answer: str):

    """
    This function parses the input file which is a txt and converts it into a csv with a header containing
    the info about the columns of said file. The txt file should have a label followed by a tab and a query, or
    two or more labels separated by the character ":", then a tab and then a query. The csv file will have the
    number of columns corresponding to the number of labels + 1. If it is only a label, it will have the
    columns label and query (the header will be label*query) and if it has more labels, the columns will be
    label1, label2, ..., labeln and query (the header will be label1*label2*...*labeln*query).

    :param infile_path: path of the file that contains a corpus (should be .txt)
    :param outfile_path: path of the file generated (.csv) from the corpus .txt file
    :return: generates a file, but it does not return anything.
    """

    input_file = open(infile_path, 'r')
    output_file = open(outfile_path, 'w')
    csv.writer(output_file, delimiter='*',quotechar =',',quoting=csv.QUOTE_MINIMAL)
    lines = list(input_file)

    # Obtains a list of tags
    tags_getter = lines[0].split('\t')
    tags_getter = tags_getter[0].split(':')
    to_write = ''
    string_format = ''

    # Verify if there are only one or more tags in order to build the header for the .csv file
    if len(tags_getter) == 1:
        to_write = 'label*' + query_or_answer + '\n'
        string_format = '{}*{}'
    else:
        count = 1
        while count<=len(tags_getter):
            to_write += 'label' + str(count) + '*'
            string_format += '{}*'  # This variable will be used further ahead in order for the writer to know how it
            # should write the columns of the csv file
            count += 1
        to_write += query_or_answer + '\n'
        string_format += '{}'
    output_file.write(to_write)
    for line in lines:
        params = []
        line_array = line.strip().split('\t')
        for el in line_array[0].split(':'):
            params.append(el)
        params.append(line_array[1])
        params = tuple(params)

        if len(line_array) < 2:
            raise Exception('Format of the file must be "label\tquery" or "label1:label2\tquery" or '
                            'multiple labels separated by two vertical dots and then a tab and then a query.')

        output_file.write(string_format.format(*params) + '\n')
    input_file.close()
    output_file.close()


