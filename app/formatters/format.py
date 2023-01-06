def formatZincResultCSV(data):
    new_data = []
    print(data)
    for res in data:
        new_res = {}
        for key, value in res.items():
            if isinstance(value, list):
                for i in value:
                    count = 0
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