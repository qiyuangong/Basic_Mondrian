"""
main module of basic Mondrian
"""

# !/usr/bin/env python
# coding=utf-8


import pdb
import time

from models.numrange import NumRange
from models.partition import Partition


__DEBUG = False
QI_LEN = 10
GL_K = 0
RESULT = []
ATT_TREES = []
QI_RANGE = []
IS_CAT = []


def get_normalized_width(partition: Partition, qid_index: int) -> float:    
    """
    Return Normalized width of partition. Similar to NCP        

        Parameters
        ----------
        qid_index : int
            The index of the QID in the data
    """        

    if IS_CAT[qid_index] is False:
        low = partition.attribute_width_list[qid_index][0]
        high = partition.attribute_width_list[qid_index][1]
        width = float(ATT_TREES[qid_index].sort_value[high]) - float(ATT_TREES[qid_index].sort_value[low])
    else:
        width = partition.attribute_width_list[qid_index]

    return width * 1.0 / QI_RANGE[qid_index]


def choose_dimension(partition: Partition) -> int:
    """ Chooss QID with largest normlized Width and return its index. """

    max_norm_width = -1
    qid_index = -1

    for i in range(QI_LEN):
        if partition.attribute_split_allowed_list[i] == 0:
            continue
        
        normalized_width = get_normalized_width(partition, i)
        if normalized_width > max_norm_width:
            max_norm_width = normalized_width
            qid_index = i

    if max_norm_width > 1:
        print("Error: max_norm_width > 1")
        pdb.set_trace()
    if qid_index == -1:
        print("cannot find the max dim")
        pdb.set_trace()

    return qid_index


def frequency_set(partition, dim):
    """
    get the frequency_set of partition on dim
    return dict{key: str values, values: count}
    """
    frequency = {}
    for record in partition.members:
        try:
            frequency[record[dim]] += 1
        except KeyError:
            frequency[record[dim]] = 1
    return frequency


def find_median(partition, dim):
    """
    find the middle of the partition
    return splitVal
    """
    frequency = frequency_set(partition, dim)
    splitVal = ''
    value_list = list(frequency.keys())
    value_list.sort(key=lambda x: int(x))
    total = sum(frequency.values())
    middle = total / 2
    if middle < GL_K or len(value_list) <= 1:
        return ('', '', value_list[0], value_list[-1])
    index = 0
    split_index = 0
    for i, t in enumerate(value_list):
        index += frequency[t]
        if index >= middle:
            splitVal = t
            split_index = i
            break
    else:
        print("Error: cannot find splitVal")
    try:
        nextVal = value_list[split_index + 1]
    except IndexError:
        nextVal = splitVal
    return (splitVal, nextVal, value_list[0], value_list[-1])


def split_numerical_value(numeric_value, splitVal):
    """
    split numeric value on splitVal
    return sub ranges
    """
    split_num = numeric_value.split(',')
    if len(split_num) <= 1:
        return split_num[0], split_num[0]
    else:
        low = split_num[0]
        high = split_num[1]
        # Fix 2,2 problem
        if low == splitVal:
            lvalue = low
        else:
            lvalue = low + ',' + splitVal
        if high == splitVal:
            rvalue = high
        else:
            rvalue = splitVal + ',' + high
        return lvalue, rvalue


def split_numerical(partition, dim, pattribute_width_list, pattribute_generalization_list):
    """
    strict split numeric attribute by finding a median,
    lhs = [low, means], rhs = (mean, high]
    """
    sub_partitions = []
    # numeric attributes
    (splitVal, nextVal, low, high) = find_median(partition, dim)
    p_low = ATT_TREES[dim].dict[low]
    p_high = ATT_TREES[dim].dict[high]
    # update middle
    if low == high:
        pattribute_generalization_list[dim] = low
    else:
        pattribute_generalization_list[dim] = low + ',' + high
    pattribute_width_list[dim] = (p_low, p_high)
    if splitVal == '' or splitVal == nextVal:
        # update middle
        return []
    middle_pos = ATT_TREES[dim].dict[splitVal]
    lattribute_generalization_list = pattribute_generalization_list[:]
    rattribute_generalization_list = pattribute_generalization_list[:]
    lattribute_generalization_list[dim], rattribute_generalization_list[dim] = split_numerical_value(pattribute_generalization_list[dim], splitVal)
    lhs = []
    rhs = []
    for temp in partition.members:
        pos = ATT_TREES[dim].dict[temp[dim]]
        if pos <= middle_pos:
            # lhs = [low, means]
            lhs.append(temp)
        else:
            # rhs = (mean, high]
            rhs.append(temp)
    lattribute_width_list = pattribute_width_list[:]
    rattribute_width_list = pattribute_width_list[:]
    lattribute_width_list[dim] = (pattribute_width_list[dim][0], middle_pos)
    rattribute_width_list[dim] = (ATT_TREES[dim].dict[nextVal], pattribute_width_list[dim][1])
    sub_partitions.append(Partition(lhs, lattribute_width_list, lattribute_generalization_list, QI_LEN))
    sub_partitions.append(Partition(rhs, rattribute_width_list, rattribute_generalization_list, QI_LEN))
    return sub_partitions


