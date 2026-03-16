// Get elements
const taskInput = document.getElementById('taskInput');
const addTaskBtn = document.getElementById('addTaskBtn');
const taskList = document.getElementById('taskList');

// Initialize tasks array
let tasks = [];

// Load tasks from LocalStorage
if (localStorage.getItem('tasks')) {
  tasks = JSON.parse(localStorage.getItem('tasks'));
  renderTasks();
}

// Add event listener to add task button
addTaskBtn.addEventListener('click', addTask);

// Function to add task
function addTask() {
  const task = taskInput.value.trim();
  if (task) {
    tasks.push(task);
    localStorage.setItem('tasks', JSON.stringify(tasks));
    renderTasks();
    taskInput.value = '';
  }
}

// Function to render tasks
function renderTasks() {
  taskList.innerHTML = '';
  tasks.forEach((task, index) => {
    const taskCard = document.createElement('div');
    taskCard.classList.add('task-card', 'mb-4');
    taskCard.innerHTML = `
      <p>${task}</p>
      <button class="delete-btn" data-index="${index}">Delete</button>
    `;
    taskList.appendChild(taskCard);
  });

  // Add event listener to delete buttons
  const deleteBtns = document.querySelectorAll('.delete-btn');
  deleteBtns.forEach((btn) => {
    btn.addEventListener('click', deleteTask);
  });
}

// Function to delete task
function deleteTask(event) {
  const index = event.target.dataset.index;
  tasks.splice(index, 1);
  localStorage.setItem('tasks', JSON.stringify(tasks));
  renderTasks();
}