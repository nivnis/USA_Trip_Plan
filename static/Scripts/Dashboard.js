function createAccordion(result) {
  if(result.length == 0) {
    document.getElementById("tripsHeadline").innerText = "You have no saved trips"
    return
  }
  document.getElementById("tripsHeadline").innerText = "Saved trips:"
  let tripCount = 1
  const accordionContainer = document.getElementById("accordionContainer")
  let tripId = result[0].trip_id
  let panelExists = false
  let orderedList, listElement

  for (i=0; i < result.length; i++) {
    if (result[i].trip_id == tripId) {
      tripIdList.push(tripId)
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
    button.innerHTML = 'Trip' + count + '<span class="close">&times;</span>'
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
      if (panell == null) {
        return
      }
      if (panell.style.maxHeight) {
        panell.style.maxHeight = null;
      } else {
        panell.style.maxHeight = panell.scrollHeight + "px";
      }
    });
  }          
}

function closeInit() {
  let closebtns = document.getElementsByClassName("close");                                   
  for (i = 0; i < closebtns.length; i++) {
    closebtns[i].parentElement.id = tripIdList[i]
    closebtns[i].addEventListener("click", function() {     
      const tripId = this.parentElement.id
      this.parentElement.nextElementSibling.remove()
      this.parentElement.remove()
      $.ajax({
          type: "DELETE",
          contentType: 'application/json;charset=UTF-8',
          url: "http://127.0.0.1:5000/trips/"+ tripId,            
          success: function() {
              console.log("success!!! trip id " + tripId + " was deleted")                        
          },
          error: function() {
              // alert('error: unable to delete trip');
          }
      });
    });
  }
}              
