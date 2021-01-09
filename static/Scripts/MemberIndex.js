document.getElementById("logout").addEventListener("click", function() {
    loggedIn = false
    window.location.replace("../Index.html");
  });

function createAccordion(result) {
  if(result.length == 0) {
    document.getElementById("tripsHeadline").innerText = "There are no popular trip plans from " + localStorage.getItem("state") + " yet"
    return
  }
  let tripCount = 1
  const accordionContainer = document.getElementById("accordionContainer")
  let tripId = result[0].trip_id
  let panelExists = false
  let orderedList, listElement

  for (i=0; i < result.length; i++) {
    if (result[i].trip_id == tripId) {
      if (!panelExists) {
        orderedList = createPanel(tripCount)
        panelExists = true
      }                
      appendList(orderedList, result[i].name, result[i].state)              
    }
    else {
      orderedList.lastElementChild.innerText = orderedList.lastElementChild.innerText.slice(0, -3)
      tripCount++
      tripId = result[i].trip_id
      orderedList = createPanel(tripCount)
      appendList(orderedList, result[i].name, result[i].state)
    }              
  } 
  orderedList.lastElementChild.innerText = orderedList.lastElementChild.innerText.slice(0, -3)                
}

function createPanel(count) {
    let button = document.createElement("BUTTON");
    button.innerHTML = 'Trip' + count
    button.className = "accordion"
    let panel = document.createElement("DIV");
    panel.className = "panel"
    let orderedList = document.createElement("OL");
    accordionContainer.appendChild(button)
    accordionContainer.appendChild(panel)
    panel.appendChild(orderedList)
    return orderedList                       
  }

function appendList(orderedList, name, state) {
  let li = document.createElement("LI");
  li.innerText = name + ', ' + state + " ->"
  orderedList.appendChild(li)
}

function designAccordion() {
  const acc = document.getElementsByClassName("accordion");
  for (i = 0; i < acc.length; i++) {
    if (acc[i] == undefined)
      continue
      
    acc[i].addEventListener("click", function() {
      this.classList.toggle("active");
      let panell = this.nextElementSibling;
      console.log(panell)
      if (panell.style.maxHeight) {
        panell.style.maxHeight = null;
      } else {
        panell.style.maxHeight = panell.scrollHeight + "px";
      }
    });
  }          
}
