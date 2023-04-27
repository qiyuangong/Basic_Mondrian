#!/usr/bin/env python
# coding=utf-8

# Read data and read tree fuctions for ADULTS data
#
# Format:
#   ['age', 'workcalss', 'final_weight', 'education', 'education_num', !marital_status', 'occupation', 'relationship', 'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week', 'native_country', 'class']
#   39, State-gov, 77516, Bachelors, 13, Never-married, Adm-clerical, Not-in-family, White, Male, 2174, 0, 40, United-States, <=50K
#   50, Self-emp-not-inc, 83311, Bachelors, 13, Married-civ-spouse, Exec-managerial, Husband, White, Male, 0, 0, 13, United-States, <=50K
#   38, Private, 215646, HS-grad, 9, Divorced, Handlers-cleaners, Not-in-family, White, Male, 0, 0, 40, United-States, <=50K
#
# Attributes 
#   [   'age',  'workcalss',        'final_weight',     'education',    'education_num',    !marital_status',       'occupation',       'relationship',     'race',     'sex',      'capital_gain',     'capital_loss',     'hours_per_week',       'native_country',   'class']
#       39,     State-gov,          77516,              Bachelors,      13,                 Never-married,          Adm-clerical,       Not-in-family,      White,      Male,       2174,               0,                  40`,                    United-States,      <=50K
#       50,     Self-emp-not-inc,   83311,              Bachelors,      13,                 Married-civ-spouse,     Exec-managerial,    Husband,            White,      Male,       0,                  0,                  13,                     United-States,      <=50K
#
# QIDs
#   ['age', 'workcalss', 'education', 'matrital_status', 'race', 'sex', 'native_country']
#
# SA 
#   ['occopation']

from models.gentree import GenTree
from models.numrange import NumRange

import pickle
import pdb

ATT_NAMES = ['age', 'workclass', 'final_weight', 'education',
             'education_num', 'marital_status', 'occupation', 'relationship',
             'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
             'native_country', 'class']
# 8 attributes are chose as QI attributes
# age and education levels are treated as numeric attributes
# only matrial_status and workclass has well defined generalization hierarchies, other categorical attributes only have 2-level generalization hierarchies.
QI_INDEX = [0, 1, 4, 5, 6, 8, 9, 13]
IS_CAT = [False, True, False, True, True, True, True, True]
SA_INDEX = -1

__DEBUG = False


# Filter out the QIDs and the SA from the original data file
def read_data() -> list[list[str]]:
    """ Read microda for *.txt and return read data """
    
    # The number of QIDs
    QI_num = len(QI_INDEX)
    # Data with the QID and SA values only
    data = []
    numeric_dict = []

    # For all QID attribute, create a dedicated array in the numeric_dict array
    for i in range(QI_num):
        numeric_dict.append(dict())

    # other categorical attributes in intuitive order
    # here, we use the appear number
    data_file = open('data/adult.data', newline=None)

    # Extract the QID attributes and the sensitive attribute into the data variable
    for line in data_file:
        # Remove spaces at the beginning and at the end of the string
        line = line.strip()
        # Remove empty and incomplete lines >> only 30162 records will be kept
        if len(line) == 0 or '?' in line:
            continue
        # Remove spaces from between attribute values
        line = line.replace(' ', '')
        # Split the line along commas, creating an array that stores the attribute values from the current line
        temp = line.split(',')

        ltemp = []

        for i in range(QI_num):
            # Get the index of the current attribute in the original data (nth column it is located in)
            index = QI_INDEX[i]

            # Store how many times each unique value of numerical attributes show up
            if IS_CAT[i] is False:
                try:
                    numeric_dict[i][temp[index]] += 1
                except KeyError:
                    numeric_dict[i][temp[index]] = 1
                    # Copy each attribute value of the line from the temp array to the ltemp array
            ltemp.append(temp[index])

        # Add the sensitive attribute value to the ltemp array
        ltemp.append(temp[SA_INDEX])
        data.append(ltemp)

    # Write the information gathered about the various numeric attributes values into a new file, through the serialization library named pickle
    # Parsing happens through read_pickle_file
    for i in range(QI_num):
        if IS_CAT[i] is False:
            static_file = open('data/adult_' + ATT_NAMES[QI_INDEX[i]] + '_static.pickle', 'wb')
            sort_value = list(numeric_dict[i].keys())
            sort_value.sort(key=lambda x: int(x))
            pickle.dump((numeric_dict[i], sort_value), static_file)
            static_file.close()

    return data


def read_tree():
    """read tree from data/tree_*.txt, store them in att_tree
    """
    att_names = []
    att_trees = []
    for t in QI_INDEX:
        att_names.append(ATT_NAMES[t])
    for i in range(len(att_names)):
        if IS_CAT[i]:
            att_trees.append(read_tree_file(att_names[i]))
        else:
            att_trees.append(read_pickle_file(att_names[i]))
    return att_trees


def read_pickle_file(att_name):
    """
    read pickle file for numeric attributes
    return numrange object
    """
    try:
        static_file = open('data/adult_' + att_name + '_static.pickle', 'rb')
        (numeric_dict, sort_value) = pickle.load(static_file)
    except:
        print("Pickle file not exists!!")
    static_file.close()
    result = NumRange(sort_value, numeric_dict)
    return result


def read_tree_file(treename):
    """read tree data from treename
    """
    leaf_to_path = {}
    att_tree = {}
    prefix = 'data/adult_'
    postfix = ".txt"
    treefile = open(prefix + treename + postfix, newline=None)
    att_tree['*'] = GenTree('*')
    if __DEBUG:
        print("Reading Tree" + treename)
    for line in treefile:
        # delete \n
        if len(line) <= 1:
            break
        line = line.strip()
        temp = line.split(';')
        # copy temp
        temp.reverse()
        for i, t in enumerate(temp):
            isleaf = False
            if i == len(temp) - 1:
                isleaf = True
            # try and except is more efficient than 'in'
            try:
                att_tree[t]
            except:
                att_tree[t] = GenTree(t, att_tree[temp[i - 1]], isleaf)
    if __DEBUG:
        print("Nodes No. = %d" % att_tree['*'].support)
    treefile.close()
    return att_tree
