// Example only. Every number here is invented.
// The real file is written to ../console/model.js by the training script.
window.FLAME_MODEL = {
  meta: { mock: false, source: "NASA PSI FLEX", rows: 0 },
  fuels: [
    { key: "heptane", label: "Heptane" },
    { key: "methanol", label: "Methanol" }
  ],
  features: [
    { key: "o2",  label: "Oxygen",           unit: "%",   min: 10,   max: 40,  step: 0.5,  digits: 1, default: 21,  data_min: 14,  data_max: 30 },
    { key: "p",   label: "Pressure",         unit: "atm", min: 0.25, max: 3.5, step: 0.05, digits: 2, default: 1.0, data_min: 0.5, data_max: 3.0 },
    { key: "co2", label: "Carbon dioxide",   unit: "%",   min: 0,    max: 40,  step: 1,    digits: 0, default: 0,   data_min: 0,   data_max: 30 },
    { key: "d0",  label: "Droplet diameter", unit: "mm",  min: 1.0,  max: 6.0, step: 0.1,  digits: 1, default: 3.0, data_min: 1.5, data_max: 5.0 }
  ],
  extinction: { intercept: 5.5,  fuel: { heptane: 0, methanol: 0.4 },   coef: { o2: -0.28, p: -0.5, co2: 0.08,   d0: 0.3 } },
  burn_rate:  { intercept: 0.30, fuel: { heptane: 0, methanol: -0.08 }, coef: { o2: 0.012, p: 0.03, co2: -0.004, d0: 0.02 } }
};
