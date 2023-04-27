class Partition(object):

    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.members: records in the partition
    Lists that store for each QID, under the index for the corresponding attribute,
        self.attribute_width_list: the width, for categoric attribute, it equal the number of leaf node, for numeric attribute, it equal to number range
        self.attribute_generalization_list: the result of the generalization
        self.allow: 0 if the partition cannot be split further along the attribute, 1 otherwise
    """

    def __init__(self, data, attribute_width_list, attribute_generalization_list, qi_len):
        self.members = list(data)
        self.attribute_width_list = list(attribute_width_list)
        self.attribute_generalization_list = list(attribute_generalization_list)
        self.attribute_split_allowed_list = [1] * qi_len

    # The number of records in partition
    def __len__(self):        
        return len(self.members)