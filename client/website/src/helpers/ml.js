const inferences = [{
    name: "buy",
    fn: function(data) {
        const response = window.ml_buy(data);
        const isUp = response[1] > 0.5;
        return {
            value: isUp,
            probability: isUp ? response[1] : response[0]
        }
    }
},{
    name: "down",
    fn: function(data) {
        const response = window.ml_down(data);
        return {
            value: response,
            probability: response
        }
    }
}]
export const runML = (data) => {
    let output = {};
    inferences.forEach(item => {
        console.log(`Infering ${item.name}...`)
        output[item.name] = item.fn(data);
        console.log(`${item.name}:`, output[item.name])
    })
    return output;
}