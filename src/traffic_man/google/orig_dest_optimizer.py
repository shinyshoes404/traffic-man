import math, copy
import pandas as pd
from traffic_man.config import Config


# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class OrigDestOptimizer:

    def __init__(self, orig_dest_list: list, dest_limit=25, element_limit=100):
        # expecting a distcint list of tuples from a sqlalchemy query result
        # ex: [("DhIJr7A7RcQEyYcRfYNPekurSZQ", "JrIJr7A7RcQEyYcRfYNPekurSZ1"), ("DhIJr7A7RcQEyYcRfYNPekurSZQ", "XsIJr7A7RcQEyYcRfYNPekurSnT")]
        self.orig_dest_data = orig_dest_list
        self.dest_limit = dest_limit
        self.element_limit = element_limit
    
    def get_orig_dest_list(self) -> list:
        data_shaped = self._shape_data()
        dest_breakdown_data = self._dest_breakdown(data_shaped)
        final_orig_dest_data = self._group_orig_dest(dest_breakdown_data)
        if self._verify_result(final_orig_dest_data):
            logger.info("origin destination list has been optimized for Google api requests")
            return final_orig_dest_data
        else:
            logger.error("the data provided does not match the data after optimizing for Google api requests")
            logger.error("\t data provided:\n\t {0}".format(self.orig_dest_data))
            logger.error("\t data after optimize:\n\t {0}".format(final_orig_dest_data))
            return None

    def _shape_data(self) -> list:
        df = pd.DataFrame(self.orig_dest_data, columns=["origin", "destination"])
        orig_distinct = df.origin.unique().tolist()
        data_shaped = []
        for orig in orig_distinct:
            dest = df.query("origin == '" + orig + "'").destination.unique().tolist()
            data_shaped.append([[orig], len(dest), [copy.deepcopy(dest)]])
        
        return data_shaped
    
    # breakdown large destination lists to less than the dest_limit
    def _dest_breakdown(self, data_shaped: list) -> list:
        dest_list_breakdown = []
        for i in range(1, len(data_shaped) + 1):
            if data_shaped[-1*i][1] > self.dest_limit:
                full_dest_count = math.floor(data_shaped[-1*i][1]/self.dest_limit)
                remainder = data_shaped[-1*i][1] % self.dest_limit
                if remainder > 0:
                    # append the remainder destination records (from the end of the list) to te temporary list
                    dest_list_breakdown.append([data_shaped[-1*i][0], remainder, [data_shaped[-1*i][2][0][-1*remainder:]]])
                if full_dest_count > 0:
                    for j in range(1, full_dest_count+1):
                        dest_list_breakdown.append([data_shaped[-1*i][0], self.dest_limit, [data_shaped[-1*i][2][0][j-1:self.dest_limit*j]]])
            else:
                dest_list_breakdown.extend(data_shaped[0:len(data_shaped)-i+1])
                break
        
        return dest_list_breakdown
    
    # assembled broken down destination lists into more efficient groupings for google's distance matrix api
    def _group_orig_dest(self, dest_list_breakdown: list) -> list:

        # sort the intermediate data by dest count
        dest_list_breakdown.sort(key = lambda i: i[1])

        # start at the end of the list and work backward - if the dest set is already at the dest_limit, just add it to our final data set
        # if the dest set is less than dest_limit look for a match at the beginning of the list
        final_data_set = []
        j = 0
        for i in range(1, len(dest_list_breakdown)+1):
            if dest_list_breakdown[-1*i][1] >= self.dest_limit:
                final_data_set.append(copy.deepcopy(dest_list_breakdown[-1*i]))
            else:
                temp_data_element = copy.deepcopy(dest_list_breakdown[-1*i])
                for k in range(j, len(dest_list_breakdown) - i):
                    if temp_data_element[1] + dest_list_breakdown[k][1] <= self.dest_limit:
                        if (len(temp_data_element[0]) + len(dest_list_breakdown[k][0])) * (temp_data_element[1] + dest_list_breakdown[k][1]) <= self.element_limit:
                            # if both of our criteria are met, add this org/dest element to our temp data
                            # extend the origin list
                            temp_data_element[0].extend(copy.deepcopy(dest_list_breakdown[k][0]))
                            # update the destination count
                            temp_data_element[1] = temp_data_element[1] + len(dest_list_breakdown[k][2][0])
                            # append the destination list
                            temp_data_element[2].append(copy.deepcopy(dest_list_breakdown[k][2][0]))
                            j = j + 1
                        else:
                            break
                    
                    else:
                        break            

                final_data_set.append(copy.deepcopy(temp_data_element))

            if len(dest_list_breakdown) - i == j:
                break
        
        return final_data_set

    def _verify_result(self, final_data_set: list) -> bool:
        
        original_data = []
        for pair in self.orig_dest_data:
            original_data.append(pair[0] + "|" + pair[1])
        
        original_data.sort()

        final_org_dest_data = []
        for data in final_data_set:
            i = 0
            for orig in data[0]:
                for dest in data[2][i]:
                    final_org_dest_data.append(orig + "|" + dest)
                i = i + 1

        final_org_dest_data.sort()

        if original_data == final_org_dest_data:
            return True
        else:
            return False


