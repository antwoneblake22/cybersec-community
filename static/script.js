async function loadMessages(){

let response = await fetch("/messages")

let data = await response.json()

let chat = document.getElementById("chat")

chat.innerHTML=""

data.messages.reverse().forEach(m=>{

chat.innerHTML += `<div class="message"><b>${m.user}</b>: ${m.msg}</div>`

})

}

setInterval(loadMessages,2000)

loadMessages()