from data_service.database import get_mongo_collection


def demo():
    collection_name = 'weather'
    file_path = 'xx/xx.xx'
    # do something to load data from file
    dataframe = []  # for example
    # do something to convert to the records you want to store
    records = []
    # connection for mongodb
    pos_collection = get_mongo_collection(collection_name)
    # store
    _ = pos_collection.insert_many(records)


def test():
    # run script
    demo()
