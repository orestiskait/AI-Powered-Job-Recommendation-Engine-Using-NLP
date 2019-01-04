const store = {
  debug: true,
  state: {
    step: 'upload',
    features: {},
    states: []
  },
  apiUrl: 'https://kr13f55f6j.execute-api.us-east-1.amazonaws.com/prod', // AWS backend
  //apiUrl: 'http://127.0.0.1:5000', // Local backend
  setStep(step) {
    this.state.step = step;
  },
  setFeatures(features) {
    this.state.features = features;
  }
}

export default store
