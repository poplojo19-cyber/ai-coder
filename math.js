// math.js

// Function to add two numbers
function add(a, b) {
  return a + b;
}

// Function to subtract two numbers
function subtract(a, b) {
  return a - b;
}

function multiply(a, b) {
  return a * b;
}
// Function to add two numbers
function add(a, b) {
  return a + b;
}

// Function to subtract two numbers
function subtract(a, b) {
  return a - b;
}

function multiply(a, b) {
  return a * b;
}

// Function to divide two numbers
function divide(a, b) {
  return a / b;
}

// Function to calculate the result of an expression
function calculate(expression) {
  return eval(expression);
}

// Connect the buttons to the functions
const display = document.getElementById('display');
const addBtn = document.getElementById('add');
const subtractBtn = document.getElementById('subtract');
const multiplyBtn = document.getElementById('multiply');
const divideBtn = document.getElementById('divide');
const equalsBtn = document.getElementById('equals');

addBtn.addEventListener('click', () => {
  display.value += '+';
});

subtractBtn.addEventListener('click', () => {
  display.value += '-';
});

multiplyBtn.addEventListener('click', () => {
  display.value += '*';
});

divideBtn.addEventListener('click', () => {
  display.value += '/';
});

equalsBtn.addEventListener('click', () => {
  const expression = display.value;
  const result = calculate(expression);
  display.value = result;
});