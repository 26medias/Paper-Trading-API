from MarketCycleClassifier import MarketCycleClassifierTF

classifier = MarketCycleClassifierTF(data_dir='../../data', model_dir='./model', model="buy-05")
classifier.run()