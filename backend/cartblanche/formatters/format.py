from pandas import DataFrame
import json 

def formatZincResult(data, format):

    if format == "csv":
        results = formatZincResultCSV(data)
        res = DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False, sep=",", line_terminator='\n')
    if format == "txt":
        results = formatZincResultCSV(data)
        res = DataFrame(results)
        return res.to_csv(encoding='utf-8', index=False, sep=" ", line_terminator='\n')
    if format == "json":
        return json.dumps(data)
    
def formatZincResultCSV(data):
    new_data = []
 
    for res in data:
        new_res = {}
        for key, value in res.items():
            count = 0
            if isinstance(value, list):
                for i in value:
                    if isinstance(i, dict):
                        for k, v in i.items():
                            new_res[key + "_" + str(count) + "_" + k] = v    
                    else:
                        new_res[key + "_" + str(count)] = i
                    count +=1                
            elif isinstance(value, dict):
                for k, v in value.items():
                    new_res[key + "_" + k] = v
            else:
                new_res[key] = value
        new_data.append(new_res)
    return new_data