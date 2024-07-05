from MarketCycleClassifier import MarketCycleClassifier

classifier = MarketCycleClassifier(data_dir='../../data', model_dir='./model', model="down")
classifier.run()