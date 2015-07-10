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
        WIPData=self.convertExcelToList(data_uri_encoded_input_data, "WIP")
        from pprint import pprint
        # pprint(WIPData)
        
        # get the number of units for a standard batch
        standardBatchUnits=0
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchSource':
                standardBatchUnits=int(node['batchNumberOfUnits']) 
            node['wip']=[]
        
        WIPData.pop(0)
        
        for row in WIPData:
            stationId=row[0]
            if not stationId:
                continue        
            workingBatchSize=nodes[stationId]['workingBatchSize']    
            assert stationId in nodes.keys(), "WIP spreadsheet has "+ stationId +" that does not exist in the graph"  
            buffered=row[1]
            notStarted=row[2]
            complete=row[3]
            inProgress=row[4]
            batchId=row[5]
            # check for buffered batches of sub-batches
            if buffered:
                # get the buffer id and also if there is decomposition after the buffer
                current=stationId
                decomposition=False
                while 1: 
                    previous=self.getPredecessors(data, current)[0]
                    if nodes[previous]['_class'] in ['Dream.Queue','Dream.LineClearance','Dream.RoutingQueue']:
                        bufferId=previous
                        break
                    if 'Decomposition' in nodes[previous]['_class']:
                        decomposition=True
                    current=previous
                # check if we have batches or sub-batches
                if decomposition or workingBatchSize==standardBatchUnits:
                    _class='Dream.Batch'
                else:
                    _class='Dream.SubBatch'
                # if we have batches
                if _class=='Dream.Batch':
                    numberOfBatches=int(buffered/standardBatchUnits)
                    for i in range(numberOfBatches):
                        partId=stationId+'_'+str(i)
                        wipDict={
                          "_class": _class,
                          "id": partId, 
                          "name": 'Batch_'+partId+'_wip',
                          "numberOfUnits":standardBatchUnits,
                          }
                        nodes[bufferId]['wip'].append(wipDict)
                elif _class=='Dream.SubBatch':
                    numberOfBatches=int(buffered/standardBatchUnits)
                    numberOfSubBatches=int(standardBatchUnits/workingBatchSize)
                    for i in range(numberOfBatches):
                        parentBatchId=stationId+'_'+str(i)
                        for j in range(numberOfSubBatches):
                            partId=stationId+'_'+parentBatchId+'_'+str(j)
                            wipDict={
                              "_class": _class,
                              "id": partId, 
                              "name": 'Batch_'+partId+'_wip',
                              "numberOfUnits":workingBatchSize,
                              "parentBatchId":parentBatchId,
                              "name":'Batch'+parentBatchId+'_SB'+partId+'wip'
                              } 
                            nodes[bufferId]['wip'].append(wipDict)
            # from now on for the WIP inside stations 
            totalUnits=notStarted+complete+inProgress               
            assert (totalUnits==standardBatchUnits or totalUnits==0 or batchId), "not full batch defined in "+stationId
            
            for node_id, node in nodes.iteritems():
                pass
                #print node_id,len(node['wip'])
        return data

    