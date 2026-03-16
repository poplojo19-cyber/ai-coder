/* calculator.js */

// Connect the buttons to the functions
const display = document.getElementById('display');
const clearBtn = document.getElementById('clear');
const addBtn = document.getElementById('add');
const subtractBtn = document.getElementById('subtract');
const multiplyBtn = document.getElementById('multiply');
const divideBtn = document.getElementById('divide');
const equalsBtn = document.getElementById('equals');

clearBtn.addEventListener('click', () => {
  display.value = '';
});

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
  const result = eval(expression);
  display.value = result;
});