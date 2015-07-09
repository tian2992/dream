from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class ReadExcelEasyWIP(plugin.InputPreparationPlugin):
    """ Input preparation 
        reads the WIP as the user uploads in a spreadsheet
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        data_uri_encoded_input_data = data['input'].get(self.configuration_dict['input_id'], {})      
        print data_uri_encoded_input_data
        return data

    