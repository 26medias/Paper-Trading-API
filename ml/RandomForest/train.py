from MarketCycleClassifier import MarketCycleClassifier

classifier = MarketCycleClassifier(data_dir='../../data', model_dir='./model', model="sell-20")
classifier.run()