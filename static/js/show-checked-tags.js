// Получаем все чекбоксы с именем "tags-in"
let tagsInCheckboxes = document.querySelectorAll("input[name='tags_in']");
let tagsOffCheckboxes = document.querySelectorAll("input[name='tags_off']");

// Получаем элемент, в котором будем отображать перечень нажатых чекбоксов
let tagsInOutput = document.getElementById("tags-in-output");
let tagsOffOutput = document.getElementById("tags-off-output");

function showTags () {
    // Создаем пустой массив для хранения нажатых чекбоксов
    tagsInOutput.innerHTML = ""
    // Перебираем все чекбоксы и добавляем в массив те, которые нажаты
    for (let checkbox of tagsInCheckboxes) {
      if (checkbox.checked) {
        // Создаем новый элемент div
        let div = document.createElement("div");
        div.classList.add("me-1", "badge", "bg-success")
        div.textContent = checkbox.value
        tagsInOutput.appendChild(div)
      }
    }

    tagsOffOutput.innerHTML = ""
    for (let checkbox of tagsOffCheckboxes) {
      if (checkbox.checked) {
        // Создаем новый элемент div
        let div = document.createElement("div");
        div.classList.add("me-1", "badge", "bg-danger")
        div.textContent = checkbox.value
        tagsOffOutput.appendChild(div)
      }
    }

  }

// Добавляем обработчик события "change" для каждого чекбокса
for (let checkbox of tagsInCheckboxes) {
  checkbox.addEventListener("change", showTags);
}
for (let checkbox of tagsOffCheckboxes) {
  checkbox.addEventListener("change", showTags);
}
window.addEventListener("load", showTags)