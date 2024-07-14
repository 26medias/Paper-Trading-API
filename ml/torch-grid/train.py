from MarketCycleDataset import MarketCycleClassifier

classifier = MarketCycleClassifier(data_dir='../../data', model_dir='./model', model="grid-up-5")
classifier.run()
