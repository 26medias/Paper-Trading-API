import joblib
import m2cgen as m2c
import sys

model = "up"

# Increase recursion limit for complex models
sys.setrecursionlimit(10000)

# Load the trained model
model = joblib.load(f'./model/mc_{model}.joblib')

# Generate JavaScript code
js_code = m2c.export_to_javascript(model)

# Save the model to a JS file
with open(f'./model/mc_{model}.js', 'w') as f:
    f.write(js_code)
with open(f'../../client/website/public/mc_{model}.js', 'w') as f:
    f.write(js_code)
print("Model exported to client-side JS")