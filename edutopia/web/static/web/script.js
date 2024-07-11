const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

const model = document.querySelector('.add-subject');
function openSubject() {
  model.classList.remove('d-none');
  model.classList.add('d-flex');
}
function closeSubject() {
  model.classList.remove('d-flex');
  model.classList.add('d-none');
}

