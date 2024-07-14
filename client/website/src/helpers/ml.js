import * as tf from '@tensorflow/tfjs';

let models = {};

async function loadModel(name) {
    if (!models[name]) {
        models[name] = await tf.loadLayersModel(name);
    }
    return models[name];
}

const inferences = [{
    type: 'buy',
    name: "buy-2%",
    fn: async function(data) {
        const response = window.ml_buy20(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}, {
    type: 'buy',
    name: "buy-1%",
    fn: async function(data) {
        const response = window.ml_buy(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}, {
    type: 'buy',
    name: "buy-0.5%",
    fn: async function(data) {
        const response = window.ml_buy05(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}, {
    type: 'sell',
    name: "sell-0.5%",
    fn: async function(data) {
        const response = window.ml_sell05(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}, {
    type: 'sell',
    name: "sell-1%",
    fn: async function(data) {
        const response = window.ml_sell10(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}, {
    type: 'sell',
    name: "sell-2%",
    fn: async function(data) {
        const response = window.ml_sell20(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: response[1]
        }
    }
}/*, {
    name: "buy-05",
    fn: async function(data) {
        const model = await loadModel('/tfjs_model_buy-05/model.json');
        const inputTensor = tf.tensor2d([data], [1, 28]); // Ensure correct shape
        const prediction = model.predict(inputTensor);
        const predictionArray = await prediction.array(); // Wait for prediction to complete
        const probability = predictionArray[0][0]; // Assuming binary classification
        const isUp = probability > 0.5;
        return {
            value: isUp,
            probability: probability
        }
    }
}*/];

export const runML = async (data) => {
    let output = [];
    for (const item of inferences) {
        try {
            const value = await item.fn(data);
            output.push({
                type: item.type,
                name: item.name,
                value: value
            });
        } catch (e) {
            console.log(`${item.name}:`, "FAIL", e.message, data);
        }
    }
    return output;
};