def split_categorical(partition, dim, pattribute_width_list, pattribute_generalization_list):
    """
    split categorical attribute using generalization hierarchy
    """
    sub_partitions = []
    # categoric attributes
    splitVal = ATT_TREES[dim][partition.attribute_generalization_list[dim]]
    sub_node = [t for t in splitVal.child]
    sub_groups = []
    for i in range(len(sub_node)):
        sub_groups.append([])
    if len(sub_groups) == 0:
        # split is not necessary
        return []
    for temp in partition.members:
        qid_value = temp[dim]
        for i, node in enumerate(sub_node):
            try:
                node.cover[qid_value]
                sub_groups[i].append(temp)
                break
            except KeyError:
                continue
        else:
            print("Generalization hierarchy error!")
    flag = True
    for index, sub_group in enumerate(sub_groups):
        if len(sub_group) == 0:
            continue
        if len(sub_group) < GL_K:
            flag = False
            break
    if flag:
        for i, sub_group in enumerate(sub_groups):
            if len(sub_group) == 0:
                continue
            wtemp = pattribute_width_list[:]
            mtemp = pattribute_generalization_list[:]
            wtemp[dim] = len(sub_node[i])
            mtemp[dim] = sub_node[i].value
            sub_partitions.append(Partition(sub_group, wtemp, mtemp, QI_LEN))
    return sub_partitions


def split_partition(partition, dim):
    """
    split partition and distribute records to different sub-partitions
    """
    pattribute_width_list = partition.attribute_width_list
    pattribute_generalization_list = partition.attribute_generalization_list
    if IS_CAT[dim] is False:
        return split_numerical(partition, dim, pattribute_width_list, pattribute_generalization_list)
    else:
        return split_categorical(partition, dim, pattribute_width_list, pattribute_generalization_list)


def anonymize(partition):
    """
    Main procedure of Half_Partition.
    recursively partition groups until not allowable.
    """
    # print(len(partition)
    # print(partition.attribute_split_allowed_list
    # pdb.set_trace()
    if check_splitable(partition) is False:
        RESULT.append(partition)
        return
    # Choose dim
    dim = choose_dimension(partition)
    if dim == -1:
        print("Error: dim=-1")
        pdb.set_trace()
    sub_partitions = split_partition(partition, dim)
    if len(sub_partitions) == 0:
        partition.attribute_split_allowed_list[dim] = 0
        anonymize(partition)
    else:
        for sub_p in sub_partitions:
            anonymize(sub_p)


def check_splitable(partition):
    """
    Check if the partition can be further splited while satisfying k-anonymity.
    """
    temp = sum(partition.attribute_split_allowed_list)
    if temp == 0:
        return False
    return True


def init(att_trees, data, k, QI_num=-1):
    """
    reset all global variables
    """
    global GL_K, RESULT, QI_LEN, ATT_TREES, QI_RANGE, IS_CAT
    ATT_TREES = att_trees
    for t in att_trees:
        if isinstance(t, NumRange):
            IS_CAT.append(False)
        else:
            IS_CAT.append(True)
    if QI_num <= 0:
        QI_LEN = len(data[0]) - 1
    else:
        QI_LEN = QI_num
    GL_K = k
    RESULT = []
    QI_RANGE = []


def mondrian(att_trees, data, k, QI_num=-1):
    """
    basic Mondrian for k-anonymity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    init(att_trees, data, k, QI_num)
    result = []
    attribute_generalization_list = []
    wtemp = []
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            QI_RANGE.append(ATT_TREES[i].range)
            wtemp.append((0, len(ATT_TREES[i].sort_value) - 1))
            attribute_generalization_list.append(ATT_TREES[i].value)
        else:
            QI_RANGE.append(len(ATT_TREES[i]['*']))
            wtemp.append(len(ATT_TREES[i]['*']))
            attribute_generalization_list.append('*')
    whole_partition = Partition(data, wtemp, attribute_generalization_list, QI_LEN)
    start_time = time.time()
    anonymize(whole_partition)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    for partition in RESULT:
        r_ncp = 0.0
        for i in range(QI_LEN):
            r_ncp += get_normalized_width(partition, i)
        temp = partition.attribute_generalization_list
        for i in range(len(partition)):
            result.append(temp + [partition.members[i][-1]])
        r_ncp *= len(partition)
        ncp += r_ncp
    # covert to NCP percentage
    ncp /= QI_LEN
    ncp /= len(data)
    ncp *= 100
    if len(result) != len(data):
        print("Losing records during anonymization!!")
        pdb.set_trace()
    if __DEBUG:
        print("K=%d" % k)
        print("size of partitions")
        print(len(RESULT))
        temp = [len(t) for t in RESULT]
        print(sorted(temp))
        print("NCP = %.2f %%" % ncp)
    return (result, (ncp, rtime))
